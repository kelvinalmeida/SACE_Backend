from flask import jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import nudges_bp
import logging

logging.basicConfig(level=logging.INFO)

@nudges_bp.route('/nudges/<int:nudges_id>', methods=['DELETE'])
@token_required
def delete_nudge(current_user, nudges_id):
    """
    Deleta um nudge.
    Requer permissão de supervisor.
    """
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: Apenas supervisores podem deletar nudges."}), 403

    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()
        
        delete_sql = "DELETE FROM nudges WHERE nudges_id = %s RETURNING nudges_id;"
        
        cursor.execute(delete_sql, (nudges_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Nudge não encontrado."}), 404
        
        conn.commit()
        return jsonify({"message": "Nudge deletado com sucesso.", "id_deletado": result['nudges_id']}), 200

    except Exception as e:
        if conn: conn.rollback()
        logging.error(f"Erro ao deletar nudge: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao deletar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()