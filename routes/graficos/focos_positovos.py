from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required # Mantenha se for usar autenticação
from .bluprint import graficos
import logging

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/focos_positivos/<int:ano>/<int:ciclo>', methods=['GET'])
def get_focos_positivos(ano, ciclo):
    """
    Endpoint para obter dados históricos de focos positivos para um gráfico.

    Esta rota busca todos os dados de focos positivos desde o início até o ano e ciclo especificados.
    Ela retorna uma lista de pontos de dados para o gráfico e um resumo comparando
    o ciclo atual com o anterior.
    """
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # Query SQL otimizada para buscar todos os dados históricos de uma vez
        # Utiliza LEFT JOIN para garantir que ciclos com 0 focos também sejam incluídos
        query_grafico = """
            SELECT
                EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER AS ano,
                c.ciclo,
                COUNT(rc.registro_de_campo_id) AS focos_positivos
            FROM
                ciclos c
            LEFT JOIN
                registro_de_campo rc ON c.ciclo_id = rc.ciclo_id AND (rc.t = True OR rc.li = True OR rc.df = True)
            WHERE
                EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER < %s OR
                (EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER = %s AND c.ciclo <= %s)
            GROUP BY
                c.ciclo_id, ano, c.ciclo
            ORDER BY
                ano, c.ciclo;
        """
        cursor.execute(query_grafico, (ano, ano, ciclo))
        dados_grafico = cursor.fetchall()

        # Se não houver dados, retorna uma estrutura vazia
        if not dados_grafico:
            return jsonify({
                "dados_grafico": [],
                "resumo_ciclo_atual": {
                    "focos_positivos": 0,
                    "dados_do_ultimo_ciclo": 0,
                    "porcentagem": "0%",
                    "crescimento": "estável"
                }
            }), 200

        # Lógica para calcular o resumo com base nos dois últimos ciclos da lista retornada
        focos_positivos_atual = 0
        focos_positivos_anterior = 0

        # O último item da lista ordenada é o ciclo atual
        if len(dados_grafico) > 0:
            focos_positivos_atual = int(dados_grafico[-1]['focos_positivos'])

        # O penúltimo item é o ciclo anterior
        if len(dados_grafico) > 1:
            focos_positivos_anterior = int(dados_grafico[-2]['focos_positivos'])
        
        # Reutilização da lógica original para cálculo de porcentagem
        porcentagem_str = "0%"
        crescimento_str = "estável"

        if focos_positivos_anterior == 0:
            if focos_positivos_atual > 0:
                porcentagem_str = "100% (Novo) ↑"
                crescimento_str = "aumentou"
        elif focos_positivos_anterior > 0:
            if focos_positivos_atual > focos_positivos_anterior:
                percentage = round(((focos_positivos_atual / focos_positivos_anterior) - 1) * 100, 2)
                porcentagem_str = f"{percentage}% ↑"
                crescimento_str = "aumentou"
            elif focos_positivos_atual < focos_positivos_anterior:
                percentage = round((1 - (focos_positivos_atual / focos_positivos_anterior)) * 100, 2)
                porcentagem_str = f"{percentage}% ↓"
                crescimento_str = "diminuiu"

        # Monta o objeto de resumo
        resumo = {
            "focos_positivos": focos_positivos_atual,
            "dados_do_ultimo_ciclo": focos_positivos_anterior,
            "porcentagem": porcentagem_str,
            "crescimento": crescimento_str
        }
        
        # Retorna a resposta final com os dados para o gráfico e o resumo
        return jsonify({
            "dados_grafico": dados_grafico,
            "resumo_ciclo_atual": resumo
        }), 200

    except Exception as e:
        logging.error(f"Falha na consulta ao banco de dados: {e}")
        # conn.rollback() # Desnecessário para consultas SELECT, mas não prejudica
        return jsonify({"error": "Falha na consulta ao banco de dados", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()