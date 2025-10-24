from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from .bluprint import denuncia
from datetime import datetime


def check_required_filds(required_fild):
    for fild in required_fild:
        if fild not in request.form or request.form[fild] is None or request.form[fild].strip() == "":
            return {"error": f"{fild} is required"}
    return False

@denuncia.route('/denuncia/<int:denuncia_id>', methods=['DELETE'])
@token_required
def delete_denuncia(current_user, denuncia_id):

    if(current_user["nivel_de_acesso"] not in ["supervisor"]):
        return jsonify({"error": "Invalid token: É nescessário ser supervisor para cadastrar denuncia."}), 403

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # Deletar denuncia do banco de dados
    try:
        cursor = conn.cursor()
        delete_query = "DELETE FROM denuncia WHERE denuncia_id = %s RETURNING denuncia_id;"
        cursor.execute(delete_query, (denuncia_id,))
        result = cursor.fetchone()

        if result is None:
            return jsonify({"error": "Denúncia não encontrada"}), 404
        
        conn.commit()

        

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()
        cursor.close()

    return jsonify({
        "message": "Denúncia deletada com sucesso",
        "denuncia_id": denuncia_id
     }), 200




    

