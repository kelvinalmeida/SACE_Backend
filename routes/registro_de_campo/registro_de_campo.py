from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from token_required import token_required
import json

registro_de_campo = Blueprint('registro_de_campo', __name__)

@registro_de_campo.route('/registro_de_campo', methods=['POST'])
@token_required
def send_registro_de_campo():

    
    rua = request.form.get('rua')
    imovel_numero = request.form.get('imovel_numero')
    imovel_lado = request.form.get('imovel_lado')
    imovel_categoria_da_localidade = request.form.get('imovel_categoria_da_localidade')
    imovel_tipo = request.form.get('imovel_tipo')
    imovel_status = request.form.get('imovel_status')
    imovel_complemento = request.form.get('imovel_complemento')
    formulario_tipo = request.form.get('formulario_tipo')
    li = request.form.get('li')
    pe = request.form.get('pe')
    t = request.form.get('t')
    df = request.form.get('df')
    pve = request.form.get('pve')
    numero_da_amostra = request.form.get('numero_da_amostra')
    quantiade_tubitos = request.form.get('quantiade_tubitos')
    observacao = request.form.get('observacao')
    area_de_visita_id = request.form.get('area_de_visita_id')
    
    agente_id = session.get("usuario_id")

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
    


    try:
        # Query para buscar a área de visita do agente logado
        cursor = conn.cursor()
        search_agente_area_de_visita = """SELECT area_de_visita_id FROM agente_area_de_visita WHERE agente_id = %s AND area_de_visita_id = %s;"""

        cursor.execute(search_agente_area_de_visita, (agente_id, area_de_visita_id))
        
        area_de_visita_id = cursor.fetchone()

        area_de_visita_id = area_de_visita_id['area_de_visita_id']

    except Exception as e:
        return jsonify({"error": "Agente não está associado a área de visita informada."}), 400


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
            raise Exception("Falha ao obter o ID do depósito após a inserção.")


    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
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
            'deposito_id': deposito_id
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
        search_users = """SELECT * FROM registro_de_campo;"""


        cursor.execute(search_users)
        registro_de_campo = cursor.fetchall()

        return jsonify(registro_de_campo)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        cursor.close()