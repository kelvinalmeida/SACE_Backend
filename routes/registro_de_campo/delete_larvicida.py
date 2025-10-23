from flask import Flask, request, jsonify, Blueprint, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo

@registro_de_campo.route('/larvicida/<int:larvicida_id>', methods=['DELETE'])
@token_required
def delete_larvicida(current_user, larvicida_id):
    

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # verificando se existe algum ciclo ativo
    try:
        cursor = conn.cursor()

        delete_larvicida = """DELETE FROM larvicida WHERE larvicida_id = %s RETURNING larvicida_id;"""
        cursor.execute(delete_larvicida, (larvicida_id,))
        deleted_id = cursor.fetchone()

        if deleted_id is None:
            return jsonify({"error": "larvicida de campo not found"}), 404

        conn.commit()


        return jsonify({"message": f"larvicida with ID {deleted_id['larvicida_id']} deleted successfully."}), 200

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()