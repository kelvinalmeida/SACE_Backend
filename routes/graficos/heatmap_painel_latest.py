# routes/graficos/heatmap_painel_latest.py

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
    
@graficos.route('/dashboard_summary/latest', methods=['GET'])
def get_latest_dashboard_summary():
    """
    Endpoint para obter um resumo de dados para o dashboard do CICLO MAIS RECENTE.
    Utiliza 'doentes_confirmados' para contagem de casos.
    """
    conn = None
    cursor = None
    summary_data = {
        "depositos": {"a1": 0, "a2": 0, "b": 0, "c": 0, "d1": 0, "d2": 0, "e": 0},
        "casos_confirmados": {"dengue": 0, "zika": 0, "chikungunya": 0},
        "areas_risco": {"Preta": 0, "Vermelha": 0, "Laranja": 0, "Amarela": 0}
    }

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

        # --- 2. ATUALIZAÇÃO: Query de Depósitos (Somente de registro_de_campo) ---
        deposits_query = """
            SELECT
                COALESCE(SUM(d.a1), 0) AS total_a1, COALESCE(SUM(d.a2), 0) AS total_a2,
                COALESCE(SUM(d.b), 0) AS total_b, COALESCE(SUM(d.c), 0) AS total_c,
                COALESCE(SUM(d.d1), 0) AS total_d1, COALESCE(SUM(d.d2), 0) AS total_d2,
                COALESCE(SUM(d.e), 0) AS total_e
            FROM registro_de_campo rc
            LEFT JOIN depositos d ON rc.deposito_id = d.deposito_id
            WHERE rc.ciclo_id = %s;
        """
        cursor.execute(deposits_query, (ciclo_id,))
        deposits_result = cursor.fetchone()

        if deposits_result:
             summary_data["depositos"]["a1"] = int(deposits_result["total_a1"])
             summary_data["depositos"]["a2"] = int(deposits_result["total_a2"])
             summary_data["depositos"]["b"] = int(deposits_result["total_b"])
             summary_data["depositos"]["c"] = int(deposits_result["total_c"])
             summary_data["depositos"]["d1"] = int(deposits_result["total_d1"])
             summary_data["depositos"]["d2"] = int(deposits_result["total_d2"])
             summary_data["depositos"]["e"] = int(deposits_result["total_e"])

        # --- 3. ATUALIZAÇÃO: Query de Casos Confirmados (Somente de doentes_confirmados) ---
        cases_query = """
            SELECT
                SUM(CASE WHEN tipo_da_doenca ILIKE 'Dengue' THEN 1 ELSE 0 END) AS casos_dengue,
                SUM(CASE WHEN tipo_da_doenca ILIKE 'Zica' THEN 1 ELSE 0 END) AS casos_zika,
                SUM(CASE WHEN tipo_da_doenca ILIKE 'Chikungunya' THEN 1 ELSE 0 END) AS casos_chikungunya
            FROM doentes_confirmados
            WHERE ciclo_id = %s;
        """
        cursor.execute(cases_query, (ciclo_id,))
        cases_result = cursor.fetchone()

        if cases_result:
             summary_data["casos_confirmados"]["dengue"] = int(cases_result["casos_dengue"] or 0)
             summary_data["casos_confirmados"]["zika"] = int(cases_result["casos_zika"] or 0)
             summary_data["casos_confirmados"]["chikungunya"] = int(cases_result["casos_chikungunya"] or 0)


        # --- 4. ATUALIZAÇÃO: Query de Nível de Risco (Usando CTEs) ---
        risk_level_query = """
            WITH FocosPorArea AS (
                -- CTE 1: Agrega focos (de registro_de_campo) por ponto geográfico
                SELECT
                    av.latitude, av.longitude, av.bairro,
                    COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0) AS focos_encontrados_agg
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
                    COUNT(doente_confirmado_id) AS total_casos_confirmados_agg
                FROM doentes_confirmados
                WHERE ciclo_id = %s AND bairro IS NOT NULL
                GROUP BY bairro
            )
            -- Junção final: Junta focos (ponto geográfico) com casos (por bairro)
            SELECT
                f.latitude, f.longitude, f.bairro,
                f.focos_encontrados_agg,
                COALESCE(c.total_casos_confirmados_agg, 0) AS total_casos_confirmados_agg
            FROM FocosPorArea f
            LEFT JOIN CasosPorBairro c ON f.bairro = c.bairro;
        """
        # Passa o ciclo_id duas vezes (uma para cada CTE)
        cursor.execute(risk_level_query, (ciclo_id, ciclo_id))
        area_results = cursor.fetchall()

        # --- 5. Calcular e Contar os Níveis de Risco ---
        risk_counts = Counter()
        for area_agg in area_results:
            casos = int(area_agg['total_casos_confirmados_agg'])
            focos = int(area_agg['focos_encontrados_agg'])
            level = calculate_risk_level(casos, focos)
            if level != "Normal":
                 risk_counts[level] += 1

        summary_data["areas_risco"]["Preta"] = risk_counts.get("Preta", 0)
        summary_data["areas_risco"]["Vermelha"] = risk_counts.get("Vermelha", 0)
        summary_data["areas_risco"]["Laranja"] = risk_counts.get("Laranja", 0)
        summary_data["areas_risco"]["Amarela"] = risk_counts.get("Amarela", 0)

        logging.info(f"Resumo do dashboard (latest) gerado para Ciclo ID {ciclo_id}.")

        return jsonify(summary_data), 200

    except Exception as e:
        logging.error(f"Erro ao gerar resumo do dashboard (latest): {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()