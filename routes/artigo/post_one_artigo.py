from flask import request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
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
    check_errors = check_required_filds(['titulo', 'descricao'])
    if check_errors:
        return jsonify(check_errors), 400
    
    # 3. Coleta de Dados
    supervisor_id = current_user.get("supervisor_id")
    conteudo_artigo_digitado = request.form.get('conteudo_artigo_digitado', None)
    titulo = request.form.get('titulo')
    descricao = request.form.get('descricao')
    arqivos_anexados = {}
    count = 1

    documento = request.files.get('artigo_documento') # Documento DOC/PDF (opcional)
    
    # Prepara o nome do documento (None se não houver arquivo)
    nome_artigo_documento = secure_filename(documento.filename) if documento else None
    arqivos_anexados["Artigo Documento"] = nome_artigo_documento

    # 4. Conexão com o Banco de Dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None # Inicializamos o cursor fora do try
    
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()

        # 5. Inserir Artigo Principal (Tabela: artigo)
        inserir_artigo_sql = """
            INSERT INTO artigo(supervisor_id, nome_artigo_documento, conteudo_artigo_digitado, titulo, descricao)
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING artigo_id;
        """
        
        cursor.execute(inserir_artigo_sql, (supervisor_id, nome_artigo_documento, conteudo_artigo_digitado, titulo, descricao))
        artigo_id = cursor.fetchone()['artigo_id']

        # 6. Salvar e Registrar Documento Principal (Se houver)
        if documento:
            documento_filepath = f'uploads/artigo_documentos/artigo_id_{artigo_id}_{nome_artigo_documento}'
            # Certifique-se de que a pasta existe antes de salvar
            # (Não implementado aqui, mas é crucial em produção)
            documento.save(documento_filepath)
        
        # 7. Inserir Fotos ou Vídeos (Tabela: arquivo_artigo)
        arquivos_media = request.files.getlist('files')
        
        if arquivos_media:
            inserir_arquivos_sql = """
                INSERT INTO arquivo_artigo(artigo_id, arquivo_nome) 
                VALUES (%s, %s);
            """
            for file in arquivos_media:
                if file.filename:
                    arquivo_nome = secure_filename(file.filename)
                    arqivos_anexados[f"Arquivo {count}"] = arquivo_nome
                    count = count + 1
                    # Salva o arquivo no sistema de arquivos
                    file.save(f'uploads/artigo_arquivos/artigo_id_{artigo_id}_{arquivo_nome}')
                    
                    # Registra no banco de dados
                    cursor.execute(inserir_arquivos_sql, (artigo_id, arquivo_nome))
        
        # 8. Commit final (se tudo acima for bem-sucedido)
        conn.commit()
        
        return jsonify({
            "message": "Artigo e arquivos anexados criados com sucesso.",
            "titulo": titulo,
            "descricao": descricao,
            "conteudo_artigo_digitado": conteudo_artigo_digitado,
            "artigo_id": artigo_id,
            "arqivos_anexados": arqivos_anexados
        }), 201

    except Exception as e:
        # 9. Rollback e Tratamento de Erro
        # Garante que, se algo falhar (DB ou salvamento de arquivo), 
        # a transação do DB seja revertida.
        if conn:
            conn.rollback()
        # logging.error é útil aqui
        return jsonify({"error": f"Erro ao processar o artigo: {str(e)}"}), 500
    
    finally:
        # 10. Fechamento de Conexão e Cursor
        if cursor:
            cursor.close()
        if conn:
            conn.close()
