from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required
from .bluprint import graficos
import logging
from collections import defaultdict

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/casos_por_ciclo/<int:ano>', methods=['GET'])
def get_casos_por_ciclo(ano):
    """
    Endpoint para obter dados para o gráfico de 'Casos por Ciclos'.

    Esta rota busca a quantidade de casos confirmados (da tabela doentes_confirmados)
    para cada bairro, agrupados por ciclo, dentro de um ano específico.
    """
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # --- CORREÇÃO: ETAPA 1 ---
        # Primeiro, descobrimos qual é o número máximo de ciclo para o ano selecionado,
        # independentemente de ter tido casos ou não.
        get_max_ciclo_query = """
            SELECT MAX(ciclo) AS max_ciclo
            FROM ciclos
            WHERE EXTRACT(YEAR FROM ano_de_criacao)::INTEGER = %s;
        """
        cursor.execute(get_max_ciclo_query, (ano,))
        max_ciclo_result = cursor.fetchone()

        max_ciclo = 0
        if max_ciclo_result and max_ciclo_result['max_ciclo'] is not None:
            max_ciclo = int(max_ciclo_result['max_ciclo'])
        
        # Se não há ciclos para este ano (max_ciclo = 0), retorna vazio.
        if max_ciclo == 0:
            return jsonify({"labels": [], "datasets": []}), 200


        # --- ETAPA 2: Query original (para buscar apenas os dados que existem) ---
        # Não precisamos alterar esta query, pois a lógica Python agora
        # vai preencher os "buracos" (ciclos sem casos).
        query = """
            SELECT
                dc.bairro,
                c.ciclo,
                COUNT(dc.doente_confirmado_id) AS quantidade
            FROM
                doentes_confirmados dc
            JOIN
                ciclos c ON dc.ciclo_id = c.ciclo_id
            WHERE
                EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER = %s
                AND dc.bairro IS NOT NULL
            GROUP BY
                dc.bairro, c.ciclo
            ORDER BY
                dc.bairro, c.ciclo;
        """
        cursor.execute(query, (ano,))
        resultados = cursor.fetchall()

        # --- Processamento (Agora funciona corretamente) ---
        
        # 'labels' agora usa o 'max_ciclo' real (ex: 4 para 2025)
        labels = [f"Ciclo {i}" for i in range(1, max_ciclo + 1)]

        # 'dados_por_bairro' cria listas com o tamanho correto (ex: [0, 0, 0, 0])
        dados_por_bairro = defaultdict(lambda: [0] * max_ciclo)

        # O loop 'resultados' (que para 2025, só tem ciclos 1 e 2)
        # preenche apenas as posições [0] e [1] dos bairros encontrados.
        for row in resultados:
            bairro = row['bairro']
            ciclo = row['ciclo']
            quantidade = row['quantidade']
            # O índice na lista é ciclo - 1 (ex: Ciclo 1 -> índice 0)
            dados_por_bairro[bairro][ciclo - 1] = quantidade
        
        # Formata a saída. Bairros com dados nos ciclos 1 e 2
        # agora aparecerão com [X, Y, 0, 0] para 2025.
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