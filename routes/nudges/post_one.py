from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import nudges_bp
import logging

logging.basicConfig(level=logging.INFO)

@nudges_bp.route('/nudges', methods=['POST'])
@token_required
def create_nudge(current_user):
    """
    Cria um novo nudge (dica/notificação).
    Requer permissão de supervisor.
    """
    # 1. Validação de Permissão (apenas supervisores podem criar)
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: Apenas supervisores podem criar nudges."}), 403

    data = request.json
    
    # 2. Validação de Campos Obrigatórios
    titulo = data.get('titulo')
    descricao = data.get('descricao')
    url = data.get('url')
    
    if not all([titulo, descricao, url]):
        return jsonify({"error": "Campos 'titulo', 'descricao' e 'url' são obrigatórios."}), 400

    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()
        
        insert_sql = """
            INSERT INTO nudges (titulo, descricao, url)
            VALUES (%s, %s, %s)
            RETURNING nudges_id, titulo, descricao, url;
        """
        
        cursor.execute(insert_sql, (titulo, descricao, url))
        new_nudge = cursor.fetchone()
        conn.commit()

        
        return jsonify(new_nudge), 201

    except Exception as e:
        if conn: conn.rollback()
        logging.error(f"Erro ao criar nudge: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao criar registro.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()