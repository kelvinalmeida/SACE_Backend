from flask import jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import doentes_confirmados_bp
import logging

logging.basicConfig(level=logging.INFO)

@doentes_confirmados_bp.route('/doente_confirmado/<int:doenca_id>', methods=['DELETE'])
@token_required
def delete_doente_confirmado(current_user, doenca_id):
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
        
        delete_sql = "DELETE FROM doentes_confirmados WHERE doente_confirmado_id = %s RETURNING doente_confirmado_id;"
        
        cursor.execute(delete_sql, (doenca_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Registro não encontrado."}), 404
        
        conn.commit()
        return jsonify({"message": "Registro deletado com sucesso.", "id_deletado": result['doente_confirmado_id']}), 200

    except Exception as e:
        if conn: conn.rollback()
        logging.error(f"Erro ao deletar doença confirmada: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao deletar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()