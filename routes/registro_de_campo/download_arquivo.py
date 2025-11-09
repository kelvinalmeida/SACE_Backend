from flask import jsonify, current_app, send_from_directory
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo
import os
import logging
from werkzeug.exceptions import NotFound # <-- 1. IMPORTAR A EXCEÇÃO CORRETA

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

@registro_de_campo.route('/registro_de_campo/arquivo/<int:arquivo_id>', methods=['GET'])
@token_required
def get_arquivo_registro(current_user, arquivo_id):
    """
    Busca um arquivo de 'registro_de_campo' pelo ID do arquivo
    e retorna o arquivo para download/visualização.
    """
    # Define o diretório base onde os arquivos de registro estão salvos
    directory = os.path.join(current_app.root_path, 'uploads', 'registro_de_campo_arquivos')
    
    conn = None
    cursor = None
    nome_arquivo_no_disco = "[desconhecido]" # Para logs de erro mais claros
    
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()

        # 1. Buscar o nome original e o ID do registro pai
        query = """
            SELECT arquivo_nome, registro_de_campo_id 
            FROM registro_de_campo_arquivos 
            WHERE registro_de_campo_arquivo_id = %s;
        """
        cursor.execute(query, (arquivo_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Arquivo não encontrado no banco de dados."}), 404

        arquivo_nome_original = result['arquivo_nome']
        registro_id = result['registro_de_campo_id']
        
        # 2. Montar o nome do arquivo como ele foi salvo no disco
        # (Conforme a lógica em post_one_registro_de_campo.py)
        nome_arquivo_no_disco = f"reg_de_campo_id_{registro_id}_{arquivo_nome_original}"

        # 3. Servir o arquivo
        return send_from_directory(
            directory, 
            nome_arquivo_no_disco, 
            as_attachment=False # False = tenta exibir no navegador
        )

    except NotFound: # <-- 2. CAPTURAR A EXCEÇÃO CORRETA
        logging.error(f"Arquivo não encontrado no disco: {nome_arquivo_no_disco} (ID: {arquivo_id})")
        return jsonify({"error": "Arquivo físico não encontrado no servidor."}), 404
    except Exception as e:
        logging.error(f"Erro ao buscar arquivo de registro {arquivo_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar arquivo.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()