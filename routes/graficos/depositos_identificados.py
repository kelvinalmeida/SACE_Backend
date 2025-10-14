from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import graficos
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/depositos_identificados/<int:ano>/<int:ciclo>', methods=['GET'])
@token_required
def get_depositos_identificados(current_user, ano, ciclo):

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    # Buscar ciclo_id do ciclo e ano fornecido
    try:
        cursor = conn.cursor()

        all_cicles = """SELECT ciclo_id, EXTRACT(YEAR FROM ano_de_criacao)::INTEGER AS ano, ciclo FROM ciclos;"""

        cursor.execute(all_cicles)
        ciclos = cursor.fetchall()


        ciclo_procurado = [c for c in ciclos if c['ano'] == ano and c['ciclo'] == ciclo]
        
        ciclo_id = ciclo_procurado[0]['ciclo_id'] if ciclo_procurado else None

        depositos_ids_ciclo_procurado = """SELECT deposito_id FROM registro_de_campo WHERE T = True OR LI = True OR DF = True AND ciclo_id = %s;"""

        cursor.execute(depositos_ids_ciclo_procurado, (ciclo_id,)) 
        depositos_ids_ciclo_procurado = cursor.fetchall() if ciclo_id else []
        # return  jsonify(depositos_ids_ciclo_procurado)
        
        
        # return jsonify(depositos_ids_ciclo_procurado)

        if(ciclo == 1):
            ano_anterior = ano - 1
            
            ciclo_anterior = [c for c in ciclos if c['ano'] == ano_anterior]

            ciclo_id_ano_anterior = ciclo_anterior[-1]['ciclo_id'] if ciclo_anterior else None
        else:
            ano_anterior = ano
            ciclo_anterior = ciclo - 1

            ciclo_anterior = [c for c in ciclos if c['ano'] == ano_anterior and c['ciclo'] == ciclo_anterior]

            ciclo_id_ano_anterior = ciclo_anterior[0]['ciclo_id'] if ciclo_anterior else None
            
       
        if ciclo_id_ano_anterior:
            depositos_ids_ciclo_anterior = """SELECT deposito_id FROM registro_de_campo WHERE T = True OR LI = True OR DF = True AND ciclo_id = %s;"""

            cursor.execute(depositos_ids_ciclo_anterior, (ciclo_id_ano_anterior,))
            depositos_ids_ciclo_anterior = cursor.fetchall()

            
         
        else:
            depositos_ids_ciclo_anterior = 0


    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    

    # Contando os depositos do ciclo atual    
    try:
        all_deposits = """SELECT * FROM depositos;"""
        cursor.execute(all_deposits)
        all_deposits = cursor.fetchall()

        all_deposits = {deposito['deposito_id']: deposito for deposito in all_deposits }
        quantidade_depositos = {}
        quantidade_depositos["depositos identificados"] = 0


        if depositos_ids_ciclo_procurado:
            for deposito_id_ciclo_procurado in depositos_ids_ciclo_procurado:
                print(deposito_id_ciclo_procurado['deposito_id'])
                deposito = all_deposits.get(deposito_id_ciclo_procurado['deposito_id'], 0)
                
                # return jsonify(deposito)
                quantidade_depositos["depositos identificados"] = quantidade_depositos["depositos identificados"] + deposito['a1'] + deposito["a2"] + deposito["b"] + deposito["c"] + deposito["d1"] + deposito["d2"] + deposito["e"]

        # return jsonify(quantidade_depositos)

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    # Contando os depositos do ciclo anterior   
    try:
        quantidade_depositos["Dados do ultimo ciclo: "] = 0


        if depositos_ids_ciclo_anterior:
            for deposito_id_ciclo_anterior in depositos_ids_ciclo_anterior:
                deposito = all_deposits.get(deposito_id_ciclo_anterior['deposito_id'], 0)
                
                # return jsonify(deposito)
                quantidade_depositos["Dados do ultimo ciclo: "] = quantidade_depositos["Dados do ultimo ciclo: "] + deposito['a1'] + deposito["a2"] + deposito["b"] + deposito["c"] + deposito["d1"] + deposito["d2"] + deposito["e"]
        
        depositos_identificados = quantidade_depositos["depositos identificados"]
        dados_do_ultimo_ciclo = quantidade_depositos["Dados do ultimo ciclo: "]
        
        
        dados_do_ultimo_ciclo = quantidade_depositos["Dados do ultimo ciclo: "]

        if dados_do_ultimo_ciclo == 0 and depositos_identificados > 0:
            # Cannot calculate percentage change from zero, but it's an increase
            quantidade_depositos["porcentagem"] = "100% (Novo)"
            quantidade_depositos["crescimento"] = "aumentou"
        elif (dados_do_ultimo_ciclo == 0 and depositos_identificados == 0) or (dados_do_ultimo_ciclo ==  depositos_identificados) :
            quantidade_depositos["porcentagem"] = "0%"
            quantidade_depositos["crescimento"] = "estável"
        elif dados_do_ultimo_ciclo > 0:
            if depositos_identificados > dados_do_ultimo_ciclo:
                porcentagem = round(((depositos_identificados / dados_do_ultimo_ciclo) - 1) * 100, 2)
                quantidade_depositos["porcentagem"] = f"{porcentagem}% ↑"
                quantidade_depositos["crescimento"] = "aumentou"
            else:
                porcentagem = round((1 - (depositos_identificados / dados_do_ultimo_ciclo)) * 100, 2)
                quantidade_depositos["porcentagem"] = f"{porcentagem}% ↓"
                quantidade_depositos["crescimento"] = "diminuiu"
        else:
            # Handle case where current is zero and previous was > 0
            porcentagem = round((1 - (0 / dados_do_ultimo_ciclo)) * 100, 2) # Should be 100% decrease
            quantidade_depositos["porcentagem"] = f"{porcentagem}% ↓"
            quantidade_depositos["crescimento"] = "diminuiu"

        return jsonify(quantidade_depositos)
    

    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        cursor.close()
        conn.close()
    
    