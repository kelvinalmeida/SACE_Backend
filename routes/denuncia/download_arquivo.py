from flask import jsonify, current_app, send_from_directory
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import denuncia
import os
import logging
from werkzeug.exceptions import NotFound # <-- 1. IMPORTAR A EXCEÇÃO CORRETA

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

@denuncia.route('/denuncia/arquivo/<int:arquivo_id>', methods=['GET'])
@token_required
def get_arquivo_denuncia(current_user, arquivo_id):
    """
    Busca um arquivo de 'denuncia' pelo ID do arquivo
    e retorna o arquivo para download/visualização.
    """
    # Define o diretório base onde os arquivos de denúncia estão salvos
    directory = os.path.join(current_app.root_path, 'uploads', 'denuncia_arquivos')
    
    conn = None
    cursor = None
    nome_arquivo_no_disco = "[desconhecido]" # Para logs de erro mais claros

    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()

        # 1. Buscar o nome original e o ID da denúncia pai
        query = """
            SELECT arquivo_nome, denuncia_id 
            FROM arquivos_denuncia 
            WHERE arquivo_denuncia_id = %s;
        """
        cursor.execute(query, (arquivo_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Arquivo não encontrado no banco de dados."}), 404

        arquivo_nome_original = result['arquivo_nome']
        denuncia_id = result['denuncia_id']
        
        # 2. Montar o nome do arquivo como ele foi salvo no disco
        nome_arquivo_no_disco = f"denuncia_id_{denuncia_id}_{arquivo_nome_original}"

        # 3. Servir o arquivo
        return send_from_directory(
            directory, 
            nome_arquivo_no_disco, 
            as_attachment=False
        )

    except NotFound: # <-- 2. CAPTURAR A EXCEÇÃO CORRETA
        logging.error(f"Arquivo não encontrado no disco: {nome_arquivo_no_disco} (ID: {arquivo_id})")
        return jsonify({"error": "Arquivo físico não encontrado no servidor."}), 404
    except Exception as e:
        logging.error(f"Erro ao buscar arquivo de denúncia {arquivo_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar arquivo.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()