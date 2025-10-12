from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import area_para_visita

@area_para_visita.route('/area_de_visita/<int:area_de_visita_id>', methods=['PUT'])
@token_required
def update_area_de_visita(current_user, area_de_visita_id):
    # print("current_user:", current_user)
    if not current_user or current_user.get("supervisor_id") == None or current_user.get("nivel_de_acesso") not in ["supervisor"]: 
        return jsonify({"error": "É nescessário ser supervisor para atualizar alguma área de vísita!"}), 403
    
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # area_de_visita_id | integer                |           | not null | generated always as identity
        # supervisor_id     | integer                |           |          |
        # cep               | character varying(10)  |           |          |
        # setor             | character varying(100) |           |          |
        # numero_quarteirao | smallint               |           |          |
        # estado            | character varying(2)   |           |          |
        # municipio         | character varying(100) |           |          |
        # bairro            | character varying(100) |           |          |
        # logadouro         | character varying(100) |           |          |

        supervisor_id = current_user.get("supervisor_id")
        print("supervisor_id:", supervisor_id)

        cep = request.json.get('cep')
        setor = request.json.get('setor')

        try:
            numero_quarteirao = int(request.json.get('numero_quarteirao'))
        except (TypeError, ValueError):
            return jsonify({"error": "Número do quarteirão inválido"}), 400

        estado = request.json.get('estado')
        municipio = request.json.get('municipio')
        bairro = request.json.get('bairro')
        logadouro = request.json.get('logadouro')
        status = request.json.get('status')

        insert_area = """UPDATE area_de_visita SET supervisor_id = %s, cep = %s, setor = %s, numero_quarteirao = %s, estado = %s, municipio = %s, bairro = %s, logadouro = %s, status = %s WHERE area_de_visita_id = %s RETURNING area_de_visita_id;"""

        cursor.execute(insert_area, (supervisor_id, cep, setor, numero_quarteirao, estado, municipio, bairro, logadouro, status, area_de_visita_id))

        area_de_visita_id = cursor.fetchone()
        
        if area_de_visita_id is None:
            return jsonify({"error": f"Área de visita com ID {area_de_visita_id} não encontrada"}), 404

        conn.commit()

        return jsonify({
            "message": "Área de visita atualizada com sucesso", 
            "area_de_visita_id": area_de_visita_id,
            "supervisor_id": supervisor_id,
            }), 200
    
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            conn.close()