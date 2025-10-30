from flask import Flask, request, jsonify, Blueprint, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo

@registro_de_campo.route('/casos_confirmado/<int:registro_de_campo_id>', methods=['PUT'])
@token_required
def casos_confirmado(current_user, registro_de_campo_id):
    
    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # verificando se existe algum ciclo ativo
    try:
        cursor = conn.cursor()

        update_registros_de_campo = """UPDATE registro_de_campo SET caso_comfirmado = TRUE WHERE registro_de_campo_id = %s RETURNING registro_de_campo_id;"""
        cursor.execute(update_registros_de_campo, (registro_de_campo_id,))
        updated_registro_de_campo_id = cursor.fetchone()

        if updated_registro_de_campo_id is None:
            return jsonify({"error": "Registro de campo not found"}), 404
        
        updated_registro_de_campo_id = updated_registro_de_campo_id['registro_de_campo_id']

        conn.commit()

        return jsonify({"message": f"Caso confirmado com sucesso do degistro de campo com o ID {updated_registro_de_campo_id}."}), 200

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()