from flask import jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import ciclos
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

@ciclos.route('/ciclos/status', methods=['GET'])
@token_required
def get_ciclo_status(current_user):

    conn = None
    cursor = None
    try:
        # 1. Conexão com o banco de dados
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
        
        cursor = conn.cursor()

        # 2. Consulta para encontrar o ciclo ATIVO
        # Buscamos o último ciclo que está marcado como ativo, caso exista mais de um por erro.
        search_active_ciclo_query = """
            SELECT 
                ciclo_id, 
                EXTRACT(YEAR FROM ano_de_criacao)::INTEGER AS ano, 
                ciclo, 
                ativo
            FROM 
                ciclos 
            WHERE 
                ativo = True 
            ORDER BY 
                ano_de_criacao DESC, ciclo DESC
            LIMIT 1;
        """
        cursor.execute(search_active_ciclo_query)
        ciclo_ativo_info = cursor.fetchone()

        # 3. Determinar o status
        if ciclo_ativo_info:
            return jsonify({
                "status": "ativo",
                "detalhes": {
                    "ciclo_id": ciclo_ativo_info['ciclo_id'],
                    "ano": ciclo_ativo_info['ano'],
                    "ciclo_numero": ciclo_ativo_info['ciclo']
                }
            }), 200
        else:
            return jsonify({
                "status": "inativo",
                "detalhes": "Nenhum ciclo ativo encontrado. É necessário iniciar um novo ciclo."
            }), 200

    except Exception as e:
        logging.error(f"Erro ao buscar status do ciclo: {e}")
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação."}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()