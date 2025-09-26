from flask import Flask, request, jsonify, Blueprint, current_app, session
import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from db import create_connection
from token_required import token_required

login = Blueprint('login', __name__)


@login.route('/login', methods=['POST'])
def login_user():
    cpf = request.json['username']  # aqui você pode pegar de request.json['username']
    password = request.json['password']  # aqui você pode pegar de request.json['username']

    # Cria conexão
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        search_user = """SELECT usuario_id, cpf, senha, nivel_de_acesso FROM usuario WHERE cpf = %s AND senha = %s;"""
        
        cursor.execute(search_user, (cpf, password))
        fech_user = cursor.fetchone()

        # return f"fech_user: {fech_user}"

        if fech_user is None:
            return jsonify({"error": "Authentication failed."}), 401
        

        # Define tempo de expiração (30 minutos a partir de agora)
        exp_time = datetime.utcnow() + timedelta(minutes=120)

        token = jwt.encode({
            "username": cpf,
            "exp": exp_time  # Define a expiração do token
        }, current_app.config['SECRET_KEY'], algorithm="HS256")

        session["usuario_id"] = fech_user["usuario_id"]

        # Se tudo certo, retorna o usuário
        return jsonify({
            "username": fech_user["cpf"],
            "nivel_de_acesso": fech_user["nivel_de_acesso"],
            "token": token,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

    
    
@login.route("/protected", methods=["GET"])
@token_required
def protected():
    return jsonify({"message": "You’ve entered a protected route. Welcome! You are logged in."})


@login.route('/teste_db', methods=['GET'])
@token_required
def login_teste():
    role = request.json['role']  # aqui você pode pegar de request.json['username']
    # password = request.json['password']  # aqui você pode pegar de request.json['username']

    # Cria conexão
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()

        search_user = """SELECT * FROM usuario WHERE nivel_de_acesso = %s;"""
        
        cursor.execute(search_user, (role,))
        fech = cursor.fetchall()


        # Se tudo certo, retorna o usuário
        return jsonify({
            "db": fech
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()





    