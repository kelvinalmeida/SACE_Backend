from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import datetime
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)


def serialize_data(data):
    """
    Recursively converts non-serializable objects (like datetime.time)
    into strings suitable for JSON.
    """
    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    elif isinstance(data, (datetime.date, datetime.datetime, datetime.time)):
        # Convert date, datetime, and time objects to ISO 8601 strings
        return data.isoformat()
    # Handle other types like Decimal if necessary, e.g.:
    # elif isinstance(data, Decimal):
    #     return str(data) 
    else:
        return data
    

@usuario.route('/area_de_visita_denuncias/<int:agente_id>', methods=['GET'])
@token_required
def get_area_de_visita_e_denuncias_agente(current_user, agente_id):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()

        search_user = """SELECT * FROM usuario INNER JOIN agente USING(usuario_id) WHERE usuario_id = %s;"""

        cursor.execute(search_user, (agente_id,))

        usuario = cursor.fetchone()

        area_de_visitas_e_denuncias = {}

        if(usuario):
                try:

                    search_area_de_atuacao = """ SELECT agen_area.agente_id, agen_area.area_de_visita_id FROM agente_area_de_visita agen_area INNER JOIN area_de_visita area USING(area_de_visita_id) WHERE agente_id = %s;"""

                    cursor.execute(search_area_de_atuacao, (agente_id, ))
                    area_de_atuacao = cursor.fetchall()
                    areas_de_visitas = []

                    for area in area_de_atuacao:
                        area_de_visita_id = area['area_de_visita_id']
                        # return f"{area_de_visita_id}"
                        search_area_de_visita = """SELECT * FROM area_de_visita WHERE area_de_visita_id = %s;"""
                        cursor.execute(search_area_de_visita, (area_de_visita_id,))
                        area_de_visita = cursor.fetchone()
                        areas_de_visitas.append(area_de_visita)

                    area_de_visitas_e_denuncias['areas_de_visitas'] = areas_de_visitas
                    # return jsonify(area_de_visitas_e_denuncias)

                except Exception as e:
                    conn.rollback()
                    cursor.close()
                    return jsonify({"error": str(e)}), 500
                
                # pegar denuncias do agente
                try:
                     
                    search_denuncias = """ SELECT * FROM denuncia WHERE agente_responsavel_id = %s;"""
                    cursor.execute(search_denuncias, (usuario['agente_id'],))
                    denuncias = cursor.fetchall()

                    all_denuncias_dicts = [dict(denc) for denc in denuncias]
                    serializable_denuncias = serialize_data(all_denuncias_dicts)

                    area_de_visitas_e_denuncias['denuncias'] = serializable_denuncias
                
                except Exception as e:
                    conn.rollback()
                    cursor.close()
                    return jsonify({"error": str(e)}), 500
    

  
        # Adicionar esta verificação:
        if usuario is None:
            return jsonify({"error": "Agente não encontrado"}), 404

        return jsonify(area_de_visitas_e_denuncias), 200

    
    except Exception as e:
        return jsonify({"error": str(e)})
    
    