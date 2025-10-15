from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import graficos
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/depositos_tratados/<int:ano>/<int:ciclo>', methods=['GET'])
@token_required
def get_depositos_tratados(current_user, ano, ciclo):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # Buscar ciclo_id do ciclo e ano fornecido
    try:
        cursor = conn.cursor()

        search_ciclo_atual = """SELECT ciclo_id, EXTRACT(YEAR FROM ano_de_criacao)::INTEGER AS ano, ciclo FROM ciclos;"""

        cursor.execute(search_ciclo_atual)
        ciclos = cursor.fetchall()


        ciclo_procurado = [c for c in ciclos if c['ano'] == ano and c['ciclo'] == ciclo]

        ciclo_id = ciclo_procurado[0]['ciclo_id'] if ciclo_procurado else None

        registros_de_campo_do_ciclo_celecionado = """SELECT registro_de_campo_id, ciclo_id FROM registro_de_campo WHERE ciclo_id = %s"""
        cursor.execute(registros_de_campo_do_ciclo_celecionado, (ciclo_id,))
        registros_de_campo_do_ciclo_celecionado = cursor.fetchall()
        registros_de_campo_do_ciclo_celecionado = registros_de_campo_do_ciclo_celecionado if registros_de_campo_do_ciclo_celecionado else []

        # return jsonify(registros_de_campo_do_ciclo_celecionado)
                
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    try:

        
        search = """SELECT * FROM larvicida;"""

        cursor.execute(search)

        all_larvididas = cursor.fetchall()
        all_larvididas = all_larvididas if all_larvididas else []

        larcicidas_do_ciclo_selecionado = []
        for reg_camp in registros_de_campo_do_ciclo_celecionado:
            for larvicida in all_larvididas:
                if larvicida['registro_de_campo_id'] == reg_camp['registro_de_campo_id']:
                    larcicidas_do_ciclo_selecionado.append(larvicida)
        
        # return jsonify(larcicidas_do_ciclo_selecionado)
        
        
        
        
        search = """SELECT * FROM adulticida;"""
        
        cursor.execute(search)

        all_adulticidas = cursor.fetchall()
        all_adulticidas = all_adulticidas if all_adulticidas else []

        adulticidas_do_ciclo_selecionado = []
        for reg_camp in registros_de_campo_do_ciclo_celecionado:
            for larvicida in all_adulticidas:
                if larvicida['registro_de_campo_id'] == reg_camp['registro_de_campo_id']:
                    adulticidas_do_ciclo_selecionado.append(larvicida)

        return jsonify({
            "larvicidas": len(larcicidas_do_ciclo_selecionado),
            "adulticidas": len(adulticidas_do_ciclo_selecionado)
            }), 200


    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        cursor.close()
        conn.close()
    
    