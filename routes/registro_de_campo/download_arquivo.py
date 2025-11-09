# 1. 'redirect' é o novo import principal. 'os' e 'send_from_directory' não são mais necessários.
from flask import jsonify, current_app, redirect
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo
import logging
# 'NotFound' e 'os' não são mais necessários para esta rota
# from werkzeug.exceptions import NotFound 
# import os

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

@registro_de_campo.route('/registro_de_campo/arquivo/<int:arquivo_id>', methods=['GET'])
@token_required
def get_arquivo_registro(current_user, arquivo_id):
    """
    Busca a URL de um arquivo no Vercel Blob pelo ID
    e REDIRECIONA o usuário para essa URL.
    """
    conn = None
    cursor = None
    
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()

        # 1. Buscar a URL completa do blob (que está na coluna 'arquivo_nome')
        query = """
            SELECT arquivo_nome 
            FROM registro_de_campo_arquivos 
            WHERE registro_de_campo_arquivo_id = %s;
        """
        cursor.execute(query, (arquivo_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Arquivo não encontrado no banco de dados."}), 404

        # 2. Obter a URL do resultado
        blob_url = result['arquivo_nome']

        # 3. Redirecionar o usuário para a URL do Vercel Blob
        # O navegador do usuário cuidará de exibir ou baixar o arquivo.
        return redirect(blob_url)

    # A exceção 'NotFound' não é mais necessária, pois não estamos procurando um arquivo local.
    except Exception as e:
        logging.error(f"Erro ao buscar arquivo de registro {arquivo_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar arquivo.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()