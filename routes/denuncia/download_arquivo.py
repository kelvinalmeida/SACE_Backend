# Import 'redirect' e remova 'send_from_directory' e 'os'
from flask import jsonify, current_app, redirect
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import denuncia
import logging
# 'os' e 'NotFound' não são mais necessários aqui

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

@denuncia.route('/denuncia/arquivo/<int:arquivo_id>', methods=['GET'])
@token_required
def get_arquivo_denuncia(current_user, arquivo_id):
    """
    Busca a URL de um arquivo de 'denuncia' pelo ID
    e redireciona o usuário para a URL do Blob.
    """
    
    conn = None
    cursor = None

    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()

        # 1. Buscar a URL completa que está salva no banco de dados.
        # (O campo 'arquivo_nome' agora armazena a URL completa do blob)
        query = """
            SELECT arquivo_nome 
            FROM arquivos_denuncia 
            WHERE arquivo_denuncia_id = %s;
        """
        cursor.execute(query, (arquivo_id,))
        result = cursor.fetchone()

        # 2. Verificar se a URL foi encontrada
        if not result or not result.get('arquivo_nome'):
            return jsonify({"error": "Arquivo não encontrado no banco de dados."}), 404

        # O campo 'arquivo_nome' contém a URL completa
        arquivo_url_no_blob = result['arquivo_nome']
        
        # 3. Redirecionar o usuário para a URL do Blob
        # O navegador do usuário cuidará de exibir a imagem/arquivo.
        return redirect(arquivo_url_no_blob)

    except Exception as e:
        logging.error(f"Erro ao buscar URL do arquivo de denúncia {arquivo_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar arquivo.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()