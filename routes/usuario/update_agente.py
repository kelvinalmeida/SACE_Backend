from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging

logging.basicConfig(level=logging.INFO)

# Lista de campos permitidos para atualização no usuário
UPDATE_FIELDS = [
    'nome_completo', 'cpf', 'rg', 'data_nascimento', 'email', 
    'telefone_ddd', 'telefone_numero', 'estado', 'municipio', 
    'bairro', 'logradouro', 'numero', 'registro_do_servidor', 
    'cargo', 'situacao_atual', 'data_de_admissao', 'senha'
]

@usuario.route('/usuarios/agente/<int:agente_id>', methods=['PUT'])
@token_required
def update_agente(current_user, agente_id):
    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

    cursor = None
    try:
        cursor = conn.cursor()

        # 1. Obter usuario_id a partir do agente_id
        search_user_id_query = """
            SELECT usuario_id 
            FROM agente 
            WHERE agente_id = %s;
        """
        cursor.execute(search_user_id_query, (agente_id,))
        agente_data = cursor.fetchone()

        if not agente_data:
            return jsonify({"error": "Agente não encontrado com o ID especificado."}), 404
        
        usuario_id = agente_data['usuario_id']

        # 2. Construir a query de atualização de dados da tabela 'usuario'
        data_to_update = request.json
        if not data_to_update:
            return jsonify({"error": "Nenhum dado fornecido para atualização."}), 400

        set_clauses = []
        update_values = []
        
        for field, value in data_to_update.items():
            if field in UPDATE_FIELDS:
                set_clauses.append(f"{field} = %s")
                update_values.append(value)
        
        if set_clauses:
            update_values.append(usuario_id)
            update_query = f"""
                UPDATE usuario 
                SET {', '.join(set_clauses)}
                WHERE usuario_id = %s;
            """
            cursor.execute(update_query, tuple(update_values))
        
        # 3. Atualizar as áreas de atuação (setor_de_atuacao) - OPCIONAL
        # Se o campo 'setor_de_atuacao' for fornecido, ele substitui as áreas anteriores.
        if 'setor_de_atuacao' in data_to_update:
            areas_ids = data_to_update['setor_de_atuacao']
            
            if not isinstance(areas_ids, list):
                 return jsonify({"error": "O campo 'setor_de_atuacao' deve ser uma lista de IDs de área de visita."}), 400

            # 3a. Deletar associações existentes
            delete_areas_query = "DELETE FROM agente_area_de_visita WHERE agente_id = %s;"
            cursor.execute(delete_areas_query, (agente_id,))

            # 3b. Inserir novas associações
            if areas_ids:
                insert_area_query = "INSERT INTO agente_area_de_visita(agente_id, area_de_visita_id) VALUES(%s, %s);"
                for area_id in areas_ids:
                    # NOTA: Aqui, qualquer ID de área inválido causará uma exceção de chave estrangeira
                    cursor.execute(insert_area_query, (agente_id, area_id))
        
        # 4. Commit de todas as alterações
        conn.commit()

        return jsonify({
            "status": "success",
            "message": f"Dados do Agente com ID {agente_id} atualizados com sucesso.",
            "usuario_id": usuario_id
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()
        # Captura erros de chave estrangeira (area_de_visita_id inválida)
        if 'foreign key' in str(e).lower() or 'not present in table' in str(e).lower():
            detail_error = "Um ou mais IDs de área de visita em 'setor_de_atuacao' são inválidos ou não existem."
            return jsonify({"error": "Erro de referência de dados.", "details": detail_error}), 400
            
        logging.error(f"Erro ao atualizar agente {agente_id}: {e}", exc_info=True)
        return jsonify({"error": "Erro interno ao atualizar dados.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()