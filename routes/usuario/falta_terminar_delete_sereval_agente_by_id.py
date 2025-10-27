from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging


# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@usuario.route('/usuarios/agentes', methods=['DELETE'])
@token_required
def deletar_varios_agentes(current_user):
    # 1. Validação de Supervisor
    if not current_user or current_user.get("supervisor_id") is None or current_user.get("nivel_de_acesso") not in ["supervisor"]: 
        return jsonify({"error": "É necessário ser supervisor para cadastrar usuários."}), 403
     

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    


    ids = request.json.get('ids', [])

    if not isinstance(ids, list):
        return jsonify({"error": "Os dados devem ser uma lista JSON de usuários."}), 400


    
    try:
        cursor = conn.cursor()
        
        # SQL para verificar a unicidade de CPF/Email
        search_usuario = """
            SELECT agente_id, usuario_id FROM usuario INNER JOIN agente USING(usuario_id) WHERE agente_id = %s;;
        """
        for id in ids:

            cursor.execute(search_usuario, (ids[0],))

            existing_user = cursor.fetchone()

            usuario_id = existing_user['usuario_id']
            agente_id = existing_user['agente_id']
            # return jsonify({"msg": [usuario_id, agente_id]}), 200

            # Deletar o agente
            delete_agente = "DELETE FROM agente WHERE agente_id = %s;"
            cursor.execute(delete_agente, (agente_id,))
            # Deletar o usuário associado
            delete_usuario = "DELETE FROM usuario WHERE usuario_id = %s;"
            cursor.execute(delete_usuario, (usuario_id,))

            if not existing_user:
                conn.rollback()
                return jsonify({"error": f"Agente com id: {id} não encontrado."}), 404

        conn.commit()

        return jsonify({
            "message": f"{len(ids)} Agentes deletados com sucesso.",
            "ids_deletados": ids
        }), 200
 
    except Exception as e:
        # Rollback em caso de qualquer outro erro de banco de dados
        logging.error(f"Erro durante ao deletar em lote de usuários: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": f"Erro de banco de dados: {str(e)}"}), 500
    
    finally:
        # 7. Fechamento da Conexão
        if conn:
            cursor.close()
            conn.close()
