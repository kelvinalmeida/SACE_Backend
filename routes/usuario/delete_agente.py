from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging


@usuario.route('/usuarios/agente/<int:agente_id>', methods=['DELETE'])
@token_required
def delete_agente(current_user, agente_id):

    # 1. Validação de Supervisor
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: É necessário ser supervisor para deletar usuários."}), 403
    
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # 2. Obter o usuario_id associado ao agente_id
        search_user_id_query = """
            SELECT usuario_id 
            FROM agente 
            WHERE agente_id = %s;
        """
        cursor.execute(search_user_id_query, (agente_id,))
        agente_data = cursor.fetchone()

        if not agente_data:
            return jsonify({"error": f"Agente com ID {agente_id} não encontrado."}), 404
        
        usuario_id = agente_data['usuario_id']


        delete_agente_query = """
            DELETE FROM usuario 
            WHERE usuario_id = %s
            RETURNING usuario_id;
        """
        cursor.execute(delete_agente_query, (usuario_id,))
        
        # 4. Verificar se a linha de Agente foi realmente deletada
        deleted_agente = cursor.fetchone()
        
        if not deleted_agente:
            conn.rollback()
            return jsonify({"error": f"Falha ao deletar Agente {agente_id}."}), 500
        
        conn.commit()

        return jsonify({
            "status": "success",
            "message": f"Agente com ID {agente_id} deletado com sucesso.",
            "agente_id": agente_id
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Erro ao deletar agente {agente_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao deletar dados.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()