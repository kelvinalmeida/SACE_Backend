from flask import request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from datetime import datetime
from .bluprint import blu_artigo

# --- NOVAS IMPORTAÇÕES ---
import os
import os.path
# -------------------------

# --- CAMINHO DE UPLOAD (para evitar repetição) ---
# Garanta que esta pasta exista
UPLOAD_FOLDER = "uploads/artigo_img/"
# ------------------------------------------------


@blu_artigo.route('/artigo/<int:artigo_id>', methods=['DELETE'])
@token_required
def delete_artigo(current_user, artigo_id):

    # 1. Validação de Nível de Acesso
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: É necessário ser supervisor para deletar artigos."}), 403

    supervisor_id = current_user.get("supervisor_id")

    # 2. Conexão e Transação
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None
    
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # 3. Buscar Artigo (Para autorização e nome do arquivo)
        sql_get_artigo = "SELECT supervisor_id, imagem_nome FROM artigo WHERE artigo_id = %s"
        cursor.execute(sql_get_artigo, (artigo_id,))
        artigo = cursor.fetchone()

        if not artigo:
            return jsonify({"error": "Artigo não encontrado."}), 404

        # # 4. Validação de "Dono"
        # if artigo['supervisor_id'] != supervisor_id:
        #     return jsonify({"error": "Acesso negado: Você não tem permissão para deletar este artigo."}), 403

        # 5. Pegar o nome do arquivo para deletar
        imagem_nome_para_deletar = artigo.get('imagem_nome')

        # 6. Deletar o registro do Banco de Dados
        sql_delete = "DELETE FROM artigo WHERE artigo_id = %s"
        cursor.execute(sql_delete, (artigo_id,))

        # 7. Deletar o arquivo físico (imagem)
        if imagem_nome_para_deletar:
            caminho_arquivo = os.path.join(UPLOAD_FOLDER, imagem_nome_para_deletar)
            
            if os.path.exists(caminho_arquivo):
                try:
                    os.remove(caminho_arquivo)
                except Exception as e:
                    # Se falhar em deletar o arquivo, fazemos o rollback.
                    # O artigo não será deletado do DB se o arquivo não puder ser removido.
                    # (Uma alternativa é apenas logar o erro e continuar, 
                    # mas isso deixaria um "arquivo órfão")
                    conn.rollback()
                    return jsonify({"error": f"Erro ao deletar o arquivo de imagem: {str(e)}"}), 500
            # else:
                # Opcional: Logar se o arquivo não foi encontrado no disco, 
                # mas o DB será limpo mesmo assim.

        # 8. Commit final
        conn.commit()

        return jsonify({
            "message": "Artigo e arquivo de imagem associado foram deletados com sucesso.",
            "artigo_id_deletado": artigo_id
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Erro ao deletar o artigo: {str(e)}"}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()