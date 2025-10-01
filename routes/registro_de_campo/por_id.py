from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from routes.registro_de_campo.post_one_registro_de_campo import registro_de_campo

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