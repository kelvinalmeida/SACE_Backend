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
    # (PUT geralmente atualiza tudo, então mantemos a checagem)
    check_errors = check_required_filds(['titulo', 'descricao', 'link_artigo'])
    if check_errors:
        return jsonify(check_errors), 400
    
    # 3. Coleta de Dados
    supervisor_id = current_user.get("supervisor_id")
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    link_artigo = request.form.get('link_artigo')
    
    # Pega a nova imagem, se houver
    nova_imagem = request.files.get('imagem')
    
    # Gera data de atualização
    # (Assumindo que sua tabela 'artigo' tem a coluna 'data_atualizacao')
    # data_criacao = datetime.now().strftime('%Y-%m-%d')
    
    # 4. Conexão e Transação
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None 
    
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # 5. Buscar Artigo Antigo (Para autorização e nome da imagem antiga)
        sql_get_old = "SELECT supervisor_id, imagem_nome FROM artigo WHERE artigo_id = %s"
        cursor.execute(sql_get_old, (artigo_id,))
        artigo_existente = cursor.fetchone()

        if not artigo_existente:
            return jsonify({"error": "Artigo não encontrado."}), 404

        # # 6. Validação de "Dono"
        # if artigo_existente['supervisor_id'] != supervisor_id:
        #     return jsonify({"error": "Acesso negado: Você não tem permissão para editar este artigo."}), 403

        imagem_antiga_nome = artigo_existente.get('imagem_nome')
        imagem_nome_para_db = imagem_antiga_nome # Valor padrão

        # 7. Lógica de Substituição de Imagem
        if nova_imagem:
            # Salva a nova imagem
            imagem_nome_para_db = secure_filename(nova_imagem.filename)
            
            # Garanta que a pasta UPLOAD_FOLDER exista
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            
            caminho_nova_imagem = os.path.join(UPLOAD_FOLDER, imagem_nome_para_db)
            nova_imagem.save(caminho_nova_imagem)

            # Deleta a imagem antiga, se ela existir e for diferente da nova
            if imagem_antiga_nome and imagem_antiga_nome != imagem_nome_para_db:
                caminho_antigo = os.path.join(UPLOAD_FOLDER, imagem_antiga_nome)
                if os.path.exists(caminho_antigo):
                    try:
                        os.remove(caminho_antigo)
                    except Exception as e:
                        # Logar o erro, mas não parar a transação
                        print(f"Erro ao deletar imagem antiga: {e}") 


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
            imagem_nome_para_db,
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
            "imagem_nome": imagem_nome_para_db
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Erro ao atualizar o artigo: {str(e)}"}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()