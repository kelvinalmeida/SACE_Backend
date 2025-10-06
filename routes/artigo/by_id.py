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

        search_artigos = """SELECT art.artigo_id, art.supervisor_id, art.nome_artigo_documento, art.conteudo_artigo_digitado, art.titulo, art.descricao, usu.nome_completo supervisor_nome FROM artigo art INNER JOIN supervisor sup USING(supervisor_id) INNER JOIN usuario usu USING(usuario_id) WHERE art.artigo_id = %s;"""

        cursor.execute(search_artigos, (artigo_id,))
        artigo = cursor.fetchone()


        if not artigo:
            return jsonify({"error": "Artigo não encontrado"}), 404

        
        rquivos = {}

        artigo['arqivos_anexados'] = {
            "documento_anexado": artigo['nome_artigo_documento']
        }

        # return jsonify(artigo), 200
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    try:

        # Buscar documento anexado se ouver
        search_arquivos = """SELECT arquiv.arquivo_artigo_id, arquiv.arquivo_nome, arquiv.artigo_id FROM arquivo_artigo arquiv;"""
        
        cursor.execute(search_arquivos)
        arquivos = cursor.fetchall()


        anexos = [arq for arq in arquivos if arq['artigo_id'] == artigo['artigo_id']]
        for anexo in anexos:
            anexo.pop('artigo_id', None)  # Remove a chave se existir
        artigo['arqivos_anexados']['arquivos'] = anexos
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
        cursor.close()
        return jsonify(artigo), 200
