import logging # 1. Adicionado import de logging
from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from .bluprint import denuncia
from datetime import datetime
from vercel_blob import delete # 2. Adicionado import do 'delete' do blob

# Configuração de log
logging.basicConfig(level=logging.INFO)

# A função check_required_filds não é usada em um DELETE, pode ser removida
# def check_required_filds(required_fild):
#     ...

@denuncia.route('/denuncia/<int:denuncia_id>', methods=['DELETE'])
@token_required
def delete_denuncia(current_user, denuncia_id):

    if(current_user["nivel_de_acesso"] not in ["supervisor"]):
        return jsonify({"error": "Invalid token: É nescessário ser supervisor para cadastrar denuncia."}), 403

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    urls_para_deletar = [] # Lista para guardar as URLs

    try:
        cursor = conn.cursor()
        
        # --- ETAPA 1: Buscar as URLs dos arquivos ANTES de deletar a denúncia ---
        # (O campo 'arquivo_nome' agora armazena a URL completa do blob)
        search_urls_query = """
            SELECT arquivo_nome 
            FROM arquivos_denuncia 
            WHERE denuncia_id = %s;
        """
        cursor.execute(search_urls_query, (denuncia_id,))
        arquivos = cursor.fetchall()
        
        # Guarda as URLs que não são nulas
        urls_para_deletar = [arquivo['arquivo_nome'] for arquivo in arquivos if arquivo.get('arquivo_nome')]

        
        # --- ETAPA 2: Deletar a denúncia do banco de dados ---
        # (Isso irá acionar o ON DELETE CASCADE e limpar a tabela arquivos_denuncia)
        delete_query = "DELETE FROM denuncia WHERE denuncia_id = %s RETURNING denuncia_id;"
        cursor.execute(delete_query, (denuncia_id,))
        result = cursor.fetchone()

        if result is None:
            conn.rollback() # Desfaz a busca (embora não seja crítico)
            return jsonify({"error": "Denúncia não encontrada"}), 404
        

        # --- ETAPA 3: Deletar os arquivos do Vercel Blob ---
        if urls_para_deletar:
            try:
                # A função delete() do vercel-blob aceita uma lista de URLs
                delete(urls_para_deletar)
                logging.info(f"Arquivos do Blob deletados com sucesso para denuncia_id: {denuncia_id}")
            except Exception as e_blob:
                # Se a deleção do blob falhar, apenas registramos o aviso.
                # Não devemos reverter a exclusão do banco de dados por causa disso,
                # pois o registro principal foi removido.
                logging.warning(f"Falha ao deletar arquivos do blob para denuncia_id {denuncia_id}: {e_blob}")
        
        
        # --- ETAPA 4: Commit da transação do banco de dados ---
        conn.commit()

        
    except Exception as e:
        if conn: conn.rollback()
        logging.error(f"Erro ao deletar denúncia {denuncia_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    return jsonify({
        "message": "Denúncia e arquivos associados deletados com sucesso",
        "denuncia_id": denuncia_id
     }), 200