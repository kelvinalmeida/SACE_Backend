from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import graficos
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/casos_comfirmados/<int:ano>/<int:ciclo>', methods=['GET'])
@token_required
def get_casos_comfirmados(current_user, ano, ciclo):

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
            search_ano_anterior = """SELECT registro_de_campo_id, caso_comfirmado FROM registro_de_campo WHERE (caso_comfirmado = True) AND (ciclo_id = %s);"""

            cursor.execute(search_ano_anterior, (ciclo_id_ano_anterior,))
            casos_positivos_ciclo_anterior = cursor.fetchall()
            casos_positivos_ciclo_anterior = len(casos_positivos_ciclo_anterior) if casos_positivos_ciclo_anterior else 0
            # return jsonify(casos_positivos_ciclo_anterior)
            
        else:
            casos_positivos_ciclo_anterior = 0
                
        
        ciclo_id = ciclo_procurado[0]['ciclo_id'] if ciclo_procurado else None

        # return f"{ciclo_id}"
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    try:

        
        search = """SELECT registro_de_campo_id, caso_comfirmado FROM registro_de_campo WHERE (caso_comfirmado = True) AND (ciclo_id = %s);"""


        cursor.execute(search, (ciclo_id,))

        casos_positivos = cursor.fetchall()
        casos_positivos = len(casos_positivos) if ciclo_id else 0
        # return jsonify(casos_positivos)
        porcentagem_str = "0%"
        crescimento_str = "estável"
        has_changed = True


        # Case 1: Previous cycle had zero foci
        if casos_positivos_ciclo_anterior == 0:
            if casos_positivos > 0:
                # Increase from 0 to a positive number
                porcentagem_str = "100% (Novo) ↑"
                crescimento_str = "aumentou"
            else:
                # 0 in current and 0 in previous
                porcentagem_str = "0%"
                crescimento_str = "estável"
                has_changed = False

        # Case 2: Previous cycle had positive foci
        elif casos_positivos_ciclo_anterior > 0:
            if casos_positivos > casos_positivos_ciclo_anterior:
                # Increase
                percentage = round(((casos_positivos / casos_positivos_ciclo_anterior) - 1) * 100, 2)
                porcentagem_str = f"{percentage}% ↑"
                crescimento_str = "aumentou"
            elif casos_positivos < casos_positivos_ciclo_anterior:
                # Decrease
                # The calculation should be 1 - (New/Old) to get the correct decrease percentage.
                percentage = round((1 - (casos_positivos / casos_positivos_ciclo_anterior)) * 100, 2)
                porcentagem_str = f"{percentage}% ↓"
                crescimento_str = "diminuiu"
            else:
                # Stable
                porcentagem_str = "0%"
                crescimento_str = "estável"
                has_changed = False

        # Note: The case where current is 0 and previous is > 0 is handled 
        # by the 'Decrease' block above (percentage will be 100% decrease).
        # If you want a specific message for 100% decrease:
        # elif casos_positivos == 0 and casos_positivos_ciclo_anterior > 0:
        #     porcentagem_str = "100% ↓"
        #     crescimento_str = "diminuiu"


        # --- Return Statement ---

        return jsonify({
            "casos_positivos": casos_positivos,
            "Dados do ultimo ciclo": casos_positivos_ciclo_anterior,
            "porcentagem": porcentagem_str,
            "crescimento": crescimento_str
        }), 200
        
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        cursor.close()
        conn.close()
    
    