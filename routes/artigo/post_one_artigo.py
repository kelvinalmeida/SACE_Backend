from flask import request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from datetime import datetime # Importação adicionada para a data
# from .bluprint import blu_artigo # Assumindo que você definirá o Blueprint em um arquivo de módulo
# Importamos o Blueprint a partir do próprio arquivo, ou você pode ajustá-lo
from .bluprint import blu_artigo
# Se você já tem um arquivo bluprint.py, a importação original deve ser restaurada.


def check_required_filds(required_filds):
    """Verifica se todos os campos obrigatórios estão presentes no form."""
    for field in required_filds:
        if field not in request.form or not request.form[field] or request.form[field].strip() == "":
            return {"error": f"Campo obrigatório '{field}' faltando."}
    return None


@blu_artigo.route('/artigo', methods=['POST'])
@token_required
def send_artigo(current_user):

    # 1. Validação de Acesso
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: É necessário ser supervisor para cadastrar artigos."}), 403
    
    # 2. Validação de Campos Obrigatórios
    # REMOVIDO: 'data_criacao'
    check_errors = check_required_filds(['titulo', 'descricao', 'link_artigo'])
    if check_errors:
        return jsonify(check_errors), 400
    
    # 3. Coleta de Dados
    supervisor_id = current_user.get("supervisor_id")
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    link_artigo = request.form.get('link_artigo')
    
    # NOVO: Gera a data de criação atual no formato 'YYYY-MM-DD'
    data_criacao = datetime.now().strftime('%Y-%m-%d')
    
    imagem_artigo = request.files.get('imagem')
    count = 1
    
    
    # 4. Conexão com o Banco de Dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None # Inicializamos o cursor fora do try
    
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()

        # 5. Inserir Artigo Principal (Tabela: artigo)
        # SQL: Inclui a coluna 'data_criacao' no INSERT
        inserir_artigo_sql = """
            INSERT INTO artigo(supervisor_id, imagem_nome, link_artigo, titulo, descricao, data_criacao)
            VALUES (%s, %s, %s, %s, %s, %s) 
            RETURNING artigo_id;
        """
        
        # Inserir imagem do artigo, se fornecida
        if imagem_artigo:
            imagem_nome = secure_filename(imagem_artigo.filename)
            # Salvar a imagem aqui (garanta que a pasta 'uploads/artigo_img/' exista)
            imagem_artigo.save(f"uploads/artigo_img/{imagem_nome}")
        else:
            imagem_nome = None

        
        # Executa a inserção com a data gerada pelo Python
        cursor.execute(inserir_artigo_sql, (supervisor_id, imagem_nome, link_artigo, titulo, descricao, data_criacao))
        artigo_id = cursor.fetchone()['artigo_id']
            
        # Commit final (se tudo acima for bem-sucedido)
        conn.commit()
        
        return jsonify({
            "message": "Artigo e arquivos anexados criados com sucesso.",
            "titulo": titulo,
            "descricao": descricao,
            "link_artigo": link_artigo,
            "artigo_id": artigo_id,
            "imagem_nome": imagem_nome,
            "data_criacao": data_criacao # Retorna a data gerada para confirmação
        }), 201

    except Exception as e:
        # 9. Rollback e Tratamento de Erro
        if conn:
            conn.rollback()
        return jsonify({"error": f"Erro ao processar o artigo: {str(e)}"}), 500
    
    finally:
        # 10. Fechamento de Conexão e Cursor
        if cursor:
            cursor.close()
        if conn:
            conn.close()
