from flask import jsonify, current_app
from db import create_connection
# Rota pública, não requer token
from .bluprint import nudges_bp
import logging

logging.basicConfig(level=logging.INFO)

@nudges_bp.route('/nudges/<int:nudges_id>', methods=['GET'])
def get_nudge_by_id(nudges_id):
    """
    Busca um nudge específico pelo ID.
    Rota pública.
    """
    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()
        
        query = "SELECT * FROM nudges WHERE nudges_id = %s;"
        
        cursor.execute(query, (nudges_id,))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Nudge não encontrado."}), 404
            
        return jsonify(result), 200

    except Exception as e:
        logging.error(f"Erro ao buscar nudge por ID: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()