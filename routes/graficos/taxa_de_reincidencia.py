from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import graficos
import logging

# Importando a exceção específica para tratar possíveis erros de transação
# from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@graficos.route('/grafico/taxa_de_reincidencia/<int:ano>/<int:ciclo>', methods=['GET'])
@token_required
def get_taxa_de_reincidencia(current_user, ano, ciclo):

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
            search_ano_anterior = """SELECT registro_de_campo_id, area_de_visita_id, imovel_numero, logadouro, bairro FROM registro_de_campo INNER JOIN area_de_visita USING (area_de_visita_id) WHERE (t = True OR li = True OR df = True) AND ciclo_id = %s;"""

            cursor.execute(search_ano_anterior, (ciclo_id_ano_anterior,))
            focos_positivos_ciclo_anterior = cursor.fetchall()
            focos_positivos_ciclo_anterior = focos_positivos_ciclo_anterior if focos_positivos_ciclo_anterior else []
            
        else:
            focos_positivos_ciclo_anterior = 0
                
        # return jsonify(focos_positivos_ciclo_anterior)
        
        ciclo_id = ciclo_procurado[0]['ciclo_id'] if ciclo_procurado else None

        # return f"{ciclo_id}"
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    try:

        
        search = """SELECT registro_de_campo_id, area_de_visita_id, imovel_numero, logadouro, bairro FROM registro_de_campo INNER JOIN area_de_visita USING (area_de_visita_id) WHERE (t = True OR li = True OR df = True) AND ciclo_id = %s;"""


        cursor.execute(search, (ciclo_id,))

        focos_do_ciclo_procurado = cursor.fetchall()
        focos_do_ciclo_procurado = focos_do_ciclo_procurado if ciclo_id else []

        # return jsonify(focos_do_ciclo_procurado)
        reincidencia_por_bairros = {}

        if (not focos_do_ciclo_procurado) or (not focos_positivos_ciclo_anterior):
            return jsonify({
                "Ponta Verde": 0,
                "Jatiúca": 0,
                "Pajuçara": 0,
                "Farol": 0,
                "Benedito Bentes": 0,
            }), 200
        

        for reg_ciclo_atual in focos_do_ciclo_procurado:
            for reg_cliclo_anterior in focos_positivos_ciclo_anterior:
                # A condição de reincidência permanece a mesma
                if (reg_ciclo_atual['bairro'] == reg_cliclo_anterior['bairro'] and
                    reg_ciclo_atual['imovel_numero'] == reg_cliclo_anterior['imovel_numero'] and
                    reg_ciclo_atual['logadouro'] == reg_cliclo_anterior['logadouro']):

                    bairro_atual = reg_ciclo_atual['bairro']

                    # 1. CORREÇÃO: Verificamos se a chave 'bairro' JÁ EXISTE no dicionário
                    if bairro_atual in reincidencia_por_bairros:
                        # 2. CORREÇÃO: Incrementamos o contador em 1 (não somamos o nome do bairro)
                        reincidencia_por_bairros[bairro_atual] += 1
                    else:
                        # Se não existe, criamos a chave e iniciamos a contagem com 1
                        reincidencia_por_bairros[bairro_atual] = 1

                    # A reincidência para este imóvel já foi encontrada,
                    # podemos quebrar o loop interno para otimizar
                    break


        return jsonify(reincidencia_por_bairros), 200
        
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return jsonify({"error": "Database query failed"}), 500
    finally:
        cursor.close()
        conn.close()
    
    