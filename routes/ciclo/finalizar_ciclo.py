from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from datetime import datetime
from .bluprint import ciclos
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

@ciclos.route('/finalizar_ciclo', methods=['POST'])
@token_required
def finalizar_ciclo(current_user):

    # --- VERIFICAÇÃO DE PERMISSÃO ---
    if current_user.get("nivel_de_acesso") not in ["supervisor"]:
        return jsonify({"error": "Acesso negado: É necessário ser supervisor para criar um novo ciclo."}), 403

    conn = None
    cursor = None
    try:
        # --- CONEXÃO COM O BANCO ---
        # É uma boa prática usar um bloco `with` para garantir que a conexão seja fechada,
        # mas vamos manter a estrutura original com try/except/finally corrigida.
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
        
        # Usar um cursor que retorna dicionários facilita o acesso aos dados por nome de coluna.
        # Se você estiver usando psycopg2, seria algo como: cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor = conn.cursor()

        # --- BUSCAR O ÚLTIMO CICLO ATIVO DE FORMA EFICIENTE ---
        # CORREÇÃO 1: Em vez de buscar todos os ciclos, buscamos apenas o último.
        # Adicionado ORDER BY para garantir que o último ciclo seja realmente o mais recente.
        get_last_cicle_query = """
            SELECT ciclo_id, ciclo, EXTRACT(YEAR FROM ano_de_criacao)::INTEGER AS ano 
            FROM ciclos 
            ORDER BY ano_de_criacao DESC, ciclo DESC 
            LIMIT 1
        """
        cursor.execute(get_last_cicle_query)
        ultimo_ciclo_db = cursor.fetchone()

        # return jsonify(ultimo_ciclo_db)

        # --- LÓGICA PARA CRIAR NOVO CICLO ---
        current_datetime = datetime.now()
        id_ultimo_ciclo = None

        if ultimo_ciclo_db:
            id_ultimo_ciclo = ultimo_ciclo_db['ciclo_id']
            numero_ciclo = ultimo_ciclo_db['ciclo']
            ano = ultimo_ciclo_db['ano']

            # Desativa o ciclo anterior
            set_last_ciclo_inactive_query = """
                UPDATE ciclos SET ativo = False, encerramento = %s WHERE ciclo_id = %s;
            """
            cursor.execute(set_last_ciclo_inactive_query, (current_datetime, id_ultimo_ciclo))

            conn.commit()

        # CORREÇÃO 4: Removido o código inalcançável. O retorno agora é mais informativo.
        return jsonify({
            "message": "Ciclo desativado. Novos registros de campo não serão mais inseridos até que um novo ciclo seja criado (ativado.)",
            "novo_ciclo": {
                "id": id_ultimo_ciclo,
                "numero": numero_ciclo,
                "ano": ano
            }
        }), 201
    
    except Exception as e:
        # Se qualquer erro ocorrer, o rollback desfaz todas as operações no banco.
        if conn:
            conn.rollback()
        logging.error(f"Erro ao criar ciclo: {e}")
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação."}), 500

    finally:
        # O `finally` garante que o cursor e a conexão serão sempre fechados.
        if cursor:
            cursor.close()
        if conn:
            conn.close()
