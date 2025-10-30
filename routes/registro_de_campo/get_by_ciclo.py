from flask import Flask, request, jsonify, Blueprint, current_app, session
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo
import logging

logging.basicConfig(level=logging.INFO)

@registro_de_campo.route('/registro_de_campo/<int:ano>/<int:ciclo>', methods=['GET'])
@token_required
def get_registro_de_campo_by_ciclo(current_user, ano, ciclo):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = None
    try:
        cursor = conn.cursor()

        # 1. Buscar o ciclo_id a partir do ano e ciclo fornecidos
        search_ciclo_id = """
            SELECT ciclo_id, ano_de_criacao, ciclo 
            FROM ciclos 
            WHERE EXTRACT(YEAR FROM ano_de_criacao)::INTEGER = %s AND ciclo = %s;
        """
        cursor.execute(search_ciclo_id, (ano, ciclo))

        ciclo_info = cursor.fetchone()

        if not ciclo_info:
            return jsonify({"error": f"Ciclo {ciclo} do ano {ano} não encontrado."}), 404
        
        ciclo_id = ciclo_info['ciclo_id']
        ciclo_detalhes = {
            'ciclo_id': ciclo_info['ciclo_id'],
            'ano': int(ciclo_info['ano_de_criacao'].strftime('%Y')),
            'ciclo': ciclo_info['ciclo']
        }

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao buscar ciclo: {str(e)}"}), 500

    try:
        # 2. Query para buscar todos os registros de campo do ciclo encontrado
        search_registros_de_campo = """
            SELECT reg_camp.registro_de_campo_id, reg_camp.imovel_numero, reg_camp.imovel_lado, reg_camp.imovel_categoria_da_localidade, reg_camp.imovel_tipo, reg_camp.imovel_status, reg_camp.imovel_complemento, reg_camp.formulario_tipo, reg_camp.li, reg_camp.pe, reg_camp.t, reg_camp.df, reg_camp.pve, reg_camp.numero_da_amostra, reg_camp.quantiade_tubitos, reg_camp.observacao, reg_camp.area_de_visita_id, reg_camp.agente_id, reg_camp.deposito_id, reg_camp.ciclo_id, usu.nome_completo agente_nome 
            FROM registro_de_campo reg_camp INNER JOIN agente USING(agente_id) INNER JOIN usuario usu USING(usuario_id) 
            WHERE reg_camp.ciclo_id = %s;
        """
        cursor.execute(search_registros_de_campo, (ciclo_id,))
        registro_de_campo = cursor.fetchall()
        
        if not registro_de_campo:
             return jsonify([]), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao buscar registros de campo: {str(e)}"}), 500
    
    # 3. Relacionar dados auxiliares (Depósitos, Larvicidas, etc.)
    
    # --- Área de Visita e Ciclo ---
    try:
        # Reabrir cursor para nova transação (padrão do código existente)
        cursor.close()
        cursor = conn.cursor()

        # Buscar todas as áreas de visita (padrão de get_all.py)
        search_areas_de_visita = """SELECT area_de_visita_id, cep, setor, numero_quarteirao, logadouro, bairro, municipio, estado
                            FROM area_de_visita;"""
        
        cursor.execute(search_areas_de_visita)
        areas_de_visita = cursor.fetchall()

        for reg in registro_de_campo:
            # Enriquecimento com a área de visita
            area_de_visita = next((area for area in areas_de_visita if area['area_de_visita_id'] == reg['area_de_visita_id']), None)
            if area_de_visita:
                area_de_visita = area_de_visita.copy()  
                area_de_visita.pop('area_de_visita_id', None)  
            reg['area_de_visita'] = area_de_visita
            
            # Adiciona os detalhes do ciclo (já obtidos no passo 1)
            reg['ciclo'] = ciclo_detalhes
            
    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao buscar áreas de visita e ciclo: {str(e)}"}), 500

    # --- Depósitos ---
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar depósitos de TODOS os registros de campo no sistema
        search_depositos = """SELECT reg_campo.registro_de_campo_id, a1, a2, b, c, d1, d2, e
                            FROM registro_de_campo reg_campo
                            LEFT JOIN depositos dep USING(deposito_id);"""
        
        cursor.execute(search_depositos)
        depositos = cursor.fetchall()

        for reg in registro_de_campo:
            deposito = next((dep for dep in depositos if dep['registro_de_campo_id'] == reg['registro_de_campo_id']), None)
            if deposito:
                deposito = deposito.copy()  
                deposito.pop('registro_de_campo_id', None) 
            reg['deposito'] = deposito

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao buscar depósitos: {str(e)}"}), 500

 
    # --- Larvicidas ---
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar larvicidas de TODOS os registros de campo no sistema
        search_larvicidas = """SELECT reg_campo.registro_de_campo_id, larvicida_id, quantidade, forma, tipo
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
        return jsonify({"error": f"Erro ao buscar larvicidas: {str(e)}"}), 500
    
    
    # --- Adulticidas ---
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar adulticidas de TODOS os registros de campo no sistema
        search_adulticidas = """SELECT reg_campo.registro_de_campo_id, adulticida_id, quantidade, tipo
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
        return jsonify({"error": f"Erro ao buscar adulticidas: {str(e)}"}), 500
    

    # --- Arquivos ---
    try:
        cursor.close()
        cursor = conn.cursor()

        # Buscar arquivos de TODOS os registros de campo no sistema
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
        return jsonify({"error": f"Erro ao buscar arquivos: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

        return jsonify(registro_de_campo), 200