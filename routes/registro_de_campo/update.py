from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
import json
from werkzeug.utils import secure_filename
from .bluprint import registro_de_campo


def check_required_filds(required_fild):
    for fild in required_fild:
        if fild not in request.form or request.form[fild] is None or request.form[fild].strip() == "":
            return {"error": f"{fild} is required"}
    return False


@registro_de_campo.route('/registro_de_campo/<int:registro_de_campo_id>', methods=['PUT'])
@token_required
def update_registro_de_campo(current_user, registro_de_campo_id):

    print("current_user token data:", current_user)
    # Pega o agente_id do token
    try:
        agente_id = current_user['agente_id']
    except Exception as e:
        return jsonify({"error": "Invalid token: É nescessário ser agente para cadastrar registro de campo. Peça para um supervisor cadastrar você."}), 401
    
   
    check_filds = check_required_filds(['imovel_numero', 'imovel_lado', 'imovel_categoria_da_localidade', 'imovel_tipo', 'imovel_status'])

    if(check_filds):
        return jsonify(check_filds), 400

    
    imovel_lado = request.form.get('imovel_lado')
    imovel_categoria_da_localidade = request.form.get('imovel_categoria_da_localidade')
    imovel_tipo = request.form.get('imovel_tipo')
    imovel_status = request.form.get('imovel_status')
    imovel_complemento = request.form.get('imovel_complemento')
    formulario_tipo = request.form.get('formulario_tipo')

    try:
        li = request.form.get('li', 'false').lower() == 'true'
        pe = request.form.get('pe', 'false').lower() == 'true'
        t = request.form.get('t', 'false').lower() == 'true'
        df = request.form.get('df', 'false').lower() == 'true'
        pve = request.form.get('pve', 'false').lower() == 'true'

        print ("li, pe, t, df, pve: ", li, pe, t, df, pve)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input for li, pe, t, df, or pve. They must be boolean values."}), 400

    numero_da_amostra = request.form.get('numero_da_amostra')
    observacao = request.form.get('observacao')
    area_de_visita_id = request.form.get('area_de_visita_id')

    try:
        imovel_numero = request.form.get('imovel_numero')
        quantiade_tubitos = request.form.get('quantiade_tubitos')
        a1 = int(request.form.get('a1'))
        a2 = int(request.form.get('a2'))
        b = int(request.form.get('b'))
        c = int(request.form.get('c'))
        d1 = int(request.form.get('d1'))
        d2 = int(request.form.get('d2'))
        e = int(request.form.get('e'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input for imovel_numero, quantiade_tubitos, a1, a2, b, c, d1, d2, or e. They must be integers."}), 400
    

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    

    # verificando se existe algum ciclo ativo
    try:
        cursor = conn.cursor()

        check_ciclos_ativos = """SELECT * FROM ciclos WHERE ativo = True;"""
        cursor.execute(check_ciclos_ativos)
        ciclo_ativo = cursor.fetchone()

        if not ciclo_ativo:
            return jsonify({"error": "É nescessário ter um ciclo ativo! Algum supervisor FINALIZOU UM CICLO e não ativou um novo! Peça para um supervisor criar um novo ciclo!"}), 409

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
    

    # Query para buscar a área de visita do agente logado
    try:
       
        search_agente_area_de_visita = """SELECT area_de_visita_id FROM agente_area_de_visita WHERE agente_id = %s AND area_de_visita_id = %s;"""

        cursor.execute(search_agente_area_de_visita, (agente_id, area_de_visita_id))
        
        area_de_visita_id = cursor.fetchone()

        area_de_visita_id = area_de_visita_id['area_de_visita_id']

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": "Agente não está associado a área de visita informada."}), 400
    
    
    # verificando se o registro_de_campo_id existe
    try:
        search_registro_de_campo = """SELECT registro_de_campo_id, deposito_id, ciclo_id FROM registro_de_campo WHERE registro_de_campo_id = %s;"""
        cursor.execute(search_registro_de_campo, (registro_de_campo_id,))
        registro_de_campo = cursor.fetchone()
        if not registro_de_campo:
            cursor.close()
            conn.close()
            return jsonify({"error": f"Registro de campo com ID {registro_de_campo_id} não encontrado."}), 404
        
        deposito_id = registro_de_campo['deposito_id']
        ciclo_id = registro_de_campo['ciclo_id']

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": f"Erro ao buscar registro de campo: {str(e)}"}), 500


    # Inserir Depósito
    try:

        update_deposito = """
            UPDATE depositos SET a1 = %s, a2 = %s, b = %s, c = %s, d1 = %s, d2 = %s, e = %s WHERE deposito_id = %s;
        """

        # 1. Executa a inserção e a requisição do ID
        # O comando 'execute' retorna None, não o resultado.
        cursor.execute(update_deposito, (a1, a2, b, c, d1, d2, e, deposito_id))

        # 3. Faz o commit da transação
        # conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    

    # return jsonify(f"{deposito_id} atualizado")
    
    # update Registro de Campo
    try:
        cursor = conn.cursor()
        inserir_registro_de_campo = """UPDATE registro_de_campo SET imovel_numero = %s, imovel_lado = %s, imovel_categoria_da_localidade = %s, imovel_tipo = %s, imovel_status = %s, imovel_complemento = %s, formulario_tipo = %s, li = %s, pe = %s, t = %s, df = %s, pve = %s, numero_da_amostra = %s, quantiade_tubitos = %s, observacao = %s, area_de_visita_id = %s, agente_id = %s, deposito_id = %s WHERE registro_de_campo_id = %s;"""
        
        cursor.execute(inserir_registro_de_campo, (imovel_numero, imovel_lado, imovel_categoria_da_localidade, imovel_tipo, imovel_status, imovel_complemento, formulario_tipo, li, pe, t, df, pve, numero_da_amostra, quantiade_tubitos, observacao, area_de_visita_id, agente_id, deposito_id, registro_de_campo_id))
        # return 'oi'

        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    

    # return jsonify(f"Registro de campo {registro_de_campo_id} atualizado com sucesso!")
    

    # Inserir Larvicidas
    try:
        # [{"tipo": "temefos", "forma": "g", "quant": 10}, {"tipo": "adulti", ...}]
        cursor = conn.cursor()

        try:
            larvicidas = json.loads(request.form.get('larvicidas', '[]'))
        except Exception:
            larvicidas = []


        for larvicida in larvicidas:
            tipo = larvicida.get('tipo')
            forma = larvicida.get('forma')
            quantidade = larvicida.get('quantidade')

            inserir_larvicidas = """INSERT INTO larvicida(tipo, forma, quantidade, registro_de_campo_id) VALUES (%s, %s, %s, %s);"""

            # print("Larvicidas: ", tipo, forma, quantidade, registro_de_campo_id)

            cursor.execute(inserir_larvicidas, (tipo, forma, quantidade, registro_de_campo_id))
        
        conn.commit()
            
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500
    


    # Inserir Adulticidas
    try:
        # [{"tipo": "temefos", "forma": "g", "quant": 10}, {"tipo": "adulti", ...}]
        cursor = conn.cursor()

        try:
            adulticidas = json.loads(request.form.get('adulticidas', '[]'))
        except Exception:
            adulticidas = []
        
        # if(adulticida):
        for adulticida in adulticidas:
            tipo = adulticida.get('tipo')
            quantidade = adulticida.get('quantidade')

            inserir_adulticidas = """INSERT INTO adulticida(tipo, quantidade, registro_de_campo_id) VALUES (%s, %s, %s);"""

            print("adulticida: ", tipo, quantidade, registro_de_campo_id)

            cursor.execute(inserir_adulticidas, (tipo, quantidade, registro_de_campo_id))
        
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500
    
    try:
        # [{"tipo": "temefos", "forma": "g", "quant": 10}, {"tipo": "adulti", ...}]
        # cursor = conn.cursor()
        # arquivos = json.loads(request.form.get('arquivos', '[]'))
        files = {}
        count = 1
        for file in request.files.getlist('files'):
            files[f"Arquivo {count}"] = secure_filename(file.filename)
            count += 1

            arquivo_nome = secure_filename(file.filename)

            inserir_arquivos = """INSERT INTO registro_de_campo_arquivos(arquivo_nome, registro_de_campo_id) VALUES (%s, %s);""" 

            print("inserir_arquivos: ", arquivo_nome, registro_de_campo_id)

            cursor.execute(inserir_arquivos, (arquivo_nome, registro_de_campo_id))

            file.save(f'uploads/registro_de_campo_arquivos/reg_de_campo_id_{registro_de_campo_id}_{arquivo_nome}')
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500
    finally:
        conn.close()
        cursor.close()


    return jsonify({
        'status': 'success',
        'message': 'Registro de campo atualizado com sucesso',
        'data': {
            'imovel_numero': imovel_numero,
            'imovel_lado': imovel_lado,
            'imovel_categoria_da_localidade': imovel_categoria_da_localidade,
            'imovel_tipo': imovel_tipo,
            'imovel_status': imovel_status,
            'imovel_complemento': imovel_complemento,
            'formulario_tipo': formulario_tipo,
            'li': li,
            'pe': pe,
            't': t,
            'df': df,
            'pve': pve,
            'numero_da_amostra': numero_da_amostra,
            'quantiade_tubitos': quantiade_tubitos,
            'observacao': observacao,
            'area_de_visita_id': area_de_visita_id,
            'agente_id': agente_id,
            'a1': a1,
            'a2': a2,
            'b': b,
            'c': c,
            'd1': d1,
            'd2': d2,
            'e': e,
            "larvicidas": larvicidas,
            "adulticidas": adulticidas,
            'deposito_id': deposito_id,
            'files': files,
            'ciclo_id': ciclo_id,
            'registro_de_campo_id': registro_de_campo_id
        }
    })