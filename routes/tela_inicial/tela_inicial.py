from flask import Flask, request, jsonify, Blueprint, current_app
from db import create_connection

tela_inicial = Blueprint('tela_inicial', __name__)

@tela_inicial.route('/tela_inicial', methods=['GET'])
def get_tela_inicial():

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    cursor = None # Inicializa o cursor como None para o bloco finally
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        # CORREÇÃO: Removi o argumento da chamada de cursor()
        cursor = conn.cursor()

        # Para a aba DEPOSITOS
        depositos_totais_e_ruas = calculate_total_depositos(cursor)

        # Área de risco
        areas_de_risco = calcular_areas_de_risco(cursor)

        tela_inicial_response = {
            "aba_depositos": depositos_totais_e_ruas,
            "aba_areas_de_risco": areas_de_risco
        }
        
        return jsonify(tela_inicial_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: # Fecha o cursor somente se ele foi criado
            cursor.close()
        if conn: # Fecha a conexão somente se ela foi criada
            conn.close()


def calcular_areas_de_risco(cursor):
    search_users = """SELECT area.bairro, reg.formulario_tipo FROM registro_de_campo reg INNER JOIN area_de_visita area USING (area_de_visita_id) WHERE reg.imovel_status = 'Tratado' OR reg.imovel_status = 'Visitado';"""

    cursor.execute(search_users)
    bairros = cursor.fetchall()

    # {
    # "areas_de_risco": [
    #     {
    #         "bairro": "Ponta Verde",
    #         "formulario_tipo": "Dengue"
    #     },
    #     {
    #         "bairro": "Ponta Verde",
    #         "formulario_tipo": "Dengue"
    #     },
    #     {
    #         "bairro": "Ponta Verde",
    #         "formulario_tipo": "Chikungunya"
    #     },...

    dados_dos_bairros = {}

    for bairro in bairros:
        if bairro['bairro'] not in dados_dos_bairros:
            dados_dos_bairros[bairro['bairro']] = {
                "Dengue": 0,
                "Chikungunya": 0,
                "Zika": 0
            }
        if bairro['formulario_tipo'] == 'Dengue':
            dados_dos_bairros[bairro['bairro']]["Dengue"] += 1
        elif bairro['formulario_tipo'] == 'Chikungunya':
            dados_dos_bairros[bairro['bairro']]["Chikungunya"] += 1
        elif bairro['formulario_tipo'] == 'Zika':
            dados_dos_bairros[bairro['bairro']]["Zika"] += 1

    doenca_mais_populares_por_bairro = {}
    for bairro, contagens in dados_dos_bairros.items():
        doenca_mais_populares_por_bairro[bairro] = max(contagens, key=contagens.get)
    for bairro in dados_dos_bairros:
        dados_dos_bairros[bairro]["doenca_mais_popular"] = doenca_mais_populares_por_bairro[bairro]



    return dados_dos_bairros

def calculate_total_depositos(cursor):

    search_users = """SELECT reg.deposito_id, reg.rua, reg.imovel_numero, area.cep, area.estado, area.bairro, dep.a1, dep.a2, dep.b, dep.c, dep.d1, dep.d2, dep.e FROM registro_de_campo reg INNER JOIN area_de_visita area USING(area_de_visita_id) INNER JOIN depositos dep USING(deposito_id);"""

    cursor.execute(search_users)
    ruas = cursor.fetchall()
    
    quantidade_total_depositos = []
    for rua_deposito in ruas:
        quantidade_total_depositos.append({
            "A1 e A2": rua_deposito['a1'] + rua_deposito['a2'],
            "B": rua_deposito['b'],
            "C": rua_deposito['c'],
            "D1": rua_deposito['d1'],
            "D2": rua_deposito['d2'],
            "E": rua_deposito['e']
        })

    quantidade_total_depositos = {
        "A1 e A2": sum(item["A1 e A2"] for item in quantidade_total_depositos),
        "B": sum(item["B"] for item in quantidade_total_depositos),
        "C": sum(item["C"] for item in quantidade_total_depositos),
        "D1": sum(item["D1"] for item in quantidade_total_depositos),
        "D2": sum(item["D2"] for item in quantidade_total_depositos),
        "E": sum(item["E"] for item in quantidade_total_depositos)}
    
    ruas_totais = {}

    for rua in ruas:
        ruas_totais[rua['deposito_id']] = {
            "rua": rua['rua'],
            "imovel_numero": rua['imovel_numero'],
            "cep": rua['cep'],
            "estado": rua['estado'],
            "bairro": rua['bairro'],
            "A1 e A2": rua['a1'] + rua['a2'],
            "B": rua['b'],
            "C": rua['c'],
            "D1": rua['d1'],
            "D2": rua['d2'],
            "E": rua['e']
        }

    depositos_totais = {
        "quantidade_total_depositos": quantidade_total_depositos,
        "ruas_para_marcacao_no_mapa": ruas_totais
        }
    
    return depositos_totais