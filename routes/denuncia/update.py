from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from .bluprint import denuncia
from datetime import datetime


def check_required_filds(required_fild):
    for fild in required_fild:
        if fild not in request.form or request.form[fild] is None or request.form[fild].strip() == "":
            return {"error": f"{fild} is required"}
    return False


@denuncia.route('/denuncia/<int:denuncia_id>', methods=['PUT'])
@token_required
def update_denuncia(current_user, denuncia_id):

    # print("current_user token data:", current_user)
    # Pega o agente_id do token

    if(current_user["nivel_de_acesso"] not in ["supervisor"]):
        return jsonify({"error": "Invalid token: É nescessário ser supervisor para cadastrar denuncia."}), 403
    


    check_filds = check_required_filds(['tipo_imovel', 'bairro', 'numero', 'rua_avenida'])

    if(check_filds):
        return jsonify(check_filds), 400
    
    # denuncia_id          | integer                |           | not null | generated always as identity
    # supervisor_id        | integer                |           |          |
    # deposito_id          | integer                |           |          |
    # rua_avenida          | character varying(100) |           | not null |
    # numero               | smallint               |           | not null |
    # bairro               | character varying(50)  |           | not null |
    # tipo_imovel          | character varying(100) |           | not null |
    # endereco_complemento | character varying(200) |           |          |
    # data_denuncia        | date                   |           |          |
    # hora_denuncia        | time without time zone |           |          |
    # observacoes          | character varying(255) |           |          |

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
    status = 'Em Análise'
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
    

    # try:
    #     a1 = int(request.form.get('a1'))
    #     a2 = int(request.form.get('a2'))
    #     b = int(request.form.get('b'))
    #     c = int(request.form.get('c'))
    #     d1 = int(request.form.get('d1'))
    #     d2 = int(request.form.get('d2'))
    #     e = int(request.form.get('e'))
    # except (TypeError, ValueError):
    #     return jsonify({"error": "Invalid input for a1, a2, b, c, d1, d2, or e. They must be integers."}), 400
    

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # # Inserir Depósito
    # try:
    #     
    #     insir_deposito = """
    #         INSERT INTO depositos(a1, a2, b, c, d1, d2, e) 
    #         VALUES (%s, %s, %s, %s, %s, %s, %s) 
    #         RETURNING deposito_id; 
    #     """

    #     # 1. Executa a inserção e a requisição do ID
    #     # O comando 'execute' retorna None, não o resultado.
    #     cursor.execute(insir_deposito, (a1, a2, b, c, d1, d2, e))

    #     # 2. Usa fetchone() para obter a linha de resultado (que contém o ID)
    #     # Como RETURNING retorna uma única linha com uma única coluna (deposito_id),
    #     # fetchone() retorna uma tupla ou lista, dependendo do driver.
    #     resultado = cursor.fetchone()

    #     # 4. Extrai o ID
    #     if resultado:
    #         deposito_id = resultado["deposito_id"]
    #     else:
    #         conn.rollback()
    #         raise Exception("Falha ao obter o ID do depósito após a inserção.")
    # except Exception as e:
    #     conn.rollback()
    #     return jsonify({"error": str(e)}), 500
    

    #Inserir Registro de Campo
    try:
        cursor = conn.cursor()

        update_denuncia = """
            UPDATE denuncia 
            SET supervisor_id = %s,
                rua_avenida = %s,
                numero = %s,
                bairro = %s,
                tipo_imovel = %s,
                endereco_complemento = %s,
                data_denuncia = %s,
                hora_denuncia = %s,
                observacoes = %s,
                status = %s,
                agente_responsavel_id = %s
            WHERE denuncia_id = %s
            RETURNING denuncia_id;"""
        
        cursor.execute(update_denuncia, (supervisor_id, rua_avenida, numero, bairro, tipo_imovel, endereco_complemento, data_denuncia, hora_denuncia, observacoes, status, agente_responsavel_id, denuncia_id))

        resultado = cursor.fetchone()

        if not resultado:
            conn.rollback()
            return jsonify({"error": "Denúncia não encontrada com o ID especificado."}), 404


    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    

    # Inserir Arquivos
    try:

        files = {}
        count = 1
        for file in request.files.getlist('files'):
            files[f"Arquivo {count}"] = secure_filename(file.filename)
            count += 1

            arquivo_nome = secure_filename(file.filename)

            inserir_arquivos = """INSERT INTO arquivos_denuncia(arquivo_nome, denuncia_id) VALUES (%s, %s);""" 

            print("inserir_arquivos: ", arquivo_nome, denuncia_id)

            cursor.execute(inserir_arquivos, (arquivo_nome, denuncia_id))

            file.save(f'uploads/denuncia_arquivos/denuncia_id_{denuncia_id}_{arquivo_nome}')
        
        
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()
        cursor.close()


    return jsonify({
        'status': 'success',
        'message': 'Denuncia atualizada com sucesso',
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




    

