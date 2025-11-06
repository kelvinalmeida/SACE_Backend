from flask import jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import area_para_visita
import logging

logging.basicConfig(level=logging.INFO)

@area_para_visita.route('/area_de_visita/<int:area_de_visita_id>/registros', methods=['GET'])
@token_required
def get_registros_by_area(current_user, area_de_visita_id):
    """
    Busca todos os registros de campo (endereços e status) para uma 
    área de visita específica, mas apenas os do CICLO ATUAL.
    """
    conn = None
    cursor = None
    
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            logging.error("Falha na conexão com o banco de dados")
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
        
        cursor = conn.cursor()

        # 1. Buscar o ciclo ativo (Conforme lógica em get_all.py de registro_de_campo)
        search_ciclo_ativo = "SELECT ciclo_id FROM ciclos WHERE ativo = true LIMIT 1;"
        cursor.execute(search_ciclo_ativo)
        ciclo_ativo = cursor.fetchone()

        if not ciclo_ativo:
            logging.warning(f"Nenhum ciclo ativo encontrado ao buscar registros para area_id {area_de_visita_id}")
            return jsonify({"error": "Nenhum ciclo ativo encontrado."}), 404
        
        ciclo_id = ciclo_ativo['ciclo_id']

        # 2. Buscar os registros de campo para a área e ciclo
        # (Seleciona os campos de endereço e o status, conforme solicitado)
        search_registros_query = """
            SELECT 
                registro_de_campo_id, 
                imovel_numero, 
                imovel_lado,
                imovel_categoria_da_localidade,
                imovel_tipo,
                imovel_complemento, 
                imovel_status 
            FROM 
                registro_de_campo 
            WHERE 
                area_de_visita_id = %s AND ciclo_id = %s
            ORDER BY
                imovel_numero; 
        """
        cursor.execute(search_registros_query, (area_de_visita_id, ciclo_id))
        registros = cursor.fetchall()

        # Retorna a lista (pode estar vazia, o que não é um erro)
        return jsonify(registros), 200

    except Exception as e:
        logging.error(f"Erro ao buscar registros por área de visita {area_de_visita_id}: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()