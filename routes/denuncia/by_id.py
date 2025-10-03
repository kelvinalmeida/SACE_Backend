from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import denuncia
import datetime

def serialize_data(data):
    """
    Recursively converts non-serializable objects (like datetime.time)
    into strings suitable for JSON.
    """
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, (datetime.date, datetime.datetime, datetime.time)):
        # Convert date, datetime, and time objects to ISO 8601 strings
        return data.isoformat()
    # Handle other types like Decimal if necessary, e.g.:
    # elif isinstance(data, Decimal):
    #     return str(data) 
    else:
        return data


@denuncia.route('/denuncia/<int:denuncia_id>', methods=['GET'])
@token_required
def get_denuncia_by_id(current_user, denuncia_id):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # Query para buscar todos os usuários agentes relacionando ao registro de campo
        search_denuncias = """SELECT * FROM denuncia INNER JOIN supervisor USING(supervisor_id) INNER JOIN usuario usu USING(usuario_id) WHERE denuncia_id = %s;"""

        cursor.execute(search_denuncias, (denuncia_id, ))
        all_denuncias = cursor.fetchall()

        # denuncias_list = dict(all_denuncias)
        
        all_denuncias_dicts = [dict(denc) for denc in all_denuncias]
        serializable_denuncias = serialize_data(all_denuncias_dicts)

        # return jsonify(serializable_denuncias), 200
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500


    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar depósitos
        search_depositos = """SELECT denunc.denuncia_id, a1, a2, b, c, d1, d2, e
                            FROM denuncia denunc
                            LEFT JOIN depositos dep USING(deposito_id);"""
        
        cursor.execute(search_depositos)
        depositos = cursor.fetchall()

        for denunc in serializable_denuncias:
            deposito = next((dep for dep in depositos if dep['denuncia_id'] == denunc['denuncia_id']), None)
            if deposito:
                deposito = deposito.copy()  # Faz uma cópia para não alterar o original
                deposito.pop('denuncia_id', None)  # Remove a chave se existir
            denunc['deposito'] = deposito

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar arquivos
        search_arquivos = """SELECT den.denuncia_id, arquivo_nome, arquivo_denuncia_id
                            FROM denuncia den
                            LEFT JOIN arquivos_denuncia USING(denuncia_id);"""
        
        cursor.execute(search_arquivos)
        arquivos = cursor.fetchall()

        for denunc in serializable_denuncias:
            arquivos_reg = [arq.copy() for arq in arquivos if arq['denuncia_id'] == denunc['denuncia_id'] and arq['arquivo_nome'] is not None]
            for arq in arquivos_reg:
                arq.pop('denuncia_id', None)

            denunc['arquivos'] = arquivos_reg

        
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    

    finally:
        conn.close()
        cursor.close()

    try:    
        return jsonify(serializable_denuncias[0]), 200
    except Exception as e:
        return jsonify({"error": "denuncia não encontrada"}), 404