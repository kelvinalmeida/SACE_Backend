from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from .bluprint import usuario
import logging

# Importando a exceção específica para tratar possíveis erros de transação
from psycopg2 import errors

# Configuração básica de log para exibir erros
logging.basicConfig(level=logging.INFO)

@usuario.route('/usuarios', methods=['POST'])
@token_required
def criar_varios_usuarios(current_user):
    # 1. Validação de Supervisor
    if not current_user or current_user.get("supervisor_id") is None or current_user.get("nivel_de_acesso") not in ["supervisor"]: 
        return jsonify({"error": "É necessário ser supervisor para cadastrar usuários."}), 403
    
    supervisor_id = current_user.get("supervisor_id")
    
    # 2. Receber dados JSON
    try:
        usuarios_data = request.json
        if not isinstance(usuarios_data, list):
            return jsonify({"error": "Os dados devem ser uma lista JSON de usuários."}), 400
        if not usuarios_data:
             return jsonify({"error": "A lista de usuários não pode estar vazia."}), 400
    except Exception as e:
        return jsonify({"error": f"Formato JSON inválido: {e}"}), 400

    conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    inserted_usuarios_ids = []
    
    try:
        cursor = conn.cursor()
        
        # SQL para verificar a unicidade de CPF/Email
        check_unique_sql = """
            SELECT cpf, email FROM usuario WHERE cpf = %s OR email = %s;
        """
     
        # Inserção na tabela 'usuario'
        insert_usuario_sql = """
            INSERT INTO usuario (
                nome_completo, cpf, rg, data_nascimento, email, telefone_ddd, telefone_numero, 
                estado, municipio, bairro, logradouro, numero, registro_do_servidor, 
                cargo, situacao_atual, data_de_admissao, senha, nivel_de_acesso
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING usuario_id;
        """
        
        for index, user_data in enumerate(usuarios_data):
            # Validação básica de campos obrigatórios (mantida)
            required_fields = ['nome_completo', 'cpf', 'data_nascimento', 'email', 'telefone_ddd', 
                               'telefone_numero', 'estado', 'municipio', 'bairro', 'logradouro', 
                               'numero', 'registro_do_servidor', 'cargo', 'situacao_atual', 
                               'data_de_admissao', 'senha', 'nivel_de_acesso']

            for field in required_fields:
                if field not in user_data:
                    conn.rollback()
                    return jsonify({"error": f"Campo obrigatório '{field}' faltando no usuário {index + 1}."}), 400
            
            # Validação e conversão de tipos (mantida)
            try:
                numero = int(user_data['numero'])
                telefone_ddd = int(user_data['telefone_ddd'])
                # Garante que situacao_atual seja um booleano de forma segura
                situacao_atual = user_data['situacao_atual'] if isinstance(user_data['situacao_atual'], bool) else bool(user_data['situacao_atual'])
                
            except (TypeError, ValueError):
                conn.rollback()
                return jsonify({"error": f"Tipo de dado inválido para 'numero', 'telefone_ddd' ou 'situacao_atual' no usuário {index + 1}."}), 400

            # 3. PRÉ-VERIFICAÇÃO DE CPF E EMAIL
            cpf_check = user_data['cpf']
            email_check = user_data['email']
            
            cursor.execute(check_unique_sql, (cpf_check, email_check))
            existing_user = cursor.fetchone()
            
            if existing_user:
                error_msg = f"CPF ou Email já cadastrado no usuário {index + 1}."
                
                # Se o erro veio de um CPF já existente, podemos especificar
                if existing_user['cpf'] == cpf_check:
                    error_msg = f"CPF '{cpf_check}' já cadastrado."
                # Se o erro veio de um Email já existente, podemos especificar
                elif existing_user['email'] == email_check:
                    error_msg = f"Email '{email_check}' já cadastrado."
                    
                conn.rollback()
                return jsonify({"error": error_msg}), 409 # 409 Conflict

            # 4. Execução da Inserção de Usuário
            values = (
                user_data['nome_completo'], user_data['cpf'], user_data.get('rg'), user_data['data_nascimento'], 
                user_data['email'], telefone_ddd, user_data['telefone_numero'], user_data['estado'], 
                user_data['municipio'], user_data['bairro'], user_data['logradouro'], numero, 
                user_data['registro_do_servidor'], user_data['cargo'], situacao_atual, 
                user_data['data_de_admissao'], user_data['senha'], user_data['nivel_de_acesso']
            )

            # Inserção na tabela principal
            cursor.execute(insert_usuario_sql, values)
            usuario_id = cursor.fetchone()["usuario_id"]
            inserted_usuarios_ids.append(usuario_id)

            # 5. Criação de Agente ou Supervisor
            
            # CORREÇÃO: Nível de acesso para Agente é 'usuario' (não 'agante')
            agente_id = None
            if user_data['nivel_de_acesso'] == 'agente':
                inserir_agente = """INSERT INTO agente(usuario_id) VALUES (%s) RETURNING agente_id;"""
                cursor.execute(inserir_agente, (usuario_id,))
                agente_id = cursor.fetchone()['agente_id']

                # cadastrando o agente a area de visita
                try:
                    inserir_agente_area_de_visita = """INSERT INTO agente_area_de_visita(agente_id, area_de_visita_id) VALUES(%s, %s)"""

                    for id_area in user_data['setor_de_atuacao']:
                        cursor.execute(inserir_agente_area_de_visita, (agente_id, id_area))
                        print(agente_id, id_area)
                except Exception as e:
                    conn.rollback()
                    cursor.close()
                    conn.close()
                    # return jsonify({"erro": str(e)})
                    return jsonify({"erro": 'ids da area_de_visita no setor de atuacao estão incorretos!'})
                
            elif user_data['nivel_de_acesso'] == 'supervisor':
                inserir_supervisor = """INSERT INTO supervisor(usuario_id) VALUES (%s) RETURNING supervisor_id;"""
                cursor.execute(inserir_supervisor, (usuario_id,))

        
        # 6. Commit de todas as inserções
        conn.commit()
        
        return jsonify({
            "message": f"{len(inserted_usuarios_ids)} Usuários criados com sucesso.",
            "supervisor_criador_id": supervisor_id,
            "usuarios_criados_ids": inserted_usuarios_ids
        }), 201

    except errors.UniqueViolation as e:
        # Captura de exceção do Postgres (caso a pré-verificação falhe por algum motivo, como concorrência)
        logging.error(f"Erro de violação de unicidade do Postgres: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": "Um dos usuários já existe no banco de dados (CPF/Email duplicado)."}), 409
        
    except Exception as e:
        # Rollback em caso de qualquer outro erro de banco de dados
        logging.error(f"Erro durante a inserção em lote de usuários: {e}")
        if conn:
            conn.rollback()
        return jsonify({"error": f"Erro de banco de dados: {str(e)}"}), 500
    
    finally:
        # 7. Fechamento da Conexão
        if conn:
            cursor.close()
            conn.close()
