# routes/graficos/heatmap_data_latest.py

from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required
from .bluprint import graficos
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO)

def calculate_risk_level(casos, focos):
    """
    Define o nível de risco (cor) baseado no número de casos e focos.
    *** AJUSTE ESTA LÓGICA CONFORME OS SEUS CRITÉRIOS REAIS ***
    """
    if casos >= 5 and focos >= 10:
        return "Preta"
    elif casos >= 3 and focos >= 5:
        return "Vermelha"
    elif casos >= 1 or focos >= 3:
        return "Laranja"
    elif focos >= 1:
        return "Amarela"
    else:
        return "Normal"

@graficos.route('/heatmap_data/latest', methods=['GET'])
def get_latest_heatmap_data():
    """
    Endpoint para obter dados agregados por área de visita para um mapa de calor
    para o CICLO MAIS RECENTE.
    Utiliza 'doentes_confirmados' para contagem de casos.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            logging.error("Falha na conexão com o banco de dados")
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

        cursor = conn.cursor()

        # --- 1. Encontrar o ciclo_id MAIS RECENTE ---
        find_latest_ciclo_id_query = """
            SELECT ciclo_id, EXTRACT(YEAR FROM ano_de_criacao)::INTEGER AS ano, ciclo
            FROM ciclos
            ORDER BY ano_de_criacao DESC, ciclo DESC
            LIMIT 1;
        """
        cursor.execute(find_latest_ciclo_id_query)
        latest_ciclo_result = cursor.fetchone()

        if not latest_ciclo_result:
            logging.warning("Nenhum ciclo encontrado no banco de dados.")
            return jsonify({"error": "Nenhum ciclo encontrado no sistema."}), 404

        ciclo_id = latest_ciclo_result['ciclo_id']
        logging.info(f"Ciclo ID mais recente encontrado: {ciclo_id}")

        # --- 2. ATUALIZAÇÃO DA QUERY: Usando CTEs para buscar focos e casos separadamente ---
        # A contagem de casos agora vem de 'doentes_confirmados'
        heatmap_query = """
            WITH FocosPorArea AS (
                -- CTE 1: Agrega focos (de registro_de_campo) por ponto geográfico
                SELECT
                    av.latitude, av.longitude, av.bairro,
                    COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0) AS focos_encontrados
                FROM area_de_visita av
                LEFT JOIN registro_de_campo rc ON av.area_de_visita_id = rc.area_de_visita_id AND rc.ciclo_id = %s
                LEFT JOIN depositos d ON rc.deposito_id = d.deposito_id
                WHERE av.latitude IS NOT NULL AND av.longitude IS NOT NULL
                GROUP BY av.latitude, av.longitude, av.bairro
            ),
            CasosPorBairro AS (
                -- CTE 2: Agrega casos (de doentes_confirmados) por bairro
                SELECT
                    bairro,
                    SUM(CASE WHEN tipo_da_doenca ILIKE 'Dengue' THEN 1 ELSE 0 END) AS casos_dengue,
                    SUM(CASE WHEN tipo_da_doenca ILIKE 'Zica' THEN 1 ELSE 0 END) AS casos_zika,
                    SUM(CASE WHEN tipo_da_doenca ILIKE 'Chikungunya' THEN 1 ELSE 0 END) AS casos_chikungunya,
                    COUNT(doente_confirmado_id) AS total_casos_confirmados
                FROM doentes_confirmados
                WHERE ciclo_id = %s AND bairro IS NOT NULL
                GROUP BY bairro
            )
            -- Junção final: Junta focos (ponto geográfico) com casos (por bairro)
            SELECT
                f.latitude,
                f.longitude,
                f.bairro,
                f.focos_encontrados,
                COALESCE(c.casos_dengue, 0) AS casos_dengue,
                COALESCE(c.casos_zika, 0) AS casos_zika,
                COALESCE(c.casos_chikungunya, 0) AS casos_chikungunya,
                COALESCE(c.total_casos_confirmados, 0) AS total_casos_confirmados
            FROM FocosPorArea f
            LEFT JOIN CasosPorBairro c ON f.bairro = c.bairro
            ORDER BY f.bairro;
        """
        # Passa o ciclo_id duas vezes (uma para cada CTE)
        cursor.execute(heatmap_query, (ciclo_id, ciclo_id))
        results = cursor.fetchall()

        logging.info(f"Consulta para heatmap (latest) retornou {len(results)} pontos/bairros agregados.")

        # --- 3. Processa os resultados para adicionar o nível de risco ---
        processed_results = []
        for row in results:
            casos_total = int(row['total_casos_confirmados'])
            focos = int(row['focos_encontrados'])
            casos_dengue = int(row['casos_dengue'])
            casos_zika = int(row['casos_zika'])
            casos_chikungunya = int(row['casos_chikungunya'])
            nivel_risco = calculate_risk_level(casos_total, focos)

            processed_row = {
                "latitude": row['latitude'], "longitude": row['longitude'],
                "bairro": row['bairro'], "focos_encontrados": focos,
                "total_casos_confirmados": casos_total,
                "casos_dengue": casos_dengue, "casos_zika": casos_zika,
                "casos_chikungunya": casos_chikungunya,
                "nivel_risco": nivel_risco
            }
            processed_results.append(processed_row)
            
        response_data = {
             "ciclo_info": {
                 "ano": latest_ciclo_result['ano'], 
                 "ciclo": latest_ciclo_result['ciclo'], 
                 "id": ciclo_id
             },
             "heatmap_points": processed_results
         }

        # Retorna só a lista (ou response_data se preferir incluir o ciclo_info)
        return jsonify(processed_results), 200

    except Exception as e:
        logging.error(f"Erro ao buscar dados para heatmap (latest): {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()