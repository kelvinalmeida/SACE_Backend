import logging
from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from .bluprint import denuncia
from datetime import datetime
from vercel_blob import put




def check_required_filds(required_fild):
    for fild in required_fild:
        if fild not in request.form or request.form[fild] is None or request.form[fild].strip() == "":
            return {"error": f"{fild} is required"}
    return False


@denuncia.route('/denuncia', methods=['POST'])
@token_required
def create_denuncia(current_user):

    # print("current_user token data:", current_user)
    # Pega o agente_id do token

    if(current_user["nivel_de_acesso"] not in ["supervisor"]):
        return jsonify({"error": "Invalid token: É nescessário ser supervisor para cadastrar denuncia."}), 403
    


    check_filds = check_required_filds(['tipo_imovel', 'bairro', 'numero', 'rua_avenida'])

    if(check_filds):
        return jsonify(check_filds), 400
    

    supervisor_id = current_user["supervisor_id"]
    rua_avenida = request.form.get('rua_avenida')

    try:
        numero = int(request.form.get('numero'))
    except Exception:
        return jsonify({"error: numero da residência com formato incorreto."}), 400

    bairro = request.form.get('bairro')
    tipo_imovel = request.form.get('tipo_imovel')
    endereco_complemento = request.form.get('endereco_complemento')
    observacoes = request.form.get('observacoes')
    status = 'Pendente'
    agente_responsavel_id = request.form.get('agente_responsavel_id', None)

    data_denuncia = request.form.get('data_denuncia')
    hora_denuncia = request.form.get('hora_denuncia')

    # 2. Validar a data_denuncia
    if data_denuncia: # Apenas validar se o campo foi enviado
        try:
            # Tenta converter a string para um objeto de data no formato AAAA-MM-DD
            # Se o formato for diferente (ex: DD/MM/AAAA), a conversão falhará
            datetime.strptime(data_denuncia, '%Y-%m-%d')
        except ValueError:
            # Se a conversão falhar, retorna um erro claro para o cliente
            return jsonify({
                "error": "Formato de data inválido. Por favor, use o formato AAAA-MM-DD."
            }), 400 # 400 Bad Request é o status correto para erro do cliente
    
    # 3. Validar a hora_denuncia
    if hora_denuncia: # Apenas validar se o campo foi enviado
        try:
            # Tenta converter a string para um objeto de hora no formato HH:MM:SS
            datetime.strptime(hora_denuncia, '%H:%M:%S')
        except ValueError:
            return jsonify({
                "error": "Formato de hora inválido. Por favor, use o formato HH:MM:SS (24 horas)."
            }), 400
    

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    
    #Inserir Registro de Campo
    try:
        cursor = conn.cursor()

        inserir_denuncia = """INSERT INTO denuncia(
            supervisor_id, rua_avenida, numero, bairro, tipo_imovel, endereco_complemento, data_denuncia, hora_denuncia, observacoes, status, agente_responsavel_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING denuncia_id; """
        
        cursor.execute(inserir_denuncia, (supervisor_id, rua_avenida, numero, bairro, tipo_imovel, endereco_complemento, data_denuncia, hora_denuncia, observacoes, status, agente_responsavel_id))

        denuncia_fech = cursor.fetchone()
        denuncia_id = denuncia_fech['denuncia_id']

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    

    # Inserir Arquivos
    try:
        files = {}
        count = 1
        for file in request.files.getlist('files'):
            arquivo_nome = secure_filename(file.filename)
            # Define o caminho/nome do arquivo no Vercel Blob
            nome_no_blob = f"denuncia_arquivos/denuncia_id_{denuncia_id}_{arquivo_nome}"

            try:
                # CORREÇÃO: 'nome_no_blob' é o primeiro argumento, sem 'pathname='
                blob = put(
                    nome_no_blob,    # 1º argumento: O nome/caminho do arquivo no blob
                    file.read(),     # 2º argumento: O conteúdo do arquivo (sem keyword)
                    options={'access': 'public', 'allowOverwrite': True}
                )

                # Salva a URL completa retornada pelo blob
                url_para_db = blob['url']

            except Exception as e:
                conn.rollback()
                logging.error(f"Falha ao salvar arquivo no storage: {e}", exc_info=True)
                return jsonify({"error": f"Falha ao salvar arquivo no storage: {str(e)}"}), 500

            # Salva a URL no banco de dados
            inserir_arquivos = """INSERT INTO arquivos_denuncia(arquivo_nome, denuncia_id) VALUES (%s, %s);""" 
            cursor.execute(inserir_arquivos, (url_para_db, denuncia_id))

            files[f"Arquivo {count}"] = url_para_db
            count += 1
        
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()
        cursor.close()


    return jsonify({
        'status': 'success',
        'message': 'Denuncia recebida com sucesso',
        'data': {
            'denuncia_id': denuncia_id,
            'supervisor_id': supervisor_id,
            'rua_avenida': rua_avenida,
            'numero': numero,
            'bairro': bairro,
            'tipo_imovel': tipo_imovel,
            'endereco_complemento': endereco_complemento,
            'data_denuncia': data_denuncia,
            'hora_denuncia': hora_denuncia,
            'observacoes': observacoes,
            'status': status,
            'agente_responsavel_id': agente_responsavel_id,
            # 'a1': a1,
            # 'a2': a2,
            # 'b': b,
            # 'c': c,
            # 'd1': d1,
            # 'd2': d2,
            # 'e': e,
            # 'deposito_id': deposito_id,
            'files': files
        }
    }), 201




    

