from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import graficos
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/focos_positivos/<int:ano>/<int:ciclo>', methods=['GET'])
@token_required
def get_user_by_id(current_user, ano, ciclo):

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
        
        # ciclo_ano_anterior_correto = None

        

        if(ciclo == 1):
            ano_anterior = ano - 1
            
            ciclos_do_ano_anterior = [c for c in ciclos if c['ano'] == ano_anterior]

            ciclo_id_ano_anterior = ciclos_do_ano_anterior[-1]['ciclo_id'] if ciclos_do_ano_anterior else None
        else:
            ano_anterior = ano
            ciclo_anterior = ciclo - 1

            ciclos_do_ano_anterior = [c for c in ciclos if c['ano'] == ano_anterior and c['ciclo'] == ciclo_anterior]

            ciclo_id_ano_anterior = ciclos_do_ano_anterior[0]['ciclo_id'] if ciclos_do_ano_anterior else None
            
       
        if ciclo_id_ano_anterior:
            search_ano_anterior = """SELECT imovel_status, COUNT(imovel_status) focos_positivos FROM registro_de_campo WHERE imovel_status = 'Tratado' AND ciclo_id = %s GROUP BY imovel_status;"""

            cursor.execute(search_ano_anterior, (ciclo_id_ano_anterior,))
            focos_positivos_ciclo_anterior = cursor.fetchone()
            focos_positivos_ciclo_anterior = focos_positivos_ciclo_anterior['focos_positivos'] if focos_positivos_ciclo_anterior else 0
            
            
        else:
            focos_positivos_ciclo_anterior = 0
                

        ciclo_id = ciclo_procurado[0]['ciclo_id'] if ciclo_procurado else None
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    try:

        
        search = """SELECT imovel_status, COUNT(imovel_status) focos_positivos FROM registro_de_campo WHERE imovel_status = 'Tratado' AND ciclo_id = %s GROUP BY imovel_status;"""


        cursor.execute(search, (ciclo_id,))

        focos_positivos = cursor.fetchone()
        focos_positivos = focos_positivos['focos_positivos'] if focos_positivos else 0

        return jsonify({
            "focos_positivos": focos_positivos,
            "Dados do ultimo ciclo": focos_positivos_ciclo_anterior,
            "porcentagem": round(focos_positivos / focos_positivos_ciclo_anterior - 1, 2)  if focos_positivos > focos_positivos_ciclo_anterior else focos_positivos_ciclo_anterior / focos_positivos,
            "crescimento": "aumentou" if focos_positivos > focos_positivos_ciclo_anterior else "dimonuiu"
            
        }), 200
    
        
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        cursor.close()
        conn.close()
    
    