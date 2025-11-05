from flask import jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import doencas_confirmadas_bp
import logging

logging.basicConfig(level=logging.INFO)

@doencas_confirmadas_bp.route('/doencas_confirmadas/<int:doenca_id>', methods=['GET'])
@token_required
def get_doenca_confirmada_by_id(current_user, doenca_id):
    """
    Busca um registro de doença confirmada pelo ID.
    Requer autenticação.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()
        
        query = """
            SELECT dc.*, c.ciclo, EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER AS ano 
            FROM doencas_confirmadas dc
            JOIN ciclos c ON dc.ciclo_id = c.ciclo_id
            WHERE dc.doenca_confirmada_id = %s;
        """
        cursor.execute(query, (doenca_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Registro não encontrado."}), 404
            
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Erro ao buscar doença confirmada por ID: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()