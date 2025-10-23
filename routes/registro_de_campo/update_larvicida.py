from flask import Flask, request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import registro_de_campo


@registro_de_campo.route('/larvicida/<int:larvicida_id>', methods=['PUT'])
@token_required
def update_larvicida(current_user, larvicida_id):

    
    tipo = request.form.get('tipo')
    forma = request.form.get('forma')

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

        update_larvicida = """UPDATE larvicida SET tipo = %s, forma = %s, quantidade = %s WHERE larvicida_id = %s;"""
        cursor.execute(update_larvicida, (tipo, forma, quantidade, larvicida_id))
        conn.commit()


        return jsonify({
            'status': 'success',
            'message': 'Larvicida atualizado com sucesso',
            'data': {
                'larvicida_id': larvicida_id,
                'tipo': tipo,
                'forma': forma,
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