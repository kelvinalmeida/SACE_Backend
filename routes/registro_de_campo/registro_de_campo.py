from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from token_required import token_required
import json
from werkzeug.utils import secure_filename


registro_de_campo = Blueprint('registro_de_campo', __name__)

def check_required_filds(required_fild):
    for fild in required_fild:
        if fild not in request.form or request.form[fild] is None or request.form[fild].strip() == "":
            return {"error": f"{fild} is required"}
    return False


@registro_de_campo.route('/registro_de_campo', methods=['POST'])
@token_required
def send_registro_de_campo(current_user):

    print("current_user token data:", current_user)
    # Pega o agente_id do token
    try:
        agente_id = current_user['agente_id']
    except Exception as e:
        return jsonify({"error": "Invalid token: É nescessário ser agente para cadastrar registro de campo. Peça para um supervisor cadastrar você."}), 401
    


    check_filds = check_required_filds(['imovel_numero', 'imovel_lado', 'imovel_categoria_da_localidade', 'imovel_tipo', 'imovel_status'])

    if(check_filds):
        return jsonify(check_filds), 400

    imovel_numero = request.form.get('imovel_numero')
    imovel_lado = request.form.get('imovel_lado')
    imovel_categoria_da_localidade = request.form.get('imovel_categoria_da_localidade')
    imovel_tipo = request.form.get('imovel_tipo')
    imovel_status = request.form.get('imovel_status')
    imovel_complemento = request.form.get('imovel_complemento')
    formulario_tipo = request.form.get('formulario_tipo')

    try:
        li = bool(request.form.get('li'))
        pe = bool(request.form.get('pe'))
        t = bool(request.form.get('t'))
        df = bool(request.form.get('df'))
        pve = bool(request.form.get('pve'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input for li, pe, t, df, or pve. They must be boolean values."}), 400

    numero_da_amostra = request.form.get('numero_da_amostra')
    quantiade_tubitos = request.form.get('quantiade_tubitos')
    observacao = request.form.get('observacao')
    area_de_visita_id = request.form.get('area_de_visita_id')

    try:
        a1 = int(request.form.get('a1'))
        a2 = int(request.form.get('a2'))
        b = int(request.form.get('b'))
        c = int(request.form.get('c'))
        d1 = int(request.form.get('d1'))
        d2 = int(request.form.get('d2'))
        e = int(request.form.get('e'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input for a1, a2, b, c, d1, d2, or e. They must be integers."}), 400
    

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    

    
    print(">>>>>>>>>>", area_de_visita_id, agente_id)

    # Query para buscar a área de visita do agente logado
    try:
        cursor = conn.cursor()
        search_agente_area_de_visita = """SELECT area_de_visita_id FROM agente_area_de_visita WHERE agente_id = %s AND area_de_visita_id = %s;"""

        cursor.execute(search_agente_area_de_visita, (agente_id, area_de_visita_id))
        
        area_de_visita_id = cursor.fetchone()

        area_de_visita_id = area_de_visita_id['area_de_visita_id']

    except Exception as e:
        return jsonify({"error": "Agente não está associado a área de visita informada."}), 400
    

    # Inserir Depósito
    try:
        cursor = conn.cursor()
        insir_deposito = """
            INSERT INTO depositos(a1, a2, b, c, d1, d2, e) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) 
            RETURNING deposito_id; 
        """

        # 1. Executa a inserção e a requisição do ID
        # O comando 'execute' retorna None, não o resultado.
        cursor.execute(insir_deposito, (a1, a2, b, c, d1, d2, e))

        # 2. Usa fetchone() para obter a linha de resultado (que contém o ID)
        # Como RETURNING retorna uma única linha com uma única coluna (deposito_id),
        # fetchone() retorna uma tupla ou lista, dependendo do driver.
        resultado = cursor.fetchone()

        # 3. Faz o commit da transação
        conn.commit()

        # 4. Extrai o ID
        if resultado:
            deposito_id = resultado["deposito_id"]
        else:
            conn.rollback()
            raise Exception("Falha ao obter o ID do depósito após a inserção.")
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    
    #Inserir Registro de Campo
    try:
        cursor = conn.cursor()
        inserir_registro_de_campo = """INSERT INTO registro_de_campo(
            imovel_numero, imovel_lado, imovel_categoria_da_localidade, imovel_tipo, imovel_status, imovel_complemento, formulario_tipo, li, pe, t, df, pve, numero_da_amostra, quantiade_tubitos, observacao, area_de_visita_id, agente_id, deposito_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING registro_de_campo_id; """
        
        cursor.execute(inserir_registro_de_campo, (imovel_numero, imovel_lado, imovel_categoria_da_localidade, imovel_tipo, imovel_status, imovel_complemento, formulario_tipo, li, pe, t, df, pve, numero_da_amostra, quantiade_tubitos, observacao, area_de_visita_id, agente_id, deposito_id))

        registro_de_campo_id = cursor.fetchone()
        registro_de_campo_id = registro_de_campo_id['registro_de_campo_id']
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    

    # Inserir Larvicidas
    try:
        # [{"tipo": "temefos", "forma": "g", "quant": 10}, {"tipo": "adulti", ...}]
        cursor = conn.cursor()
        larvicidas = json.loads(request.form.get('larvicidas', '[]'))

        for larvicida in larvicidas:
            tipo = larvicida.get('tipo')
            forma = larvicida.get('forma')
            quantidade = larvicida.get('quantidade')
            registro_de_campo_id = registro_de_campo_id

            inserir_larvicidas = """INSERT INTO larvicida(tipo, forma, quantidade, registro_de_campo_id) VALUES (%s, %s, %s, %s);"""

            print("Larvicidas: ", tipo, forma, quantidade, registro_de_campo_id)

            cursor.execute(inserir_larvicidas, (tipo, forma, quantidade, registro_de_campo_id))
        
        conn.commit()
            
    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500
    


    # Inserir Adulticidas
    try:
        # [{"tipo": "temefos", "forma": "g", "quant": 10}, {"tipo": "adulti", ...}]
        cursor = conn.cursor()
        adulticidas = json.loads(request.form.get('adulticidas', '[]'))

        for adulticida in adulticidas:
            tipo = adulticida.get('tipo')
            quantidade = adulticida.get('quantidade')
            registro_de_campo_id = registro_de_campo_id

            inserir_adulticidas = """INSERT INTO adulticida(tipo, quantidade, registro_de_campo_id) VALUES (%s, %s, %s);"""

            print("adulticida: ", tipo, quantidade, registro_de_campo_id)

            cursor.execute(inserir_adulticidas, (tipo, quantidade, registro_de_campo_id))
        
        conn.commit()

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500
    
    try:
        # [{"tipo": "temefos", "forma": "g", "quant": 10}, {"tipo": "adulti", ...}]
        # cursor = conn.cursor()
        # arquivos = json.loads(request.form.get('arquivos', '[]'))
        files = {}
        count = 1
        for file in request.files.getlist('files'):
            files[f"Arquivo {count}"] = secure_filename(file.filename)
            count += 1

            arquivo_nome = secure_filename(file.filename)

            inserir_arquivos = """INSERT INTO registro_de_campo_arquivos(arquivo_nome, registro_de_campo_id) VALUES (%s, %s);""" 

            print("inserir_arquivos: ", arquivo_nome, registro_de_campo_id)

            cursor.execute(inserir_arquivos, (arquivo_nome, registro_de_campo_id))

            file.save(f'uploads/registro_de_campo_arquivos/reg_de_campo_id_{registro_de_campo_id}_{arquivo_nome}')
        
        conn.commit()
    finally:
        conn.rollback()
        conn.close()
        cursor.close()


    return jsonify({
        'status': 'success',
        'message': 'Registro de campo recebido com sucesso',
        'data': {
            'imovel_numero': imovel_numero,
            'imovel_lado': imovel_lado,
            'imovel_categoria_da_localidade': imovel_categoria_da_localidade,
            'imovel_tipo': imovel_tipo,
            'imovel_status': imovel_status,
            'imovel_complemento': imovel_complemento,
            'formulario_tipo': formulario_tipo,
            'li': li,
            'pe': pe,
            't': t,
            'df': df,
            'pve': pve,
            'numero_da_amostra': numero_da_amostra,
            'quantiade_tubitos': quantiade_tubitos,
            'observacao': observacao,
            'area_de_visita_id': area_de_visita_id,
            'agente_id': agente_id,
            'a1': a1,
            'a2': a2,
            'b': b,
            'c': c,
            'd1': d1,
            'd2': d2,
            'e': e,
            'deposito_id': deposito_id,
            'files': files
        }
    })



@registro_de_campo.route('/registro_de_campo', methods=['GET'])
@token_required
def get_registro_de_campo(current_user):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # Query para buscar todos os usuários agentes relacionando ao registro de campo
        search_registros_de_campo = """SELECT reg_camp.registro_de_campo_id, reg_camp.imovel_numero, reg_camp.imovel_lado, reg_camp.imovel_categoria_da_localidade, reg_camp.imovel_tipo, reg_camp.imovel_status, reg_camp.imovel_complemento, reg_camp.formulario_tipo, reg_camp.li, reg_camp.pe, reg_camp.t, reg_camp.df, reg_camp.pve, reg_camp.numero_da_amostra, reg_camp.quantiade_tubitos, reg_camp.observacao, reg_camp.area_de_visita_id, reg_camp.agente_id, reg_camp.deposito_id, usu.nome_completo agente_nome FROM registro_de_campo reg_camp INNER JOIN agente USING(agente_id) INNER JOIN usuario usu USING(usuario_id);"""

        cursor.execute(search_registros_de_campo)
        registro_de_campo = cursor.fetchall()

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    

    # relacionar registro de campo a sua area de visita
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar áreas de visita
        search_areas_de_visita = """SELECT area_de_visita.area_de_visita_id, area_de_visita.cep, area_de_visita.setor, area_de_visita.numero_quarteirao, area_de_visita.logadouro, area_de_visita.bairro, area_de_visita.municipio, area_de_visita.estado
                            FROM registro_de_campo reg_campo
                            LEFT JOIN area_de_visita USING(area_de_visita_id);"""
        
        cursor.execute(search_areas_de_visita)
        areas_de_visita = cursor.fetchall()

        area_de_visita_id = None

        for reg in registro_de_campo:
            area_de_visita = next((area for area in areas_de_visita if area['area_de_visita_id'] == reg['area_de_visita_id']), None)
            if area_de_visita:
                area_de_visita = area_de_visita.copy()  # Faz uma cópia para não alterar o original
                area_de_visita_id = area_de_visita['area_de_visita_id']
                area_de_visita.pop('area_de_visita_id', None)  # Remove a chave se existir
            reg['area_de_visita'] = area_de_visita
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar depósitos
        search_depositos = """SELECT reg_campo.registro_de_campo_id, a1, a2, b, c, d1, d2, e
                            FROM registro_de_campo reg_campo
                            LEFT JOIN depositos dep USING(deposito_id);"""
        
        cursor.execute(search_depositos)
        depositos = cursor.fetchall()

        for reg in registro_de_campo:
            deposito = next((dep for dep in depositos if dep['registro_de_campo_id'] == reg['registro_de_campo_id']), None)
            if deposito:
                deposito = deposito.copy()  # Faz uma cópia para não alterar o original
                deposito.pop('registro_de_campo_id', None)  # Remove a chave se existir
            reg['deposito'] = deposito

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    try:
        cursor.close()
        cursor = conn.cursor()

        # buscar ciclo da área de visita
        search_ciclo_area_de_visita = """SELECT ciclo_id ciclo, ano_de_criacao FROM ciclos INNER JOIN ciclo_area_de_visita USING(ciclo_id) INNER JOIN area_de_visita USING(area_de_visita_id) WHERE ativo = true AND area_de_visita_id = %s;"""
        cursor.execute(search_ciclo_area_de_visita, (area_de_visita_id,))
        ciclo_area_de_visita = cursor.fetchone()

        for reg in registro_de_campo:
            reg['ciclo'] = ciclo_area_de_visita

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
 
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar larvicidas
        search_larvicidas = """SELECT reg_campo.registro_de_campo_id, quantidade, forma, tipo
                            FROM registro_de_campo reg_campo
                            LEFT JOIN larvicida larv USING(registro_de_campo_id);"""
        
        cursor.execute(search_larvicidas)
        larvicidas = cursor.fetchall()

        for reg in registro_de_campo:
            larvicidas_reg = [larv.copy() for larv in larvicidas if larv['registro_de_campo_id'] == reg
            ['registro_de_campo_id'] and larv['tipo'] is not None]

            
            for larv in larvicidas_reg:
                larv.pop('registro_de_campo_id', None)
            

            reg['larvicidas'] = larvicidas_reg

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar adulticidas
        search_adulticidas = """SELECT reg_campo.registro_de_campo_id, quantidade, tipo
                            FROM registro_de_campo reg_campo
                            LEFT JOIN adulticida adult USING(registro_de_campo_id);"""
        
        cursor.execute(search_adulticidas)
        adulticidas = cursor.fetchall()

        for reg in registro_de_campo:
            adulticidas_reg = [adu.copy() for adu in adulticidas if adu['registro_de_campo_id'] == reg['registro_de_campo_id'] and adu['tipo'] is not None]
            for adu in adulticidas_reg:
                adu.pop('registro_de_campo_id', None)

            reg['adulticidas'] = adulticidas_reg

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    

    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar arquivos
        search_arquivos = """SELECT reg_campo.registro_de_campo_id, arquivo_nome, registro_de_campo_arquivo_id
                            FROM registro_de_campo reg_campo
                            LEFT JOIN registro_de_campo_arquivos arquiv USING(registro_de_campo_id);"""
        
        cursor.execute(search_arquivos)
        arquivos = cursor.fetchall()

        for reg in registro_de_campo:
            arquivos_reg = [arq.copy() for arq in arquivos if arq['registro_de_campo_id'] == reg['registro_de_campo_id'] and arq['arquivo_nome'] is not None]
            for arq in arquivos_reg:
                arq.pop('registro_de_campo_id', None)

            reg['arquivos'] = arquivos_reg
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
        cursor.close()

        return jsonify(registro_de_campo), 200
    

@registro_de_campo.route('/registro_de_campo/<int:registro_de_campo_id>', methods=['GET'])
@token_required
def get_one_registro_de_campo(current_user, registro_de_campo_id):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    

    try:
        cursor = conn.cursor()

        # Query para buscar todos os usuários agentes relacionando ao registro de campo
        search_registros_de_campo = """SELECT reg_camp.registro_de_campo_id, reg_camp.imovel_numero, reg_camp.imovel_lado, reg_camp.imovel_categoria_da_localidade, reg_camp.imovel_tipo, reg_camp.imovel_status, reg_camp.imovel_complemento, reg_camp.formulario_tipo, reg_camp.li, reg_camp.pe, reg_camp.t, reg_camp.df, reg_camp.pve, reg_camp.numero_da_amostra, reg_camp.quantiade_tubitos, reg_camp.observacao, reg_camp.area_de_visita_id, reg_camp.agente_id, reg_camp.deposito_id, usu.nome_completo agente_nome FROM registro_de_campo reg_camp INNER JOIN agente USING(agente_id) INNER JOIN usuario usu USING(usuario_id) WHERE registro_de_campo_id = %s;"""

        cursor.execute(search_registros_de_campo, (registro_de_campo_id,))
        registro_de_campo = cursor.fetchall()

        if not registro_de_campo:
            return jsonify({"error": "Registro de campo not found"}), 404

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    

    # relacionar registro de campo a sua area de visita
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar áreas de visita
        search_areas_de_visita = """SELECT area_de_visita.area_de_visita_id, area_de_visita.cep, area_de_visita.setor, area_de_visita.numero_quarteirao, area_de_visita.logadouro, area_de_visita.bairro, area_de_visita.municipio, area_de_visita.estado
                            FROM registro_de_campo reg_campo
                            LEFT JOIN area_de_visita USING(area_de_visita_id);"""
        
        cursor.execute(search_areas_de_visita)
        areas_de_visita = cursor.fetchall()

        area_de_visita_id = None

        for reg in registro_de_campo:
            area_de_visita = next((area for area in areas_de_visita if area['area_de_visita_id'] == reg['area_de_visita_id']), None)
            if area_de_visita:
                area_de_visita = area_de_visita.copy()  # Faz uma cópia para não alterar o original
                area_de_visita_id = area_de_visita['area_de_visita_id']
                area_de_visita.pop('area_de_visita_id', None)  # Remove a chave se existir
            reg['area_de_visita'] = area_de_visita
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    try:
        cursor.close()
        cursor = conn.cursor()

        # buscar ciclo da área de visita
        search_ciclo_area_de_visita = """SELECT ciclo_id ciclo, ano_de_criacao FROM ciclos INNER JOIN ciclo_area_de_visita USING(ciclo_id) INNER JOIN area_de_visita USING(area_de_visita_id) WHERE ativo = true AND area_de_visita_id = %s;"""
        cursor.execute(search_ciclo_area_de_visita, (area_de_visita_id,))
        ciclo_area_de_visita = cursor.fetchone()

        for reg in registro_de_campo:
            reg['ciclo'] = ciclo_area_de_visita

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar depósitos
        search_depositos = """SELECT reg_campo.registro_de_campo_id, a1, a2, b, c, d1, d2, e
                            FROM registro_de_campo reg_campo
                            LEFT JOIN depositos dep USING(deposito_id);"""
        
        cursor.execute(search_depositos)
        depositos = cursor.fetchall()

        for reg in registro_de_campo:
            deposito = next((dep for dep in depositos if dep['registro_de_campo_id'] == reg['registro_de_campo_id']), None)
            if deposito:
                deposito = deposito.copy()  # Faz uma cópia para não alterar o original
                deposito.pop('registro_de_campo_id', None)  # Remove a chave se existir
            reg['deposito'] = deposito

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
 
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar larvicidas
        search_larvicidas = """SELECT reg_campo.registro_de_campo_id, quantidade, forma, tipo
                            FROM registro_de_campo reg_campo
                            LEFT JOIN larvicida larv USING(registro_de_campo_id);"""
        
        cursor.execute(search_larvicidas)
        larvicidas = cursor.fetchall()

        for reg in registro_de_campo:
            larvicidas_reg = [larv.copy() for larv in larvicidas if larv['registro_de_campo_id'] == reg
            ['registro_de_campo_id'] and larv['tipo'] is not None]

            
            for larv in larvicidas_reg:
                larv.pop('registro_de_campo_id', None)
            

            reg['larvicidas'] = larvicidas_reg

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar adulticidas
        search_adulticidas = """SELECT reg_campo.registro_de_campo_id, quantidade, tipo
                            FROM registro_de_campo reg_campo
                            LEFT JOIN adulticida adult USING(registro_de_campo_id);"""
        
        cursor.execute(search_adulticidas)
        adulticidas = cursor.fetchall()

        for reg in registro_de_campo:
            adulticidas_reg = [adu.copy() for adu in adulticidas if adu['registro_de_campo_id'] == reg['registro_de_campo_id'] and adu['tipo'] is not None]
            for adu in adulticidas_reg:
                adu.pop('registro_de_campo_id', None)

            reg['adulticidas'] = adulticidas_reg

    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    

    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar arquivos
        search_arquivos = """SELECT reg_campo.registro_de_campo_id, arquivo_nome, registro_de_campo_arquivo_id
                            FROM registro_de_campo reg_campo
                            LEFT JOIN registro_de_campo_arquivos arquiv USING(registro_de_campo_id);"""
        
        cursor.execute(search_arquivos)
        arquivos = cursor.fetchall()

        for reg in registro_de_campo:
            arquivos_reg = [arq.copy() for arq in arquivos if arq['registro_de_campo_id'] == reg['registro_de_campo_id'] and arq['arquivo_nome'] is not None]
            for arq in arquivos_reg:
                arq.pop('registro_de_campo_id', None)

            reg['arquivos'] = arquivos_reg
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
        cursor.close()

        return jsonify(registro_de_campo[0]), 200