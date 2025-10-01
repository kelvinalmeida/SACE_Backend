from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import area_para_visita
import json
import logging

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@area_para_visita.route('/varias_areas_de_visita', methods=['POST'])
@token_required
def criar_varias_areas_de_visita(current_user):
    # 1. Validação de Supervisor
    if not current_user or current_user.get("supervisor_id") is None or current_user.get("nivel_de_acesso") not in ["supervisor"]: 
        return jsonify({"error": "É necessário ser supervisor para cadastrar áreas."}), 403
    
    supervisor_id = current_user.get("supervisor_id")
    
    # 2. Receber dados JSON
    # Esperamos que o corpo da requisição seja um array JSON de objetos de área
    try:
        areas_data = request.json
        if not isinstance(areas_data, list):
            return jsonify({"error": "Os dados devem ser uma lista JSON de áreas."}), 400
        if not areas_data:
             return jsonify({"error": "A lista de áreas não pode estar vazia."}), 400
    except Exception as e:
        return jsonify({"error": f"Formato JSON inválido: {e}"}), 400

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    inserted_areas_ids = []
    
    try:
        cursor = conn.cursor()
        
        # SQL base para inserção
        insert_area_sql = """
            INSERT INTO area_de_visita (supervisor_id, cep, setor, numero_quarteirao, estado, municipio, bairro, logadouro) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING area_de_visita_id;
        """
        
        for index, area in enumerate(areas_data):
            # Validação básica de campos obrigatórios
            print('>>>>>>>>>>>>>> ', area['numero_quarteirao'])
            
            required_fields = ['cep', 'setor', 'numero_quarteirao', 'estado', 'municipio', 'bairro', 'logadouro']
            for field in required_fields:
                if field not in area:
                    conn.rollback()
                    return jsonify({"error": f"Campo obrigatório '{field}' faltando na área {index + 1}."}), 400
            
            # Validação de tipo (numero_quarteirao)
            try:
                numero_quarteirao = int(area['numero_quarteirao'])
            except (TypeError, ValueError):
                conn.rollback()
                return jsonify({"error": f"Número do quarteirão inválido na área {index + 1}."}), 400

            # Dados para a query
            values = (
                supervisor_id,
                area['cep'],
                area['setor'],
                numero_quarteirao,
                area['estado'],
                area['municipio'],
                area['bairro'],
                area['logadouro']
            )

            # Executa a inserção
            cursor.execute(insert_area_sql, values)
            
            # Obtém o ID gerado e armazena
            area_id = cursor.fetchone()["area_de_visita_id"]
            inserted_areas_ids.append(area_id)
        
        # Commit de todas as inserções
        conn.commit()
        
        return jsonify({
            "message": f"{len(inserted_areas_ids)} Áreas de visita criadas com sucesso.",
            "supervisor_id": supervisor_id,
            "areas_criadas_ids": inserted_areas_ids
        }), 201

    except Exception as e:
        # Rollback em caso de qualquer erro de banco de dados
        logging.error(f"Erro durante a inserção em lote: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": f"Erro de banco de dados: {str(e)}"}), 500
    
    finally:
        if conn:
            cursor.close()
            conn.close()
