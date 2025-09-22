from flask import Flask, request, jsonify, Blueprint, current_app
import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from db import create_connection
from token_required import token_required

usuario = Blueprint('usuario', __name__)

@usuario.route('/usuarios', methods=['GET'])
@token_required
def get_usuarios():
    # Cria conexão
    conn = create_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        search_users = """SELECT usuario_id, nome_completo FROM usuarios;"""
        cursor.execute(search_users)
        rows = cursor.fetchall()

        usuarios = []
        for row in rows:
            usuarios.append({
                "usuario_id": row[0],
                "nome_completo": row[1]
            })

        return jsonify(usuarios)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        cursor.close()
