from flask import request, jsonify, current_app
from db import create_connection
from routes.login.token_required import token_required
from datetime import datetime
from .bluprint import ciclos
import logging

# Configuração básica de logging
logging.basicConfig(level=logging.INFO)

@ciclos.route('/criar_ciclo', methods=['POST'])
@token_required
def criar_ciclo(current_user):

    # --- VERIFICAÇÃO DE PERMISSÃO ---
    if current_user.get("nivel_de_acesso") not in ["supervisor"]:
        return jsonify({"error": "Acesso negado: É necessário ser supervisor para criar um novo ciclo."}), 403

    conn = None
    cursor = None
    try:
        # --- CONEXÃO COM O BANCO ---
        # É uma boa prática usar um bloco `with` para garantir que a conexão seja fechada,
        # mas vamos manter a estrutura original com try/except/finally corrigida.
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500
        
        # Usar um cursor que retorna dicionários facilita o acesso aos dados por nome de coluna.
        # Se você estiver usando psycopg2, seria algo como: cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor = conn.cursor()

        # --- BUSCAR O ÚLTIMO CICLO ATIVO DE FORMA EFICIENTE ---
        # CORREÇÃO 1: Em vez de buscar todos os ciclos, buscamos apenas o último.
        # Adicionado ORDER BY para garantir que o último ciclo seja realmente o mais recente.
        get_last_cicle_query = """
            SELECT ciclo_id, ciclo, EXTRACT(YEAR FROM ano_de_criacao)::INTEGER AS ano 
            FROM ciclos 
            ORDER BY ano_de_criacao DESC, ciclo DESC 
            LIMIT 1
        """
        cursor.execute(get_last_cicle_query)
        ultimo_ciclo_db = cursor.fetchone()

        # --- LÓGICA PARA CRIAR NOVO CICLO ---
        current_datetime = datetime.now()
        current_year = current_datetime.year
        supervisor_id = current_user['supervisor_id']
        novo_ciclo_numero = 1
        id_ultimo_ciclo = None

        if ultimo_ciclo_db:
            id_ultimo_ciclo = ultimo_ciclo_db['ciclo_id']
            ano_ultimo_ciclo = ultimo_ciclo_db['ano']
            numero_ultimo_ciclo = ultimo_ciclo_db['ciclo']

            # Se o ano for o mesmo, incrementa o ciclo. Se for um novo ano, o ciclo começa em 1.
            if ano_ultimo_ciclo == current_year:
                novo_ciclo_numero = numero_ultimo_ciclo + 1
            
            # Desativa o ciclo anterior
            set_last_ciclo_inactive_query = """
                UPDATE ciclos SET ativo = False, encerramento = %s WHERE ciclo_id = %s
            """
            cursor.execute(set_last_ciclo_inactive_query, (current_datetime, id_ultimo_ciclo))

        # --- INSERIR NOVO CICLO ---
        insert_new_ciclo_query = """
            INSERT INTO ciclos (supervisor_id, ano_de_criacao, encerramento, ativo, ciclo) 
            VALUES (%s, %s, %s, %s, %s) RETURNING ciclo_id;
        """
        cursor.execute(insert_new_ciclo_query, (supervisor_id, current_datetime, None, True, novo_ciclo_numero))
        novo_ciclo_id = cursor.fetchone()['ciclo_id']

        # --- COPIAR REGISTROS DO CICLO ANTERIOR (se houver) ---
        if id_ultimo_ciclo:
                        
            # Busca todos os registros de campo do ciclo anterior
            get_registros_query = "SELECT * FROM registro_de_campo WHERE ciclo_id = %s;"
            cursor.execute(get_registros_query, (id_ultimo_ciclo, ))
            registros_do_ultimo_ciclo = cursor.fetchall()

            # CORREÇÃO 2: A query de INSERT estava com um placeholder a menos. Adicionado o %s faltante para a coluna 't'.
            insert_new_registro_query = """
                INSERT INTO registro_de_campo (
                    agente_id, area_de_visita_id, caso_comfirmado, ciclo_id, deposito_id, df, 
                    formulario_tipo, imovel_categoria_da_localidade, imovel_complemento, 
                    imovel_lado, imovel_numero, imovel_status, imovel_tipo, li, numero_da_amostra, 
                    observacao, pe, pve, quantiade_tubitos, t
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                );
            """

            for reg_de_campo in registros_do_ultimo_ciclo:
                
                # Cria um novo depósito para todos os registros do novo ciclo
                create_deposito_query = """
                    INSERT INTO depositos(a1, a2, b, c, d1, d2, e) 
                    VALUES (0, 0, 0, 0, 0, 0, 0) RETURNING deposito_id;
                """
                cursor.execute(create_deposito_query)
                deposito_id_novo_ciclo = cursor.fetchone()['deposito_id']

                # Monta os dados para o novo registro, zerando os campos necessários
                novo_registro_data = (
                    reg_de_campo['agente_id'],
                    reg_de_campo['area_de_visita_id'],
                    False,                          # caso_confirmado
                    novo_ciclo_id,
                    deposito_id_novo_ciclo,         # Um novo depósito para todos os novos registros
                    False,                          # df
                    None,                           # formulario_tipo
                    reg_de_campo['imovel_categoria_da_localidade'],
                    reg_de_campo['imovel_complemento'],
                    reg_de_campo['imovel_lado'],
                    reg_de_campo['imovel_numero'],
                    'nao_inspecionado',             # imovel_status
                    reg_de_campo['imovel_tipo'],
                    False,                          # li
                    None,                           # numero_da_amostra
                    reg_de_campo.get('observacao'), # Usar .get() para evitar erro se a chave não existir
                    False,                          # pe
                    False,                          # pve
                    None,                           # quantiade_tubitos
                    False                           # t
                )
                cursor.execute(insert_new_registro_query, novo_registro_data)
        
        # CORREÇÃO 3: O `commit` deve ocorrer aqui, ao final do bloco `try`, se tudo deu certo.
        conn.commit()

        # CORREÇÃO 4: Removido o código inalcançável. O retorno agora é mais informativo.
        return jsonify({
            "message": "Novo ciclo criado com sucesso!",
            "novo_ciclo": {
                "id": novo_ciclo_id,
                "numero": novo_ciclo_numero,
                "ano": current_year
            }
        }), 201
    
    except Exception as e:
        # Se qualquer erro ocorrer, o rollback desfaz todas as operações no banco.
        if conn:
            conn.rollback()
        logging.error(f"Erro ao criar ciclo: {e}")
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação."}), 500

    finally:
        # O `finally` garante que o cursor e a conexão serão sempre fechados.
        if cursor:
            cursor.close()
        if conn:
            conn.close()
