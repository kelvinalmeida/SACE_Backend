from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import blu_artigo


@blu_artigo.route('/artigo/<int:artigo_id>', methods=['GET'])
@token_required
def get_artigo_by_id(current_user, artigo_id):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        search_artigos = """SELECT artigo.artigo_id, artigo.supervisor_id, artigo.link_artigo, artigo.titulo, artigo.descricao, artigo.imagem_nome, usu.nome_completo supervisor_nome FROM artigo INNER JOIN supervisor USING(supervisor_id) INNER JOIN usuario usu USING(usuario_id) WHERE artigo_id = %s;"""

        cursor.execute(search_artigos, (artigo_id,))
        artigo = cursor.fetchone()

        if artigo is None:
            return jsonify({"error": "Artigo not found"}), 404

        return jsonify(artigo), 200
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
        cursor.close()
