from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@usuario.route('/usuarios/<int:user_id>', methods=['GET'])
@token_required
def get_user_by_id(current_user, user_id):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()

        search_user = """SELECT * FROM usuario INNER JOIN agente USING(usuario_id) WHERE usuario_id = %s;"""

        cursor.execute(search_user, (user_id,))

        usuario = cursor.fetchone()

        if(usuario):
                try:

                    search_area_de_atuacao = """ SELECT agen_area.agente_id, agen_area.area_de_visita_id, area.cep, area.setor, area.numero_quarteirao, area.estado, area.municipio, area.bairro, area.logadouro FROM agente_area_de_visita agen_area INNER JOIN area_de_visita area USING(area_de_visita_id);"""

                    cursor.execute(search_area_de_atuacao)
                    area_de_atuacao = cursor.fetchall()

                    
                    area_de_atuacao_do_usuario = [ area for area in area_de_atuacao if area['agente_id'] == usuario['agente_id']]

                    area_de_atuacao_do_usuario = [ { 'area_de_visita_id': area['area_de_visita_id'], 'cep': area['cep'], 'setor': area['setor'], 'numero_quarteirao': area['numero_quarteirao'], 'estado': area['estado'], 'municipio': area['municipio'], 'bairro': area['bairro'], 'logadouro': area['logadouro'] } for area in area_de_atuacao_do_usuario ]

                    usuario['setor_de_atuacao'] = area_de_atuacao_do_usuario
        

                except Exception as e:
                    conn.rollback()
                    cursor.close()
                    return jsonify({"error": str(e)}), 500
    

        if(not usuario):

            search_user = """SELECT * FROM usuario INNER JOIN supervisor USING(usuario_id) WHERE usuario_id = %s;"""

            cursor.execute(search_user, (user_id,))

            usuario = cursor.fetchone()
        
        
        # Adicionar esta verificação:
        if usuario is None:
            return jsonify({"error": "Usuário não encontrado"}), 404

        return jsonify(usuario), 200

    
    except Exception as e:
        return jsonify({"error": str(e)})
    
    