from flask import request, jsonify, Blueprint, current_app, send_from_directory
from db import create_connection
from .bluprint import blu_artigo
import os
import logging

# Configuração básica de log
logging.basicConfig(level=logging.INFO)


@blu_artigo.route('/artigo/img/<int:artigo_id>', methods=['GET'])
def get_img(artigo_id):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None # Inicializa o cursor fora do try
    
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # 1. Buscar o nome da imagem no DB
        search_artigo = """SELECT imagem_nome FROM artigo WHERE artigo_id = %s;"""
        cursor.execute(search_artigo, (artigo_id,))
        artigo = cursor.fetchone() # Usamos fetchone() pois esperamos apenas um resultado
        
        if not artigo or not artigo['imagem_nome']:
            return jsonify({"error": "Imagem do Artigo não encontrada ou não cadastrada"}), 404
        
        imagem_name = artigo['imagem_nome']
        
        # 2. Configurar o caminho do diretório e do arquivo
        # O diretório base onde as imagens estão salvas
        directory = os.path.join(current_app.root_path, 'uploads', 'artigo_img')
        
        # 3. Retornar o arquivo usando send_from_directory
        # Esta função busca o arquivo no diretório especificado e o envia para o cliente.
        return send_from_directory(directory, imagem_name)

    except FileNotFoundError:
        # Erro específico se o arquivo existir no DB mas não no disco
        return jsonify({"error": f"Arquivo '{imagem_name}' não encontrado no servidor."}), 404
        
    except Exception as e:
        # Erro genérico (DB ou outro)
        logging.error(f"Erro ao buscar imagem: {e}")
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

    finally:
        # Fechamento de Conexão e Cursor de forma segura
        if cursor:
            cursor.close()
        if conn:
            conn.close()
