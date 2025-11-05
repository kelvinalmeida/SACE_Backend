from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required # Rota é pública
from .bluprint import graficos
import logging

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/total_doencas_confirmadas/<int:ano>/<int:ciclo>', methods=['GET'])
def get_total_doencas_confirmadas_historico(ano, ciclo):
    """
    Endpoint para obter dados históricos do total de doenças confirmadas
    (da tabela doencas_confirmadas) para um gráfico.

    Esta rota busca todos os dados de doenças confirmadas desde o início até o 
    ano e ciclo especificados. Retorna uma lista de pontos de dados para o 
    gráfico e um resumo comparando o ciclo atual com o anterior.
    """
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # Query SQL modificada para usar a tabela 'doencas_confirmadas'
        query_grafico = """
            SELECT
                EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER AS ano,
                c.ciclo,
                COUNT(dc.doenca_confirmada_id) AS total_doencas
            FROM
                ciclos c
            LEFT JOIN
                doencas_confirmadas dc ON c.ciclo_id = dc.ciclo_id
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
                    "total_doencas": 0,
                    "dados_do_ultimo_ciclo": 0,
                    "porcentagem": "0%",
                    "crescimento": "estável"
                }
            }), 200

        # Lógica para calcular o resumo (variáveis renomeadas)
        total_doencas_atual = 0
        total_doencas_anterior = 0

        if len(dados_grafico) > 0:
            total_doencas_atual = int(dados_grafico[-1]['total_doencas'])
        if len(dados_grafico) > 1:
            total_doencas_anterior = int(dados_grafico[-2]['total_doencas'])
        
        porcentagem_str = "0%"
        crescimento_str = "estável"

        if total_doencas_anterior == 0:
            if total_doencas_atual > 0:
                porcentagem_str = "100% (Novo) ↑"
                crescimento_str = "aumentou"
        elif total_doencas_anterior > 0:
            if total_doencas_atual > total_doencas_anterior:
                percentage = round(((total_doencas_atual / total_doencas_anterior) - 1) * 100, 2)
                porcentagem_str = f"{percentage}% ↑"
                crescimento_str = "aumentou"
            elif total_doencas_atual < total_doencas_anterior:
                percentage = round((1 - (total_doencas_atual / total_doencas_anterior)) * 100, 2)
                porcentagem_str = f"{percentage}% ↓"
                crescimento_str = "diminuiu"

        # Monta o objeto de resumo
        resumo = {
            "total_doencas": total_doencas_atual,
            "dados_do_ultimo_ciclo": total_doencas_anterior,
            "porcentagem": porcentagem_str,
            "crescimento": crescimento_str
        }
        
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