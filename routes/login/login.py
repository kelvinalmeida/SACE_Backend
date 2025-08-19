from flask import Flask, request, jsonify, Blueprint, current_app
import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from db import create_connection
from token_required import token_required

login = Blueprint('login', __name__)


@login.route('/login', methods=['GET'])
def login_page():
    username = request.json['username']  # aqui você pode pegar de request.json['username']
    password = request.json['password']  # aqui você pode pegar de request.json['username']

    try:
        if not username == 'admin': 
            return jsonify({"error": "Username not found"}), 404
        
        if not password == '123456':
            return jsonify({"error": "Incorrect password"}), 401
        
        # Define tempo de expiração (30 minutos a partir de agora)
        exp_time = datetime.utcnow() + timedelta(minutes=30)

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


# @login.route('/login', methods=['POST'])
# def login_user():
#     username = request.json['username']  # aqui você pode pegar de request.json['username']
#     password = request.json['password']  # aqui você pode pegar de request.json['username']

#     # Cria conexão
#     conn = create_connection()
#     if conn is None:
#         return jsonify({"error": "Database connection failed"}), 500

#     try:
#         cursor = conn.cursor()

#         search_user = """SELECT username, password 
#                          FROM accounts 
#                          WHERE username = %s;"""
        
#         cursor.execute(search_user, (username,))
#         fech_user = cursor.fetchone()

#         if fech_user is None:
#             return jsonify({"error": "Username not found"}), 404
        
#         if not fech_user["password"] == password:
#             return jsonify({"error": "Incorrect password"}), 401
        

#         # Define tempo de expiração (30 minutos a partir de agora)
#         exp_time = datetime.utcnow() + timedelta(minutes=30)

#         token = jwt.encode({
#             "username": fech_user["username"],
#             "role": "Deu Certo",
#             "exp": exp_time  # Define a expiração do token
#         }, current_app.config['SECRET_KEY'], algorithm="HS256")

#         # Se tudo certo, retorna o usuário
#         return jsonify({
#             "username": fech_user["username"],
#             "token": token
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     finally:
#         cursor.close()
#         conn.close()


    