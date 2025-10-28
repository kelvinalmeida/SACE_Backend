# ⚠️ Ponto Importante sobre as Cores (Níveis de Risco):

# Sua base de dados atual não armazena diretamente o nível de risco (Preta, Vermelha, Laranja, Amarela) para cada area_de_visita. Para calcular isso, precisamos definir os critérios.

#     Como exemplo, vou usar a seguinte lógica hipotética baseada nas contagens por area_de_visita dentro do ciclo:

#         Preta (Emergência): >= 5 casos confirmados E >= 10 focos encontrados

#         Vermelha (Perigo): >= 3 casos confirmados E >= 5 focos encontrados

#         Laranja (Alerta): >= 1 caso confirmado OU >= 3 focos encontrados

#         Amarela (Atenção): >= 1 foco encontrado (e não se encaixa nas anteriores)

#         (Implícito) Normal/Sem Risco: 0 casos e 0 focos


from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required # Descomente se precisar de autenticação
from .bluprint import graficos
import logging
from collections import Counter # Usaremos Counter para contar as cores

# Configuração básica de log
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
        return "Normal" # Ou None, se não quiser contar áreas sem risco
    

# ... (importações, função calculate_risk_level, rota get_heatmap_data) ...

# --- NOVA ROTA PARA O CICLO MAIS RECENTE ---
# Descomente o decorator se precisar de autenticação
# @token_required
# def get_latest_heatmap_data(current_user):
@graficos.route('/heatmap_data/latest', methods=['GET'])
def get_latest_heatmap_data():
    """
    Endpoint para obter dados agregados por área de visita para um mapa de calor
    para o CICLO MAIS RECENTE.
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

        # --- 2. Query principal para agregar dados por COORDENADAS E BAIRRO ---
        # (A query é a mesma da rota anterior, só muda o parâmetro ciclo_id)
        heatmap_query = """
            SELECT
                av.latitude, av.longitude, av.bairro,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Dengue' THEN 1 ELSE 0 END) AS casos_dengue,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Zica' THEN 1 ELSE 0 END) AS casos_zika,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Chikungunya' THEN 1 ELSE 0 END) AS casos_chikungunya,
                COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0) AS focos_encontrados,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE THEN 1 ELSE 0 END) AS total_casos_confirmados
            FROM area_de_visita av
            LEFT JOIN registro_de_campo rc ON av.area_de_visita_id = rc.area_de_visita_id AND rc.ciclo_id = %s
            LEFT JOIN depositos d ON rc.deposito_id = d.deposito_id
            WHERE av.latitude IS NOT NULL AND av.longitude IS NOT NULL
            GROUP BY av.latitude, av.longitude, av.bairro
            ORDER BY av.bairro;
        """
        cursor.execute(heatmap_query, (ciclo_id,))
        results = cursor.fetchall()

        logging.info(f"Consulta para heatmap (latest) retornou {len(results)} pontos/bairros agregados.")

        # --- 3. Processa os resultados para adicionar o nível de risco ---
        # (A lógica é a mesma da rota anterior)
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
            
        # Adiciona informação sobre qual ciclo foi usado na resposta (opcional, mas útil)
        response_data = {
             "ciclo_info": {
                 "ano": latest_ciclo_result['ano'], 
                 "ciclo": latest_ciclo_result['ciclo'], 
                 "id": ciclo_id
             },
             "heatmap_points": processed_results
         }

        return jsonify(processed_results), 200 # Retorna só a lista
        # return jsonify(response_data), 200 # Retorna a lista dentro de um objeto com info do ciclo


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