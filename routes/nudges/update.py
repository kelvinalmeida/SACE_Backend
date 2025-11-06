from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import nudges_bp
import logging

logging.basicConfig(level=logging.INFO)

@nudges_bp.route('/nudges/<int:nudges_id>', methods=['PUT'])
@token_required
def update_nudge(current_user, nudges_id):
    """
    Atualiza um nudge existente.
    Requer permissão de supervisor.
    """
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: Apenas supervisores podem atualizar nudges."}), 403

    data = request.json
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
        
        update_sql = """
            UPDATE nudges
            SET titulo = %s, descricao = %s, url = %s
            WHERE nudges_id = %s
            RETURNING nudges_id, titulo, descricao, url;
        """
        
        cursor.execute(update_sql, (titulo, descricao, url, nudges_id))
        updated_nudge = cursor.fetchone()
        
        if not updated_nudge:
            return jsonify({"error": "Nudge não encontrado."}), 404
        
        conn.commit()
        return jsonify(updated_nudge), 200

    except Exception as e:
        if conn: conn.rollback()
        logging.error(f"Erro ao atualizar nudge: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao atualizar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()