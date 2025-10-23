from flask import Flask, request, jsonify, Blueprint, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo

@registro_de_campo.route('/adulticida/<int:adulticida_id>', methods=['PUT'])
@token_required
def update_adulticida(current_user, adulticida_id):
        
    tipo = request.form.get('tipo')

    try:
        quantidade = request.form.get('quantidade')
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid input for quantidade. They must be integers."}), 400
    

    # Conexão com o banco de dados
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])

    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    

    # verificando se existe algum ciclo ativo
    try:
        cursor = conn.cursor()

        update_larvicida = """UPDATE adulticida SET tipo = %s, quantidade = %s WHERE adulticida_id = %s;"""
        cursor.execute(update_larvicida, (tipo, quantidade, adulticida_id))
        conn.commit()


        return jsonify({
            'status': 'success',
            'message': 'Adulticida atualizado com sucesso',
            'data': {
                'adulticida_id': adulticida_id,
                'tipo': tipo,
                'quantidade': quantidade
            }
        }), 200

    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        return jsonify({"error": f"Erro interno no servidor: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()