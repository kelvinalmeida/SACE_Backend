from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging

logging.basicConfig(level=logging.INFO)

# Lista de campos permitidos para atualização (excluíndo chaves sensíveis/automáticas)
UPDATE_FIELDS = [
    'nome_completo', 'cpf', 'rg', 'data_nascimento', 'email', 
    'telefone_ddd', 'telefone_numero', 'estado', 'municipio', 
    'bairro', 'logradouro', 'numero', 'registro_do_servidor', 
    'cargo', 'situacao_atual', 'data_de_admissao', 'senha' # 'senha' pode ser atualizada
]

@usuario.route('/usuarios/supervisor/<int:supervisor_id>', methods=['PUT'])
@token_required
def update_supervisor(current_user, supervisor_id):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # 1. Obter usuario_id a partir do supervisor_id
        search_user_id_query = """
            SELECT usuario_id 
            FROM supervisor 
            WHERE supervisor_id = %s;
        """
        cursor.execute(search_user_id_query, (supervisor_id,))
        supervisor_data = cursor.fetchone()

        if not supervisor_data:
            return jsonify({"error": "Supervisor não encontrado com o ID especificado."}), 404
        
        usuario_id = supervisor_data['usuario_id']

        # 2. Construir a query de atualização dinamicamente
        data_to_update = request.json
        if not data_to_update:
            return jsonify({"error": "Nenhum dado fornecido para atualização."}), 400

        set_clauses = []
        update_values = []
        
        # Filtra e prepara apenas os campos permitidos
        for field, value in data_to_update.items():
            if field in UPDATE_FIELDS:
                set_clauses.append(f"{field} = %s")
                update_values.append(value)
        
        if not set_clauses:
            return jsonify({"error": "Nenhum campo válido fornecido para atualização."}), 400

        # Adiciona o usuario_id ao final para a cláusula WHERE
        update_values.append(usuario_id)

        update_query = f"""
            UPDATE usuario 
            SET {', '.join(set_clauses)}
            WHERE usuario_id = %s;
        """

        # 3. Executar a atualização
        cursor.execute(update_query, tuple(update_values))
        
        # 4. A atualização de setor_de_atuacao não se aplica a supervisores (mas a lógica de checagem do JSON pode ser incluída se necessário)

        conn.commit()

        return jsonify({
            "status": "success",
            "message": f"Dados do Supervisor com ID {supervisor_id} atualizados com sucesso.",
            "usuario_id": usuario_id
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Erro ao atualizar supervisor {supervisor_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao atualizar dados.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()