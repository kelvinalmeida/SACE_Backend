import logging  # 1. Adicionado import
from flask import request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from datetime import datetime
from .bluprint import blu_artigo
from vercel_blob import put, delete  # 2. Importado 'put' e 'delete'

# 3. Importações de 'os' e 'UPLOAD_FOLDER' removidas (não são mais necessárias)

# Configuração de log
logging.basicConfig(level=logging.INFO)


def check_required_filds(required_filds):
    """Verifica se todos os campos obrigatórios estão presentes no form."""
    for field in required_filds:
        if field not in request.form or not request.form[field] or request.form[field].strip() == "":
            return {"error": f"Campo obrigatório '{field}' faltando."}
    return None


@blu_artigo.route('/artigo/<int:artigo_id>', methods=['PUT'])
@token_required
def update_artigo(current_user, artigo_id):

    # 1. Validação de Acesso (Supervisor)
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: É necessário ser supervisor para editar artigos."}), 403

    # 2. Validação de Campos Obrigatórios
    check_errors = check_required_filds(['titulo', 'descricao', 'link_artigo'])
    if check_errors:
        return jsonify(check_errors), 400

    # 3. Coleta de Dados
    supervisor_id = current_user.get("supervisor_id")
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    link_artigo = request.form.get('link_artigo')
    nova_imagem = request.files.get('imagem')

    # 4. Conexão e Transação
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # 5. Buscar Artigo Antigo (Para pegar a URL da imagem antiga)
        sql_get_old = "SELECT supervisor_id, imagem_nome FROM artigo WHERE artigo_id = %s"
        cursor.execute(sql_get_old, (artigo_id,))
        artigo_existente = cursor.fetchone()

        if not artigo_existente:
            return jsonify({"error": "Artigo não encontrado."}), 404

        # 'imagem_nome' no DB agora é a URL completa do blob
        url_imagem_antiga = artigo_existente.get('imagem_nome')
        url_imagem_para_db = url_imagem_antiga  # Valor padrão (manter a imagem antiga)

        # 7. Lógica de Substituição de Imagem no Blob
        if nova_imagem:
            # Salva a nova imagem no Blob
            imagem_nome_seguro = secure_filename(nova_imagem.filename)
            nome_no_blob = f"artigo_img/{imagem_nome_seguro}"

            try:
                # Faz o upload da nova imagem
                blob = put(
                    nome_no_blob,
                    nova_imagem.read(),
                    options={'access': 'public', 'allowOverwrite': True},
                )
                # Pega a URL da nova imagem para salvar no DB
                url_imagem_para_db = blob['url']

            except Exception as e:
                conn.rollback()
                logging.error(f"Falha ao salvar NOVA imagem do artigo no storage: {e}", exc_info=True)
                return jsonify({"error": f"Falha ao salvar nova imagem do artigo no storage: {str(e)}"}), 500

            # Se o upload da nova foi bem-sucedido, deleta a imagem antiga do Blob
            if url_imagem_antiga and url_imagem_antiga != url_imagem_para_db:
                try:
                    # A função delete() do vercel-blob recebe a URL completa
                    delete(url_imagem_antiga)
                    logging.info(f"Imagem antiga do blob deletada: {url_imagem_antiga}")
                except Exception as e_del:
                    # Se falhar ao deletar a antiga, apenas registramos o aviso.
                    # A transação principal (atualizar para a nova URL) continua.
                    logging.warning(f"Erro ao deletar imagem antiga do blob ({url_imagem_antiga}): {e_del}")

        # Atualiza o banco de dados com os novos dados e a URL da imagem (nova ou antiga)
        sql_update = """
            UPDATE artigo
            SET 
                titulo = %s,
                descricao = %s,
                link_artigo = %s,
                imagem_nome = %s
            WHERE artigo_id = %s;
        """

        cursor.execute(sql_update, (
            titulo,
            descricao,
            link_artigo,
            url_imagem_para_db,  # Salva a URL correta
            artigo_id
        ))

        # 9. Commit
        conn.commit()

        return jsonify({
            "message": "Artigo atualizado com sucesso.",
            "artigo_id": artigo_id,
            "titulo": titulo,
            "descricao": descricao,
            "link_artigo": link_artigo,
            "imagem_nome": url_imagem_para_db  # Retorna a URL
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Erro ao atualizar o artigo: {e}", exc_info=True)
        return jsonify({"error": f"Erro ao atualizar o artigo: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()