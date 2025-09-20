from flask import Flask, request, jsonify, Blueprint, current_app, app
import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from db import create_connection
from token_required import token_required

login = Blueprint('login', __name__)


@login.route('/login', methods=['POST'])
def login_page():
    username = request.json['username']  # aqui você pode pegar de request.json['username']
    password = request.json['password']  # aqui você pode pegar de request.json['username']

    # app.logger.debug('A value for debugging')
    # app.logger.warning('A warning occurred (%d apples)', 42)
    # app.logger.error('An error occurred')

    try:
        if not username == 'admin': 
            return jsonify({"error": "Username not found"}), 404
        
        if not password == '123456':
            return jsonify({"error": "Incorrect password"}), 401
        
        # Define tempo de expiração (30 minutos a partir de agora)
        exp_time = datetime.utcnow() + timedelta(minutes=120)

        token = jwt.encode({
            "username": username,
            "exp": exp_time  # Define a expiração do token
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        # Se tudo certo, retorna o usuário
        return jsonify({
            "username": username,
            "token": token
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@login.route("/protected", methods=["GET"])
@token_required
def protected():
    return jsonify({"message": "You’ve entered a protected route. Welcome! You are logged in."})


@login.route('/teste_db', methods=['GET'])
@token_required
def login_user():
    # username = request.json['username']  # aqui você pode pegar de request.json['username']
    # password = request.json['password']  # aqui você pode pegar de request.json['username']

    # Cria conexão
    conn = create_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        search_user = """SELECT u.nome_completo, u.cpf, u.usuario_id, s.usuario_id, s.supervisor_id  FROM supervisor s INNER JOIN usuario u USING(usuario_id);"""
        
        cursor.execute(search_user)
        fech_user = cursor.fetchall() 


        # Se tudo certo, retorna o usuário
        return jsonify({
            "db": fech_user
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


    