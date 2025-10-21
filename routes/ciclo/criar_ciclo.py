from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from datetime import datetime
from .bluprint import ciclos
import logging


logging.basicConfig(level=logging.INFO)

@ciclos.route('/criar_ciclo', methods=['POST'])
@token_required
def criar_ciclo(current_user):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # Buscar ciclo_id do ciclo e ano fornecido
    try:
        cursor = conn.cursor()

        search_all_cicles = """SELECT ciclo_id, ciclo, EXTRACT(YEAR FROM ano_de_criacao)::INTEGER AS ano FROM ciclos"""

        inserir_ciclo = """INSERT INTO ciclos (supervisor_id, ano_de_criacao, encerramento, ativo, ciclo) VALUES (%s, %s, %s, %s, %s);"""

        cursor.execute(search_all_cicles)
        all_ciclos = cursor.fetchall()


        ano_do_ciclo_anterior = all_ciclos[-1]['ano']
        ciclo_anterior = all_ciclos[-1]['ciclo']
        id_ciclo_anterior = all_ciclos[-1]['ciclo_id']

        current_datetime = datetime.now()
        current_year = current_datetime.year


        ciclo = ciclo_anterior + 1
    
        if(ano_do_ciclo_anterior != current_year):
            ciclo = 1

        return jsonify({
            "ciclo": ciclo,
            "ano": current_year,
            "id_ciclo_anterior": id_ciclo_anterior
        })
        
        

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
    
    