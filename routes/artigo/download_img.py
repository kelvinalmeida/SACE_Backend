import logging
from flask import request, jsonify, Blueprint, current_app, redirect
from db import create_connection
from .bluprint import blu_artigo
# 'os' e 'send_from_directory' não são mais necessários

# Configuração básica de log
logging.basicConfig(level=logging.INFO)


@blu_artigo.route('/artigo/img/<int:artigo_id>', methods=['GET'])
def get_img(artigo_id):
    """
    Busca a URL da imagem de um artigo pelo ID
    e redireciona o usuário para a URL do Blob.
    """
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None # Inicializa o cursor fora do try
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # 1. Buscar a URL da imagem no DB (o campo 'imagem_nome' agora armazena a URL)
        search_artigo = """SELECT imagem_nome FROM artigo WHERE artigo_id = %s;"""
        cursor.execute(search_artigo, (artigo_id,))
        artigo = cursor.fetchone()
        
        # 2. Verificar se a URL foi encontrada
        if not artigo or not artigo.get('imagem_nome'):
            return jsonify({"error": "Imagem do Artigo não encontrada ou não cadastrada"}), 404
        
        imagem_url = artigo['imagem_nome']
        
        # 3. Redirecionar o usuário para a URL do Blob
        # O navegador do usuário cuidará de exibir a imagem.
        return redirect(imagem_url)
        
    except Exception as e:
        # Erro genérico (DB ou outro)
        logging.error(f"Erro ao buscar URL da imagem do artigo {artigo_id}: {e}", exc_info=True)
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

    finally:
        # Fechamento de Conexão e Cursor de forma segura
        if cursor:
            cursor.close()
        if conn:
            conn.close()