from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import blu_artigo


@blu_artigo.route('/artigo', methods=['GET'])
@token_required
def get_artigo(current_user):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        search_artigos = """SELECT artigo.artigo_id, artigo.supervisor_id, artigo.nome_artigo_documento, artigo.conteudo_artigo_digitado, artigo.titulo, artigo.descricao, usu.nome_completo supervisor_nome FROM artigo INNER JOIN supervisor USING(supervisor_id) INNER JOIN usuario usu USING(usuario_id);"""

        cursor.execute(search_artigos)
        all_artigos = cursor.fetchall()

        arquivos = {}
        
        for art in all_artigos:
            art['arqivos_anexados'] = {
                "documento_anexado": art['nome_artigo_documento']
            }

    
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    try:

        # Buscar documento anexado se ouver
        search_arquivos = """SELECT arquiv.arquivo_artigo_id, arquiv.arquivo_nome, arquiv.artigo_id FROM arquivo_artigo arquiv;"""
        
        cursor.execute(search_arquivos)
        arquivos = cursor.fetchall()

        for art in all_artigos:
            anexos = [arq for arq in arquivos if arq['artigo_id'] == art['artigo_id']]
            for anexo in anexos:
                anexo.pop('artigo_id', None)  # Remove a chave se existir
            art['arqivos_anexados']['arquivos'] = anexos
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
        cursor.close()
        return jsonify(all_artigos), 200
