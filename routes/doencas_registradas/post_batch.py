from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import doencas_confirmadas_bp
import logging

# Configuração de log
logging.basicConfig(level=logging.INFO)

@doencas_confirmadas_bp.route('/doencas_confirmadas', methods=['POST'])
@token_required
def create_doencas_confirmadas_batch(current_user):
    """
    Cria um ou mais registros de doenças confirmadas a partir de um array JSON.
    Requer permissão de supervisor.
    """
    # 1. Validação de Permissão
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: Apenas supervisores podem criar registros."}), 403

    # 2. Validação da Entrada
    data = request.json
    if not isinstance(data, list) or not data:
        return jsonify({"error": "A entrada deve ser uma lista não vazia de doenças confirmadas."}), 400

    conn = None
    cursor = None
    created_ids = []

    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
        
        cursor = conn.cursor()

        # 3. Obter o ciclo ativo (essencial para associar o registro)
        check_ciclo_sql = "SELECT ciclo_id FROM ciclos WHERE ativo = True LIMIT 1;"
        cursor.execute(check_ciclo_sql)
        ciclo_ativo = cursor.fetchone()
        
        if not ciclo_ativo:
            return jsonify({"error": "Nenhum ciclo ativo encontrado. Crie um novo ciclo antes de adicionar casos."}), 409 # 409 Conflict
        
        ciclo_id = ciclo_ativo['ciclo_id']

        # 4. Preparar o SQL de Inserção
        insert_sql = """
            INSERT INTO doencas_confirmadas (nome, tipo_da_doenca, rua, numero, bairro, ciclo_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING doenca_confirmada_id;
        """

        # 5. Iterar e Inserir cada item do array
        for item in data:
            # Validação dos campos NOT NULL
            if not item.get('tipo_da_doenca') or not item.get('rua'):
                conn.rollback() # Desfaz inserções anteriores desta transação
                return jsonify({"error": "Campos 'tipo_da_doenca' e 'rua' são obrigatórios."}), 400
            
            values = (
                item.get('nome'),
                item['tipo_da_doenca'],
                item['rua'],
                item.get('numero'),
                item.get('bairro'),
                ciclo_id # Associa ao ciclo ativo
            )
            
            cursor.execute(insert_sql, values)
            new_id = cursor.fetchone()['doenca_confirmada_id']
            created_ids.append(new_id)

        # 6. Commit final
        conn.commit()
        
        return jsonify({
            "message": f"{len(created_ids)} registros de doenças confirmadas criados com sucesso.",
            "ids_criados": created_ids,
            "ciclo_id_associado": ciclo_id
        }), 201

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Erro ao criar doenças confirmadas em lote: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao processar a solicitação.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()