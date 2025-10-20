from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import graficos
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/imoveis_trabalhados/<int:ano>/<int:ciclo>', methods=['GET'])
def get_imoveis_trabalhados(ano, ciclo):

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

                
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    try:

        ciclo_id = ciclo_procurado[0]['ciclo_id'] if ciclo_procurado else None
        
        search = """SELECT imovel_status, COUNT(imovel_status) quantidade FROM registro_de_campo WHERE ciclo_id = %s GROUP BY imovel_status;"""


        cursor.execute(search, (ciclo_id,))

        registros_status_ciclo_precurado = cursor.fetchall()
        registros_status_ciclo_precurado = registros_status_ciclo_precurado if registros_status_ciclo_precurado else {}


        imoveis_trabalhados = {}
        imoveis_trabalhados['inspecionados'] = 0
        imoveis_trabalhados['bloqueados'] = 0
        imoveis_trabalhados['fechados'] = 0
        imoveis_trabalhados['recusados'] = 0
        imoveis_trabalhados['nao_inspecionados'] = 0
        imoveis_trabalhados['total'] = sum([sta['quantidade'] for sta in registros_status_ciclo_precurado])
        # return jsonify(registros_status_ciclo_precurado)

        for status in registros_status_ciclo_precurado:

            if status["imovel_status"] == 'inspecionado':
                imoveis_trabalhados['inspecionados'] = status["quantidade"]
            elif status["imovel_status"] == 'bloqueado':
                imoveis_trabalhados['bloqueados'] = status["quantidade"]
            elif status["imovel_status"] == 'fechado':
                imoveis_trabalhados['fechados'] = status["quantidade"]
            elif status["imovel_status"] == 'recusado':
                imoveis_trabalhados['recusados'] = status["quantidade"]
            elif status["imovel_status"] == 'nao_inspecionado':
                imoveis_trabalhados['nao_inspecionados'] = status["quantidade"]

        return jsonify(imoveis_trabalhados), 200


    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        cursor.close()
        conn.close()
    
    