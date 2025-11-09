import logging # 1. Adicionado import de logging
from flask import request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from datetime import datetime
from .bluprint import blu_artigo
from vercel_blob import delete # 2. Adicionado import do 'delete' do blob

# 3. Importações de 'os' e 'UPLOAD_FOLDER' removidas (não são mais necessárias)

# Configuração de log
logging.basicConfig(level=logging.INFO)


@blu_artigo.route('/artigo/<int:artigo_id>', methods=['DELETE'])
@token_required
def delete_artigo(current_user, artigo_id):

    # 1. Validação de Nível de Acesso
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: É necessário ser supervisor para deletar artigos."}), 403

    # 2. Conexão e Transação
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None
    
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    url_para_deletar = None # Variável para guardar a URL

    try:
        cursor = conn.cursor()

        # 3. Buscar Artigo (Para pegar a URL da imagem antiga)
        # (O campo 'imagem_nome' agora armazena a URL completa do blob)
        sql_get_artigo = "SELECT supervisor_id, imagem_nome FROM artigo WHERE artigo_id = %s"
        cursor.execute(sql_get_artigo, (artigo_id,))
        artigo = cursor.fetchone()

        if not artigo:
            return jsonify({"error": "Artigo não encontrado."}), 404

        # 5. Pegar a URL do arquivo para deletar
        url_para_deletar = artigo.get('imagem_nome')

        # 6. Deletar o registro do Banco de Dados
        sql_delete = "DELETE FROM artigo WHERE artigo_id = %s"
        cursor.execute(sql_delete, (artigo_id,))

        # 7. Deletar o arquivo físico (imagem) do Blob
        if url_para_deletar:
            try:
                # A função delete() do vercel-blob aceita a URL completa
                delete(url_para_deletar)
                logging.info(f"Imagem do Blob deletada com sucesso: {url_para_deletar}")
            except Exception as e_blob:
                # Se falhar em deletar o arquivo do blob, apenas registramos o aviso.
                # A transação do DB não deve ser revertida por isso.
                logging.warning(f"Falha ao deletar imagem do blob ({url_para_deletar}): {e_blob}")

        # 8. Commit final (somente após as operações de DB)
        conn.commit()

        return jsonify({
            "message": "Artigo e imagem associada foram deletados com sucesso.",
            "artigo_id_deletado": artigo_id
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Erro ao deletar o artigo: {e}", exc_info=True)
        return jsonify({"error": f"Erro ao deletar o artigo: {str(e)}"}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()