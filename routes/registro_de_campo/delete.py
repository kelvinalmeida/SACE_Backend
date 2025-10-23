from flask import Flask, request, jsonify, Blueprint, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo

@registro_de_campo.route('/registro_de_campo/<int:registro_de_campo_id>', methods=['DELETE'])
@token_required
def delete_registro_de_campo(current_user, registro_de_campo_id):
    

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # verificando se existe algum ciclo ativo
    try:
        cursor = conn.cursor()

        delete_registro = """DELETE FROM registro_de_campo WHERE registro_de_campo_id = %s RETURNING registro_de_campo_id;"""
        cursor.execute(delete_registro, (registro_de_campo_id,))
        deleted_id = cursor.fetchone()

        if deleted_id is None:
            return jsonify({"error": "Registro de campo not found"}), 404

        conn.commit()


        return jsonify({"message": f"Registro de campo with ID {deleted_id['registro_de_campo_id']} deleted successfully."}), 200

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()