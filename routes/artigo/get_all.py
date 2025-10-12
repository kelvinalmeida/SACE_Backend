from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import blu_artigo


@blu_artigo.route('/artigo', methods=['GET'])
def get_artigo():
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        search_artigos = """SELECT artigo.artigo_id, artigo.supervisor_id, artigo.link_artigo, artigo.titulo, artigo.descricao, artigo.data_criacao , artigo.imagem_nome, usu.nome_completo supervisor_nome FROM artigo INNER JOIN supervisor USING(supervisor_id) INNER JOIN usuario usu USING(usuario_id);"""

        cursor.execute(search_artigos)
        all_artigos = cursor.fetchall()

        # return jsonify(all_artigos), 200
        return f"{all_artigos}", 200
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
        cursor.close()
        return jsonify(all_artigos), 200
