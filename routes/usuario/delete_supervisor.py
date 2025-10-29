from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging

logging.basicConfig(level=logging.INFO)

@usuario.route('/usuarios/supervisor/<int:supervisor_id>', methods=['DELETE'])
@token_required
def delete_supervisor(current_user, supervisor_id):
    """
    Deleta o supervisor e, usando ON DELETE CASCADE no DB, deleta o Usuário associado.
    """
    # 1. Validação de Supervisor
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: É necessário ser supervisor para deletar usuários."}), 403
    
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # 2. Obter o usuario_id associado ao supervisor_id
        search_user_id_query = """
            SELECT usuario_id 
            FROM supervisor 
            WHERE supervisor_id = %s;
        """
        cursor.execute(search_user_id_query, (supervisor_id,))
        supervisor_data = cursor.fetchone()

        if not supervisor_data:
            return jsonify({"error": f"supervisor com ID {supervisor_id} não encontrado."}), 404
        
        usuario_id = supervisor_data['usuario_id']

        # 3. Deletar o registro diretamente da tabela supervisor.
        # A regra ON DELETE CASCADE no DB DEVE deletar o registro em 'usuario'.
        # Se for um usuário que é SOMENTE supervisor, a linha de 'usuario' será removida.
        delete_supervisor_query = """
            DELETE FROM usuario 
            WHERE usuario_id = %s
            RETURNING usuario_id;
        """
        cursor.execute(delete_supervisor_query, (usuario_id,))
        
        # 4. Verificar se a linha de supervisor foi realmente deletada
        deleted_supervisor = cursor.fetchone()
        
        if not deleted_supervisor:
            conn.rollback()
            return jsonify({"error": f"Falha ao deletar supervisor {supervisor_id}."}), 500
        
        conn.commit()

        return jsonify({
            "status": "success",
            "message": f"Supervisor com ID {supervisor_id} deletado com sucesso.",
            "supervisor_id": supervisor_id
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Erro ao deletar supervisor {supervisor_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao deletar dados.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

