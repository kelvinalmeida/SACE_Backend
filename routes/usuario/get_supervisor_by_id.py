from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@usuario.route('/usuarios/supervisor/<int:supervisor_id>', methods=['GET'])
@token_required
def get_supervisor(current_user, supervisor_id):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()

        search_user = """SELECT * FROM supervisor INNER JOIN usuario USING(usuario_id) WHERE supervisor_id = %s;"""

        cursor.execute(search_user, (supervisor_id,))

        supervisor = cursor.fetchone()
        
        
        # Adicionar esta verificação:
        if supervisor is None:
            return jsonify({"error": "Usuário não encontrado"}), 404

        return jsonify(supervisor), 200

    
    except Exception as e:
        return jsonify({"error": str(e)})
    
    