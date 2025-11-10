from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required # Mantenha se for usar autenticação
from .bluprint import graficos
import logging

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/casos_confirmados/<int:ano>/<int:ciclo>', methods=['GET'])
def get_casos_confirmados(ano, ciclo):
    """
    Endpoint para obter dados históricos de casos confirmados (da tabela doentes_confirmados)
    para um gráfico.

    Esta rota busca todos os dados de casos confirmados desde o início até o ano e ciclo especificados.
    Ela retorna uma lista de pontos de dados para o gráfico e um resumo comparando
    o ciclo atual com o anterior.
    """
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # --- ATUALIZAÇÃO DA QUERY ---
        # Agora faz LEFT JOIN com 'doentes_confirmados' e conta 'doente_confirmado_id'
        # em vez de 'registro_de_campo.caso_comfirmado'.
        query_grafico = """
            SELECT
                EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER AS ano,
                c.ciclo,
                COUNT(dc.doente_confirmado_id) AS casos_confirmados
            FROM
                ciclos c
            LEFT JOIN
                doentes_confirmados dc ON c.ciclo_id = dc.ciclo_id
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
                    "casos_confirmados": 0,
                    "dados_do_ultimo_ciclo": 0,
                    "porcentagem": "0%",
                    "crescimento": "estável"
                }
            }), 200

        # Lógica para calcular o resumo (permanece a mesma, pois o nome da coluna 'casos_confirmados' foi mantido)
        casos_confirmados_atual = 0
        casos_confirmados_anterior = 0

        # O último item da lista ordenada é o ciclo atual
        if len(dados_grafico) > 0:
            casos_confirmados_atual = int(dados_grafico[-1]['casos_confirmados'])

        # O penúltimo item é o ciclo anterior
        if len(dados_grafico) > 1:
            casos_confirmados_anterior = int(dados_grafico[-2]['casos_confirmados'])
        
        # Reutilização da lógica para cálculo de porcentagem
        porcentagem_str = "0%"
        crescimento_str = "estável"

        if casos_confirmados_anterior == 0:
            if casos_confirmados_atual > 0:
                porcentagem_str = "100% (Novo) ↑"
                crescimento_str = "aumentou"
        elif casos_confirmados_anterior > 0:
            if casos_confirmados_atual > casos_confirmados_anterior:
                percentage = round(((casos_confirmados_atual / casos_confirmados_anterior) - 1) * 100, 2)
                porcentagem_str = f"{percentage}% ↑"
                crescimento_str = "aumentou"
            elif casos_confirmados_atual < casos_confirmados_anterior:
                percentage = round((1 - (casos_confirmados_atual / casos_confirmados_anterior)) * 100, 2)
                porcentagem_str = f"{percentage}% ↓"
                crescimento_str = "diminuiu"

        # Monta o objeto de resumo
        resumo = {
            "casos_confirmados": casos_confirmados_atual,
            "dados_do_ultimo_ciclo": casos_confirmados_anterior,
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
        return jsonify({"error": "Falha na consulta ao banco de dados", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()