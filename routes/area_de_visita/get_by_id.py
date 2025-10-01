from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from bluprint import area_para_visita

@area_para_visita.route('/area_de_visita/<int:area_de_visita_id>', methods=['GET'])
@token_required
def obter_area_de_visita(current_user, area_de_visita_id):
    
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        supervisor_id = current_user.get("supervisor_id")

        print("supervisor_id:", supervisor_id)
        print("area_de_visita_id:", area_de_visita_id)

        search_area = """SELECT area_de_visita_id, cep, setor, numero_quarteirao, estado, municipio, bairro, logadouro FROM area_de_visita WHERE area_de_visita_id = %s;"""

        cursor.execute(search_area, (area_de_visita_id,))
        area = cursor.fetchone()

        if area is None:
            return jsonify({"error": "Área de visita não encontrada"}), 404

        return jsonify(area), 200
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            conn.close()