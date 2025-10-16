from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import ciclos
import logging


logging.basicConfig(level=logging.INFO)

@ciclos.route('/anos_ciclos', methods=['GET'])
@token_required
def get_anos_and_ciclos(current_user):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # Buscar ciclo_id do ciclo e ano fornecido
    try:
        cursor = conn.cursor()

        search_ciclo_atual = """SELECT ciclo_id, EXTRACT(YEAR FROM ano_de_criacao)::INTEGER AS ano, ciclo FROM ciclos;"""

        cursor.execute(search_ciclo_atual)
        ciclos = cursor.fetchall()

        if not ciclos:
            return jsonify({"error": "O sistem não tem ciclos" })
        

        ciclos_e_seus_anos = {}

        for ciclo in ciclos:
            ano = ciclo["ano"]
            ciclo = ciclo["ciclo"]
            if ano in ciclos_e_seus_anos:
                ciclos_e_seus_anos[ano].append(ciclo)
            else:
                ciclos_e_seus_anos[ano] = []
                ciclos_e_seus_anos[ano].append(ciclo)


        return jsonify(ciclos_e_seus_anos)
    
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        cursor.close()
        conn.close()
    
    