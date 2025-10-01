from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from bluprint import area_para_visita


@area_para_visita.route('/area_de_visita', methods=['GET'])
@token_required
def listar_areas_de_visita(current_user):
    
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        supervisor_id = current_user.get("supervisor_id")

        print("supervisor_id:", supervisor_id)

        search_areas = """SELECT area_de_visita_id, cep, setor, numero_quarteirao, estado, municipio, bairro, logadouro FROM area_de_visita;"""

        cursor.execute(search_areas)
        areas = cursor.fetchall()

        return jsonify(areas), 200
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            conn.close()