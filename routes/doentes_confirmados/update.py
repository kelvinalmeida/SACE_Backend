from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import doentes_confirmados_bp
import logging

logging.basicConfig(level=logging.INFO)

@doentes_confirmados_bp.route('/doentes_confirmados/<int:doenca_id>', methods=['PUT'])
@token_required
def update_doenca_confirmada(current_user, doenca_id):
    """
    Atualiza um registro de doença confirmada.
    Requer permissão de supervisor.
    """
    if current_user.get("nivel_de_acesso") != "supervisor":
        return jsonify({"error": "Acesso negado: Apenas supervisores podem atualizar."}), 403

    data = request.json
    # Validação dos campos NOT NULL
    if not data.get('tipo_da_doenca') or not data.get('rua'):
        return jsonify({"error": "Campos 'tipo_da_doenca' e 'rua' são obrigatórios."}), 400

    conn = None
    cursor = None
    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        cursor = conn.cursor()
        
        update_sql = """
            UPDATE doentes_confirmados
            SET nome = %s, tipo_da_doenca = %s, rua = %s, numero = %s, bairro = %s
            WHERE doente_confirmado_id = %s
            RETURNING doente_confirmado_id;
        """
        values = (
            data.get('nome'),
            data['tipo_da_doenca'],
            data['rua'],
            data.get('numero'),
            data.get('bairro'),
            doenca_id
        )
        
        cursor.execute(update_sql, values)
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "Registro não encontrado."}), 404
        
        conn.commit()
        return jsonify({"message": "Registro atualizado com sucesso.", "id": result['doente_confirmado_id']}), 200

    except Exception as e:
        if conn: conn.rollback()
        logging.error(f"Erro ao atualizar doença confirmada: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao atualizar dados.", "details": str(e)}), 500
    
    finally:
        if cursor: cursor.close()
        if conn: conn.close()