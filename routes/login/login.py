from flask import Flask, request, jsonify, Blueprint, current_app, session
import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from db import create_connection
from routes.login.token_required import token_required

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

        search_user = """SELECT usuario_id, cpf, senha, nome_completo, nivel_de_acesso FROM usuario WHERE cpf = %s AND senha = %s;"""
        
        cursor.execute(search_user, (cpf, password))
        fech_user = cursor.fetchone()

        print("fech_user:", fech_user)

        # return f"fech_user: {fech_user}"

        if fech_user is None:
            return jsonify({"error": "Authentication failed."}), 401
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    try:
        cursor.close()
        cursor = conn.cursor()

        # Query para buscar o agente_id do usuário logado
        search_agente = """SELECT agente_id FROM agente WHERE usuario_id = %s;"""
        cursor.execute(search_agente, (fech_user["usuario_id"],))
        fech_agente = cursor.fetchone()
    except Exception as e:
        fech_agente = None

    try:
        cursor.close()
        cursor = conn.cursor()

        # Query para buscar o supervisor_id do usuário logado
        search_supervisor = """SELECT supervisor_id FROM supervisor WHERE usuario_id = %s;"""
        cursor.execute(search_supervisor, (fech_user["usuario_id"],))
        fech_supervisor = cursor.fetchone()
    except Exception as e:
        fech_supervisor = None
    finally:
        cursor.close()
        conn.close()

    print("fech_agente:", fech_agente)
    print("fech_supervisor:", fech_supervisor)
    
    if not fech_agente and not fech_supervisor:
        return jsonify({"error": "Invalid token: 'É nescessário ser agente ou supervisor para logar. Peça para um supervisor cadastrar você.'"}), 401


    # Define tempo de expiração (30 minutos a partir de agora)
    exp_time = datetime.utcnow() + timedelta(minutes=120)

    if fech_supervisor and fech_agente:
        token = jwt.encode({
        "username": cpf,
        "exp": exp_time,  # Define a expiração do token
        "usuario_id": fech_user["usuario_id"],
        "agente_id": fech_agente["agente_id"],
        "supervisor_id": fech_supervisor["supervisor_id"],
        "nivel_de_acesso": fech_user["nivel_de_acesso"]
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    elif fech_agente:
        token = jwt.encode({
        "username": cpf,
        "exp": exp_time,  # Define a expiração do token
        "usuario_id": fech_user["usuario_id"],
        "agente_id": fech_agente["agente_id"],
        "nivel_de_acesso": fech_user["nivel_de_acesso"]
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    else:
        token = jwt.encode({
        "username": cpf,
        "exp": exp_time,  # Define a expiração do token
        "usuario_id": fech_user["usuario_id"],
        "supervisor_id": fech_supervisor["supervisor_id"],
        "nivel_de_acesso": fech_user["nivel_de_acesso"]
    }, current_app.config['SECRET_KEY'], algorithm="HS256")


    # Se tudo certo, retorna o usuário
    return jsonify({
        "nome_completo": fech_user["nome_completo"],
        "username": fech_user["cpf"],
        "nivel_de_acesso": fech_user["nivel_de_acesso"],
        "usuario_id": fech_user["usuario_id"],
        "agente_id": fech_agente["agente_id"] if fech_agente else None,
        "supervisor_id": fech_supervisor["supervisor_id"] if fech_supervisor else None,
        "token": token,
    })
    
    
@login.route("/protected", methods=["GET"])
@token_required
def protected(current_user):
    return jsonify({"message": "You’ve entered a protected route. Welcome! You are logged in."})



    