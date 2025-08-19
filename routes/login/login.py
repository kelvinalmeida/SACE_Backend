from flask import Flask, request, jsonify, Blueprint
import jwt
from datetime import datetime
from db import create_connection

login = Blueprint('login', __name__)

@login.route('/login', methods=['POST'])
def login_user():
    username = request.json['username']  # aqui você pode pegar de request.json['username']
    password = request.json['password']  # aqui você pode pegar de request.json['username']

    # Cria conexão
    conn = create_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        search_user = """SELECT username, password 
                         FROM accounts 
                         WHERE username = %s AND password = %s;"""
        
        cursor.execute(search_user, (username, password))
        fech_user = cursor.fetchone()

        if fech_user is None:
            return jsonify({"error": "User not found"}), 404

        # Se tudo certo, retorna o usuário
        return jsonify({
            "username": fech_user["username"],
            "password": fech_user["password"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# @login.route('/login', methods=['POST'])
# def login_user():
#     # Cria conexão
#     conn = create_connection()
#     if conn is None:
#         return jsonify({"error": "Database connection failed"}), 500

#     try:
#         cursor = conn.cursor()

#         search_user = """SELECT * FROM accounts;"""
#         cursor.execute(search_user)
#         users = cursor.fetchall()  # <- pega todos

#         if not users:
#             return jsonify({"error": "No users found"}), 404

#         # Retorna todos os usuários como JSON
#         return jsonify(users)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     finally:
#         cursor.close()
#         conn.close()