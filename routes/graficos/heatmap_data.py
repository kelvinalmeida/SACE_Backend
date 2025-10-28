from flask import jsonify, current_app
from db import create_connection
# Se precisar de autenticação, descomente a linha abaixo
# from routes.login.token_required import token_required
from .bluprint import graficos # Importa o blueprint 'graficos'
import logging

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

# Se precisar de autenticação, descomente o decorator abaixo
# @token_required
# def get_heatmap_data(current_user, ano, ciclo):
@graficos.route('/heatmap_data/<int:ano>/<int:ciclo>', methods=['GET'])
def get_heatmap_data(ano, ciclo):
    """
    Endpoint para obter dados agregados por área de visita para um mapa de calor.

    Retorna latitude, longitude, contagem total de focos (depósitos), e contagem
    específica de casos confirmados de Dengue, Zika e Chikungunya para cada
    área de visita dentro de um ciclo específico.
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
        
        # return jsonify(ciclo_result)


        # --- 2. Query principal para agregar dados por COORDENADAS E BAIRRO ---
        heatmap_query = """
            SELECT
                -- Removido av.area_de_visita_id da seleção principal
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
                -- Alterado o GROUP BY para agrupar por coordenadas e bairro
                av.latitude,
                av.longitude,
                av.bairro
            ORDER BY
                av.bairro; -- Mantém a ordenação por bairro
        """
        cursor.execute(heatmap_query, (ciclo_id,))
        results = cursor.fetchall()

        logging.info(f"Consulta para heatmap retornou {len(results)} pontos/bairros agregados.")

        # Converte os resultados para inteiros onde aplicável
        for row in results:
             row['casos_dengue'] = int(row['casos_dengue'])
             row['casos_zika'] = int(row['casos_zika'])
             row['casos_chikungunya'] = int(row['casos_chikungunya'])
             row['focos_encontrados'] = int(row['focos_encontrados'])
             row['total_casos_confirmados'] = int(row['total_casos_confirmados'])


        return jsonify(results), 200

    except Exception as e:
        logging.error(f"Erro ao buscar dados para heatmap: {e}", exc_info=True)
        # Se houver erro, tenta fazer rollback (embora seja um SELECT, é boa prática)
        if conn:
            conn.rollback()
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação.", "details": str(e)}), 500

    finally:
        # Garante que cursor e conexão sejam fechados
        if cursor:
            cursor.close()
        if conn:
            conn.close()