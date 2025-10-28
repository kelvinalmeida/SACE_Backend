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

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

# --- Função para calcular o nível de risco ---
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
# --- Fim da Função ---

# Descomente o decorator se precisar de autenticação
# @token_required
# def get_heatmap_data(current_user, ano, ciclo):
@graficos.route('/heatmap_data/<int:ano>/<int:ciclo>', methods=['GET'])
def get_heatmap_data(ano, ciclo):
    """
    Endpoint para obter dados agregados por área de visita para um mapa de calor.

    Retorna latitude, longitude, contagem total de focos, contagem total e
    específica (Dengue, Zika, Chikungunya) de casos confirmados, e o nível
    de risco (cor) para cada ponto geográfico dentro de um ciclo específico.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            logging.error("Falha na conexão com o banco de dados")
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

        cursor = conn.cursor()

        # --- 1. Encontrar o ciclo_id ---
        find_ciclo_id_query = """
            SELECT ciclo_id
            FROM ciclos
            WHERE EXTRACT(YEAR FROM ano_de_criacao)::INTEGER = %s AND ciclo = %s
            LIMIT 1;
        """
        cursor.execute(find_ciclo_id_query, (ano, ciclo))
        ciclo_result = cursor.fetchone()

        if not ciclo_result:
            logging.warning(f"Ciclo não encontrado para ano {ano}, ciclo {ciclo}")
            return jsonify({"error": f"Ciclo {ciclo} do ano {ano} não encontrado."}), 404

        ciclo_id = ciclo_result['ciclo_id']
        logging.info(f"Ciclo ID encontrado: {ciclo_id} para Ano: {ano}, Ciclo: {ciclo}")

        # --- 2. Query principal para agregar dados por COORDENADAS E BAIRRO ---
        # <<< MODIFICADA PARA REINCLUIR CONTAGENS ESPECÍFICAS DE CASOS >>>
        heatmap_query = """
            SELECT
                av.latitude,
                av.longitude,
                av.bairro,
                -- Contagem de casos confirmados por tipo (usando formulario_tipo)
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Dengue' THEN 1 ELSE 0 END) AS casos_dengue,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Zica' THEN 1 ELSE 0 END) AS casos_zika,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Chikungunya' THEN 1 ELSE 0 END) AS casos_chikungunya,
                -- Soma total de depósitos (focos encontrados)
                COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0) AS focos_encontrados,
                -- Contagem total de casos confirmados na área (independente do tipo)
                SUM(CASE WHEN rc.caso_comfirmado = TRUE THEN 1 ELSE 0 END) AS total_casos_confirmados
            FROM
                area_de_visita av
            LEFT JOIN
                registro_de_campo rc ON av.area_de_visita_id = rc.area_de_visita_id
                                   AND rc.ciclo_id = %s -- Filtro do ciclo no JOIN
            LEFT JOIN
                depositos d ON rc.deposito_id = d.deposito_id
            WHERE
                av.latitude IS NOT NULL AND av.longitude IS NOT NULL -- Apenas áreas com coordenadas
            GROUP BY
                av.latitude,
                av.longitude,
                av.bairro
            ORDER BY
                av.bairro;
        """
        cursor.execute(heatmap_query, (ciclo_id,))
        results = cursor.fetchall() # Resultados do banco de dados

        logging.info(f"Consulta para heatmap retornou {len(results)} pontos/bairros agregados.")

        # --- 3. Processa os resultados para adicionar o nível de risco ---
        processed_results = []
        for row in results:
            casos_total = int(row['total_casos_confirmados'])
            focos = int(row['focos_encontrados'])
            casos_dengue = int(row['casos_dengue']) # <<< ADICIONADO >>>
            casos_zika = int(row['casos_zika'])     # <<< ADICIONADO >>>
            casos_chikungunya = int(row['casos_chikungunya']) # <<< ADICIONADO >>>

            # Calcula o nível de risco usando a função
            nivel_risco = calculate_risk_level(casos_total, focos)

            # Cria um novo dicionário com todos os dados + nível de risco
            processed_row = {
                "latitude": row['latitude'],
                "longitude": row['longitude'],
                "bairro": row['bairro'],
                "focos_encontrados": focos,
                "total_casos_confirmados": casos_total,
                "casos_dengue": casos_dengue,         # <<< ADICIONADO >>>
                "casos_zika": casos_zika,             # <<< ADICIONADO >>>
                "casos_chikungunya": casos_chikungunya, # <<< ADICIONADO >>>
                "nivel_risco": nivel_risco
            }
            processed_results.append(processed_row)

        return jsonify(processed_results), 200 # Retorna a lista processada

    except Exception as e:
        logging.error(f"Erro ao buscar dados para heatmap: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()