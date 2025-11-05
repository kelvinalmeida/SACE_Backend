from flask import jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import doencas_confirmadas_bp
import logging

logging.basicConfig(level=logging.INFO)

@doencas_confirmadas_bp.route('/doencas_confirmadas/<int:doenca_id>', methods=['DELETE'])
@token_required
def delete_doenca_confirmada(current_user, doenca_id):
    """
    Deleta um registro de doença confirmada.
    Requer permissão de supervisor.
    """
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: Apenas supervisores podem deletar."}), 403

    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()
        
        delete_sql = "DELETE FROM doencas_confirmadas WHERE doenca_confirmada_id = %s RETURNING doenca_confirmada_id;"
        
        cursor.execute(delete_sql, (doenca_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Registro não encontrado."}), 404
        
        conn.commit()
        return jsonify({"message": "Registro deletado com sucesso.", "id_deletado": result['doenca_confirmada_id']}), 200

    except Exception as e:
        if conn: conn.rollback()
        logging.error(f"Erro ao deletar doença confirmada: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao deletar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()