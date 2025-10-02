from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@usuario.route('/usuarios/<int:user_id>', methods=['GET'])
@token_required
def get_user_by_id(current_user, user_id):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()

        search_user = """SELECT * FROM usuario INNER JOIN agente USING(usuario_id) WHERE usuario_id = %s;"""

        cursor.execute(search_user, (user_id,))

        usuario = cursor.fetchone()
    

        if(not usuario):

            search_user = """SELECT * FROM usuario INNER JOIN supervisor USING(usuario_id) WHERE usuario_id = %s;"""

            cursor.execute(search_user, (user_id,))

            usuario = cursor.fetchone()
        
        
        # Adicionar esta verificação:
        if usuario is None:
            return jsonify({"error": "Usuário não encontrado"}), 404

        return jsonify(usuario), 200

    
    except Exception as e:
        return jsonify({"error": str(e)})
    
    