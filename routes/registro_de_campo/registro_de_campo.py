from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from token_required import token_required
import json
from werkzeug.utils import secure_filename


registro_de_campo = Blueprint('registro_de_campo', __name__)

def check_required_filds(required_fild):
    for fild in required_fild:
        if fild not in request.form or request.form[fild] is None or request.form[fild].strip() == "":
            return {"error": f"{fild} is required"}
    return False


@registro_de_campo.route('/registro_de_campo', methods=['POST'])
@token_required
def send_registro_de_campo(current_user):

    check_filds = check_required_filds(['rua', 'imovel_numero', 'imovel_lado', 'imovel_categoria_da_localidade', 'imovel_tipo', 'imovel_status'])

    if(check_filds):
        return jsonify(check_filds), 400

    rua = request.form.get('rua')
    imovel_numero = request.form.get('imovel_numero')
    imovel_lado = request.form.get('imovel_lado')
    imovel_categoria_da_localidade = request.form.get('imovel_categoria_da_localidade')
    imovel_tipo = request.form.get('imovel_tipo')
    imovel_status = request.form.get('imovel_status')
    imovel_complemento = request.form.get('imovel_complemento')
    formulario_tipo = request.form.get('formulario_tipo')

    try:
        li = bool(request.form.get('li'))
        pe = bool(request.form.get('pe'))
        t = bool(request.form.get('t'))
        df = bool(request.form.get('df'))
        pve = bool(request.form.get('pve'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input for li, pe, t, df, or pve. They must be boolean values."}), 400

    numero_da_amostra = request.form.get('numero_da_amostra')
    quantiade_tubitos = request.form.get('quantiade_tubitos')
    observacao = request.form.get('observacao')
    area_de_visita_id = request.form.get('area_de_visita_id')
    
    agente_id = current_user['agente_id']

    try:
        a1 = int(request.form.get('a1'))
        a2 = int(request.form.get('a2'))
        b = int(request.form.get('b'))
        c = int(request.form.get('c'))
        d1 = int(request.form.get('d1'))
        d2 = int(request.form.get('d2'))
        e = int(request.form.get('e'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input for a1, a2, b, c, d1, d2, or e. They must be integers."}), 400
    

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    

    
    print(">>>>>>>>>>", area_de_visita_id, agente_id)

    # Query para buscar a área de visita do agente logado
    try:
        cursor = conn.cursor()
        search_agente_area_de_visita = """SELECT area_de_visita_id FROM agente_area_de_visita WHERE agente_id = %s AND area_de_visita_id = %s;"""

        cursor.execute(search_agente_area_de_visita, (agente_id, area_de_visita_id))
        
        area_de_visita_id = cursor.fetchone()

        area_de_visita_id = area_de_visita_id['area_de_visita_id']

    except Exception as e:
        return jsonify({"error": "Agente não está associado a área de visita informada."}), 400
    

    # Inserir Depósito
    try:
        cursor = conn.cursor()
        insir_deposito = """
            INSERT INTO depositos(a1, a2, b, c, d1, d2, e) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
            RETURNING deposito_id; 
        """

        # 1. Executa a inserção e a requisição do ID
        # O comando 'execute' retorna None, não o resultado.
        cursor.execute(insir_deposito, (a1, a2, b, c, d1, d2, e))

        # 2. Usa fetchone() para obter a linha de resultado (que contém o ID)
        # Como RETURNING retorna uma única linha com uma única coluna (deposito_id),
        # fetchone() retorna uma tupla ou lista, dependendo do driver.
        resultado = cursor.fetchone()

        # 3. Faz o commit da transação
        conn.commit()

        # 4. Extrai o ID
        if resultado:
            deposito_id = resultado["deposito_id"]
        else:
            conn.rollback()
            raise Exception("Falha ao obter o ID do depósito após a inserção.")
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    #Inserir Registro de Campo
    try:
        cursor = conn.cursor()
        inserir_registro_de_campo = """INSERT INTO registro_de_campo(
            rua, imovel_numero, imovel_lado, imovel_categoria_da_localidade, imovel_tipo, imovel_status, imovel_complemento, formulario_tipo, li, pe, t, df, pve, numero_da_amostra, quantiade_tubitos, observacao, area_de_visita_id, agente_id, deposito_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING registro_de_campo_id; """
        
        cursor.execute(inserir_registro_de_campo, (rua, imovel_numero, imovel_lado, imovel_categoria_da_localidade, imovel_tipo, imovel_status, imovel_complemento, formulario_tipo, li, pe, t, df, pve, numero_da_amostra, quantiade_tubitos, observacao, area_de_visita_id, agente_id, deposito_id))

        registro_de_campo_id = cursor.fetchone()
        registro_de_campo_id = registro_de_campo_id['registro_de_campo_id']
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    

    # Inserir Larvicidas
    try:
        # [{"tipo": "temefos", "forma": "g", "quant": 10}, {"tipo": "adulti", ...}]
        cursor = conn.cursor()
        larvicidas = json.loads(request.form.get('larvicidas', '[]'))

        for larvicida in larvicidas:
            tipo = larvicida.get('tipo')
            forma = larvicida.get('forma')
            quantidade = larvicida.get('quantidade')
            registro_de_campo_id = registro_de_campo_id

            inserir_larvicidas = """INSERT INTO larvicida(tipo, forma, quantidade, registro_de_campo_id) VALUES (%s, %s, %s, %s);"""

            print("Larvicidas: ", tipo, forma, quantidade, registro_de_campo_id)

            cursor.execute(inserir_larvicidas, (tipo, forma, quantidade, registro_de_campo_id))
        
        conn.commit()
            
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500
    


    # Inserir Adulticidas
    try:
        # [{"tipo": "temefos", "forma": "g", "quant": 10}, {"tipo": "adulti", ...}]
        cursor = conn.cursor()
        adulticidas = json.loads(request.form.get('adulticidas', '[]'))

        for adulticida in adulticidas:
            tipo = adulticida.get('tipo')
            quantidade = adulticida.get('quantidade')
            registro_de_campo_id = registro_de_campo_id

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
    finally:
        conn.rollback()
        conn.close()
        cursor.close()


    return jsonify({
        'status': 'success',
        'message': 'Registro de campo recebido com sucesso',
        'data': {
            'rua': rua,
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
            'deposito_id': deposito_id,
            'files': files
        }
    })



@registro_de_campo.route('/registro_de_campo/all', methods=['GET'])
@token_required
def get_registro_de_campo():
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # Query para buscar todos os usuários agentes relacionando a sua área de visita
        search_users = """SELECT * FROM registro_de_campo INNER JOIN area_de_visita USING(area_de_visita_id) INNER JOIN depositos USiNG(deposito_id) INNER JOIN agente USING(agente_id) INNER JOIN usuario USING(usuario_id);"""


        cursor.execute(search_users)
        registro_de_campo = cursor.fetchall()

        return jsonify(registro_de_campo)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        cursor.close()