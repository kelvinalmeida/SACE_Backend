from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import area_para_visita

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

        search_area = """SELECT area_de_visita_id, cep, setor, numero_quarteirao, estado, municipio, status, bairro, logadouro FROM area_de_visita WHERE area_de_visita_id = %s;"""

        cursor.execute(search_area, (area_de_visita_id,))
        area = cursor.fetchone()

        if area is None:
            return jsonify({"error": "Área de visita não encontrada"}), 404

        # return jsonify(area), 200
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500
    
    try:
        search_agentes = """SELECT * FROM agente_area_de_visita INNER JOIN agente USING(agente_id) INNER JOIN usuario USING(usuario_Id);"""

        cursor.execute(search_agentes)
        agentes = cursor.fetchall()

        # Mapear agentes para suas respectivas áreas
        area_to_agentes = {}
        for agente in agentes:
            area_id = agente['area_de_visita_id']
            if area_id not in area_to_agentes:
                area_to_agentes[area_id] = []
            area_to_agentes[area_id].append({
                "agente_id": agente['agente_id'],
                "nome": agente['nome_completo'],
                "situacao_atual": agente['situacao_atual'] 
            })

        # Adicionar agentes às áreas correspondentes
        
        area_id = area['area_de_visita_id']
        area['agentes'] = area_to_agentes.get(area_id, [])


        return jsonify(area), 200
    
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            conn.close()