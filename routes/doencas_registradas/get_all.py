from flask import jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import doencas_confirmadas_bp
import logging

logging.basicConfig(level=logging.INFO)

@doencas_confirmadas_bp.route('/doencas_confirmadas', methods=['GET'])
@token_required
def get_all_doencas_confirmadas(current_user):
    """
    Lista todos os registros de doenças confirmadas.
    Requer autenticação.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()
        
        # Junta com a tabela ciclos para obter o ano e número do ciclo
        query = """
            SELECT dc.*, c.ciclo, EXTRACT(YEAR FROM c.ano_de_criacao)::INTEGER AS ano 
            FROM doencas_confirmadas dc
            JOIN ciclos c ON dc.ciclo_id = c.ciclo_id
            ORDER BY dc.doenca_confirmada_id DESC;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        
        return jsonify(results), 200

    except Exception as e:
        logging.error(f"Erro ao buscar doenças confirmadas: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()