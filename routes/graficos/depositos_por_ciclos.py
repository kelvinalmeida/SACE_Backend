from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required # Mantenha se for usar autenticação
from .bluprint import graficos
import logging
from collections import defaultdict

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/depositos_por_ciclo/<int:ano>', methods=['GET'])
def get_depositos_por_ciclo(ano):
    """
    Endpoint para obter dados para o gráfico de 'Depósitos por Ciclos'.

    Esta rota busca a quantidade total de depósitos (soma de a1, a2, b, c, d1, d2, e)
    para cada bairro, agrupados por ciclo, dentro de um ano específico.
    """
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # Query SQL para buscar e somar os depósitos por bairro e ciclo
        query = """
            SELECT
                av.bairro,
                c.ciclo,
                COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0)::INTEGER AS quantidade
            FROM
                registro_de_campo rc
            JOIN
                area_de_visita av ON rc.area_de_visita_id = av.area_de_visita_id
            JOIN
                ciclos c ON rc.ciclo_id = c.ciclo_id
            JOIN
                depositos d ON rc.deposito_id = d.deposito_id
            WHERE
                EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER = %s
            GROUP BY
                av.bairro, c.ciclo
            ORDER BY
                av.bairro, c.ciclo;
        """
        cursor.execute(query, (ano,))
        resultados = cursor.fetchall()

        # Se não houver dados, retorna uma estrutura vazia
        if not resultados:
            return jsonify({
                "labels": [],
                "datasets": []
            }), 200

        # --- Processamento dos dados para o formato do gráfico ---
        max_ciclo = 0
        if resultados:
            max_ciclo = max(row['ciclo'] for row in resultados)
        
        labels = [f"Ciclo {i}" for i in range(1, max_ciclo + 1)]

        dados_por_bairro = defaultdict(lambda: [0] * max_ciclo)

        for row in resultados:
            bairro = row['bairro']
            ciclo = row['ciclo']
            quantidade = row['quantidade']
            # O índice na lista é ciclo - 1 (ex: Ciclo 1 -> índice 0)
            dados_por_bairro[bairro][ciclo - 1] = quantidade
        
        # Formata a saída no padrão de datasets para bibliotecas de gráficos
        datasets = []
        for bairro, data in dados_por_bairro.items():
            datasets.append({
                "label": bairro,
                "data": data
            })

        return jsonify({
            "labels": labels,
            "datasets": datasets
        }), 200

    except Exception as e:
        logging.error(f"Falha na consulta ao banco de dados: {e}")
        return jsonify({"error": "Falha na consulta ao banco de dados", "details": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
