from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import area_para_visita

@area_para_visita.route('/area_de_visita', methods=['DELETE'])
@token_required
def delete_list_of_area_de_visita(current_user):

    if not current_user or current_user.get("supervisor_id") == None or current_user.get("nivel_de_acesso") not in ["supervisor"]: 
        return jsonify({"error": "É nescessário ser supervisor para atualizar alguma área de vísita!"}), 403
    
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        ids = request.json.get('ids', [])
        if not ids or not isinstance(ids, list):
            return jsonify({"error": "Lista de IDs inválida"}), 400

        for area_id in ids:
            cursor.execute("DELETE FROM area_de_visita WHERE area_de_visita_id = %s RETURNING area_de_visita_id;", (area_id,))
            deleted_area = cursor.fetchone()
            if not deleted_area:
                conn.rollback()
                conn.close()
                return jsonify({"error": f"Área de visita com ID {area_id} não encontrada"}), 404

        conn.commit()

        return jsonify({
            "message": f"Areas de visitas com IDs {ids} deletadas com sucesso", 
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