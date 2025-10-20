from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required # Mantenha se for usar autenticação
from .bluprint import graficos
import logging

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/depositos_identificados/<int:ano>/<int:ciclo>', methods=['GET'])
def get_depositos_identificados(ano, ciclo):
    """
    Endpoint para obter dados históricos de depósitos identificados para um gráfico.

    Esta rota busca o somatório de todos os tipos de depósitos (a1, a2, b, c, d1, d2, e)
    para cada ciclo, desde o início até o ano e ciclo especificados.
    """
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # Query SQL otimizada para buscar e somar os depósitos de todos os ciclos
        query_grafico = """
            SELECT
                EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER AS ano,
                c.ciclo,
                COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0)::INTEGER AS depositos_identificados
            FROM
                ciclos c
            LEFT JOIN
                registro_de_campo rc ON c.ciclo_id = rc.ciclo_id AND (rc.t = True OR rc.li = True OR rc.df = True)
            LEFT JOIN
                depositos d ON rc.deposito_id = d.deposito_id
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
                    "depositos_identificados": 0,
                    "dados_do_ultimo_ciclo": 0,
                    "porcentagem": "0%",
                    "crescimento": "estável"
                }
            }), 200

        # Lógica para calcular o resumo com base nos dois últimos ciclos da lista retornada
        depositos_atual = 0
        depositos_anterior = 0

        if len(dados_grafico) > 0:
            depositos_atual = int(dados_grafico[-1]['depositos_identificados'])
        if len(dados_grafico) > 1:
            depositos_anterior = int(dados_grafico[-2]['depositos_identificados'])
        
        # Reutilização da lógica para cálculo de porcentagem
        porcentagem_str = "0%"
        crescimento_str = "estável"

        if depositos_anterior == 0:
            if depositos_atual > 0:
                porcentagem_str = "100% (Novo) ↑"
                crescimento_str = "aumentou"
        elif depositos_anterior > 0:
            if depositos_atual > depositos_anterior:
                percentage = round(((depositos_atual / depositos_anterior) - 1) * 100, 2)
                porcentagem_str = f"{percentage}% ↑"
                crescimento_str = "aumentou"
            elif depositos_atual < depositos_anterior:
                percentage = round((1 - (depositos_atual / depositos_anterior)) * 100, 2)
                porcentagem_str = f"{percentage}% ↓"
                crescimento_str = "diminuiu"

        # Monta o objeto de resumo
        resumo = {
            "depositos_identificados": depositos_atual,
            "dados_do_ultimo_ciclo": depositos_anterior,
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
