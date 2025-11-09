from flask import Flask, request, jsonify, Blueprint, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo
from vercel_blob import delete # <-- 1. Importar a função 'delete'
import logging # <-- 2. Importar logging para erros

@registro_de_campo.route('/registro_de_campo/<int:registro_de_campo_id>', methods=['DELETE'])
@token_required
def delete_registro_de_campo(current_user, registro_de_campo_id):
    
    conn = None
    cursor = None
    
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor()

        # --- Início da Transação ---
        
        # 1. Obter o 'deposito_id' associado ANTES de deletar o registro principal
        cursor.execute(
            "SELECT deposito_id FROM registro_de_campo WHERE registro_de_campo_id = %s", 
            (registro_de_campo_id,)
        )
        registro = cursor.fetchone()

        if not registro:
            return jsonify({"error": "Registro de campo not found"}), 404
        
        deposito_id = registro['deposito_id']

        # 2. Obter TODAS as URLs de arquivos associadas ANTES de deletar
        cursor.execute(
            "SELECT arquivo_nome FROM registro_de_campo_arquivos WHERE registro_de_campo_id = %s", 
            (registro_de_campo_id,)
        )
        arquivos = cursor.fetchall()
        # Cria uma lista de URLs para deletar do blob
        urls_para_deletar = [arquivo['arquivo_nome'] for arquivo in arquivos]

        # 3. Deletar registros das tabelas "filhas" (respeitando foreign keys)
        cursor.execute("DELETE FROM larvicida WHERE registro_de_campo_id = %s", (registro_de_campo_id,))
        cursor.execute("DELETE FROM adulticida WHERE registro_de_campo_id = %s", (registro_de_campo_id,))
        cursor.execute("DELETE FROM registro_de_campo_arquivos WHERE registro_de_campo_id = %s", (registro_de_campo_id,))
        
        # 4. Deletar o registro "pai"
        cursor.execute("DELETE FROM registro_de_campo WHERE registro_de_campo_id = %s", (registro_de_campo_id,))

        # 5. Deletar o depósito associado (que agora está órfão)
        if deposito_id:
            cursor.execute("DELETE FROM depositos WHERE deposito_id = %s", (deposito_id,))

        # 6. Deletar os arquivos do Vercel Blob
        # Isso é feito DEPOIS das exclusões do DB, mas ANTES do commit.
        # Se isso falhar, o 'except' será acionado e fará o rollback.
        if urls_para_deletar:
            try:
                # A função 'delete' pode receber uma lista de URLs
                delete(urls_para_deletar)
            except Exception as e:
                # Se falhar, registra o erro e levanta uma exceção para acionar o rollback
                logging.error(f"Falha ao deletar arquivos do blob: {e}")
                raise Exception(f"Falha ao deletar arquivos do storage: {str(e)}")

        # 7. Se tudo (DB e Blob) deu certo, faz o commit final
        conn.commit()

        return jsonify({
            "message": f"Registro de campo ID {registro_de_campo_id} e todos os dados/arquivos associados foram deletados com sucesso."
        }), 200

    except Exception as e:
        # Se qualquer passo falhar, reverte TODAS as operações do banco
        if conn: conn.rollback()
        logging.error(f"Erro ao deletar registro {registro_de_campo_id}: {e}", exc_info=True)
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
    
    finally:
        # Sempre fecha a conexão e o cursor
        if cursor: cursor.close()
        if conn: conn.close()