from flask import jsonify, current_app
from db import create_connection
# Rota pública, não requer token
from .bluprint import nudges_bp
import logging

logging.basicConfig(level=logging.INFO)

@nudges_bp.route('/nudges', methods=['GET'])
def get_all_nudges():
    """
    Lista todos os nudges cadastrados.
    Rota pública.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()
        
        query = "SELECT * FROM nudges ORDER BY nudges_id DESC;"
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        return jsonify(results), 200

    except Exception as e:
        logging.error(f"Erro ao buscar todos os nudges: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()