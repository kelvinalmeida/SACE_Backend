from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging

# Importando a exceção específica para tratar possíveis erros de transação
from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@usuario.route('/usuarios', methods=['GET'])
@token_required
def get_usuarios(current_user):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    usuarios = {}

    try: 
        cursor = conn.cursor()

        search_agentes = """
    SELECT 
        usuario_id, nome_completo, cpf, rg, data_nascimento, email, 
        telefone_ddd, telefone_numero, estado, municipio, bairro, 
        logradouro, numero, registro_do_servidor, cargo, situacao_atual, 
        data_de_admissao, nivel_de_acesso, agente_id
    FROM usuario INNER JOIN agente USING(usuario_id);
"""

        cursor.execute(search_agentes)
        agentes = cursor.fetchall()

        usuarios['agentes'] = agentes

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    try:

        search_area_de_atuacao = """ SELECT agen_area.agente_id, agen_area.area_de_visita_id, area.cep, area.setor, area.numero_quarteirao, area.estado, area.municipio, area.bairro, area.logadouro FROM agente_area_de_visita agen_area INNER JOIN agente USING (agente_id) INNER JOIN area_de_visita area USING(area_de_visita_id);"""

        cursor.execute(search_area_de_atuacao)
        area_de_atuacao = cursor.fetchall()


        for usua in usuarios['agentes']:
            areas_de_atuacao_do_usuario = [ area for area in area_de_atuacao if usua['agente_id'] == area['agente_id']]

            areas_de_atuacao_do_usuario = [ { 'area_de_visita_id': area['area_de_visita_id'], 'cep': area['cep'], 'setor': area['setor'], 'numero_quarteirao': area['numero_quarteirao'], 'estado': area['estado'], 'municipio': area['municipio'], 'bairro': area['bairro'], 'logadouro': area['logadouro'] } for area in areas_de_atuacao_do_usuario ]

            usua['setor_de_atuacao'] = areas_de_atuacao_do_usuario
        

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    try:

        search_supervisores = """
    SELECT 
        *
    FROM usuario INNER JOIN supervisor USING(usuario_id);
"""

        cursor.execute(search_supervisores)
        supervisores = cursor.fetchall()

        usuarios['supervisores'] = supervisores
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    finally:
        conn.close()
        cursor.close()

        return jsonify(usuarios), 200