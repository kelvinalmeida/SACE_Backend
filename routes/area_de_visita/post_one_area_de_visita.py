from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import area_para_visita

@area_para_visita.route('/area_de_visita', methods=['POST'])
@token_required
def criar_area_de_visita(current_user):
    print("current_user:", current_user)
    if not current_user or current_user.get("supervisor_id") == None or current_user.get("nivel_de_acesso") not in ["supervisor"]: 
        return jsonify({"error": "É nescessário ser supervisor!"}), 403
    
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        supervisor_id = current_user.get("supervisor_id")
        print("supervisor_id:", supervisor_id)

        cep = request.form.get('cep')
        setor = request.form.get('setor')

        try:
            numero_quarteirao = int(request.form.get('numero_quarteirao'))
        except (TypeError, ValueError):
            return jsonify({"error": "Número do quarteirão inválido"}), 400

        estado = request.form.get('estado')
        municipio = request.form.get('municipio')
        bairro = request.form.get('bairro')
        logadouro = request.form.get('logadouro')

        insert_area = """INSERT INTO area_de_visita (supervisor_id, cep, setor, numero_quarteirao, estado, municipio, bairro, logadouro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING area_de_visita_id;"""

        cursor.execute(insert_area, (supervisor_id, cep, setor, numero_quarteirao, estado, municipio, bairro, logadouro))
        area_de_visita_id = cursor.fetchone()["area_de_visita_id"]
        conn.commit()

        return jsonify({
            "message": "Área de visita criada com sucesso", 
            "area_de_visita_id": area_de_visita_id,
            "supervisor_id": supervisor_id,
            }), 201
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()
            conn.close()