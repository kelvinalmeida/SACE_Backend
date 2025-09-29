from flask import Flask, request, jsonify, Blueprint, current_app
from db import create_connection
from token_required import token_required

usuario = Blueprint('usuario', __name__)

@usuario.route('/usuarios/agentes', methods=['GET'])
@token_required
def get_usuarios(current_user):
    # Cria conexão
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # Query para buscar todos os usuários agentes relacionando a sua área de visita
        search_users = """SELECT usuario.nome_completo nome, usuario.telefone_numero contato, area.setor zonas_responsaveis, area.municipio localidade, usuario.situacao_atual situacao FROM usuario usuario INNER JOIN agente USING(usuario_id) INNER JOIN agente_area_de_visita USING(agente_id) INNER JOIN area_de_visita area USING(area_de_visita_id);"""


        cursor.execute(search_users)
        agentes = cursor.fetchall()


        return jsonify(agentes)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        cursor.close()