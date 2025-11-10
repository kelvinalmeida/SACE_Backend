import pytest

# Usaremos esta variável global para armazenar os IDs
# dos novos registros criados, para que os testes de PUT e DELETE possam usá-los.
ids_criados_no_teste = []

def test_seguranca_agente_permissoes_doentes(agente_client):
    """
    TESTE DE SEGURANÇA:
    Verifica se um AGENTE PODE LER, mas NÃO PODE modificar (POST, PUT, DELETE)
    os registros de doentes confirmados.
    """
    
    # --- 1. AGENTE PODE LER (GET) ---
    
    # GET /doentes_confirmados (Listar todos)
    resp_get_all = agente_client.get('/doentes_confirmados')
    assert resp_get_all.status_code == 200
    assert isinstance(resp_get_all.json, list)
    # Verifica os 15 registros do backup.sql
    assert len(resp_get_all.json) >= 15 

    # GET /doentes_confirmados/1 (Buscar um)
    resp_get_one = agente_client.get('/doentes_confirmados/1')
    assert resp_get_one.status_code == 200
    assert resp_get_one.json['doente_confirmado_id'] == 1
    assert resp_get_one.json['nome'] == 'Ana Lúcia Barbosa'

    # --- 2. AGENTE NÃO PODE MODIFICAR ---

    # POST /doentes_confirmados (Criar)
    resp_post = agente_client.post('/doentes_confirmados', json=[{
        "tipo_da_doenca": "Dengue", "rua": "Rua Teste Agente"
    }])
    assert resp_post.status_code == 403
    assert "Acesso negado: Apenas supervisores" in resp_post.json['error']

    # PUT /doentes_confirmados/1 (Atualizar)
    resp_put = agente_client.put('/doentes_confirmados/1', json={
        "tipo_da_doenca": "Dengue", "rua": "Rua Teste Agente PUT"
    })
    assert resp_put.status_code == 403
    assert "Acesso negado: Apenas supervisores" in resp_put.json['error']

    # DELETE /doente_confirmado/1 (Deletar)
    # ATENÇÃO: A sua rota de delete está no singular: /doente_confirmado/
    resp_delete = agente_client.delete('/doente_confirmado/1')
    assert resp_delete.status_code == 403
    assert "Acesso negado: Apenas supervisores" in resp_delete.json['error']


def test_supervisor_workflow_crud_doentes_confirmados(auth_client):
    """
    TESTE DE WORKFLOW (SUPERVISOR):
    Testa o fluxo completo de CRUD (Criar em lote, Atualizar, Deletar)
    para um supervisor.
    """
    global ids_criados_no_teste
    
    # --- 1. CRIAR EM LOTE (POST /doentes_confirmados) ---
    
    # O ciclo 4 (2025/2) está ativo no backup.sql.
    # Os novos registros devem ser associados a ele.
    payload_post = [
        {
            "nome": "Paciente Pytest 1",
            "tipo_da_doenca": "Dengue",
            "rua": "Rua do Teste 1",
            "numero": "100",
            "bairro": "Bairro Pytest"
        },
        {
            "nome": "Paciente Pytest 2",
            "tipo_da_doenca": "Zica",
            "rua": "Rua do Teste 2",
            "bairro": "Bairro Pytest"
        }
    ]
    
    resp_post = auth_client.post('/doentes_confirmados', json=payload_post)
    
    assert resp_post.status_code == 201, f"Erro: {resp_post.json}"
    data_post = resp_post.json
    assert "registros de doenças confirmadas criados com sucesso" in data_post['message']
    assert len(data_post['ids_criados']) == 2
    assert data_post['ciclo_id_associado'] == 8 # Verifica se associou ao ciclo ativo
    
    # Armazena os IDs para os próximos testes
    ids_criados_no_teste = data_post['ids_criados']
    assert ids_criados_no_teste[0] is not None
    assert ids_criados_no_teste[1] is not None

    # --- 2. ATUALIZAR (PUT /doentes_confirmados/<id>) ---
    
    id_para_atualizar = ids_criados_no_teste[0]
    payload_put = {
        "nome": "Paciente Pytest 1 (ATUALIZADO)",
        "tipo_da_doenca": "Chikungunya", # Mudou de Dengue
        "rua": "Rua do Teste 1 (ATUALIZADA)", # Mudou a rua
        "numero": "100-A", # Mudou o número
        "bairro": "Bairro Pytest"
    }
    
    resp_put = auth_client.put(
        f'/doentes_confirmados/{id_para_atualizar}', 
        json=payload_put
    )
    
    assert resp_put.status_code == 200
    assert resp_put.json['message'] == "Registro atualizado com sucesso."
    
    # --- 3. VERIFICAR ATUALIZAÇÃO (GET) ---
    resp_get = auth_client.get(f'/doentes_confirmados/{id_para_atualizar}')
    assert resp_get.status_code == 200
    data_get = resp_get.json
    assert data_get['nome'] == "Paciente Pytest 1 (ATUALIZADO)"
    assert data_get['tipo_da_doenca'] == "Chikungunya"
    assert data_get['rua'] == "Rua do Teste 1 (ATUALIZADA)"
    assert data_get['numero'] == "100-A"

    # --- 4. DELETAR (DELETE /doente_confirmado/<id>) ---
    # Deleta os dois registros que criamos
    
    # ATENÇÃO: A sua rota de delete está no singular: /doente_confirmado/
    
    id_1 = ids_criados_no_teste[0]
    id_2 = ids_criados_no_teste[1]
    
    resp_del_1 = auth_client.delete(f'/doente_confirmado/{id_1}')
    assert resp_del_1.status_code == 200
    assert resp_del_1.json['id_deletado'] == id_1
    
    resp_del_2 = auth_client.delete(f'/doente_confirmado/{id_2}')
    assert resp_del_2.status_code == 200
    assert resp_del_2.json['id_deletado'] == id_2

    # --- 5. VERIFICAR DELEÇÃO (GET) ---
    resp_get_404 = auth_client.get(f'/doentes_confirmados/{id_1}')
    assert resp_get_404.status_code == 404
    assert resp_get_404.json['error'] == "Registro não encontrado."

    resp_get_404_2 = auth_client.get(f'/doentes_confirmados/{id_2}')
    assert resp_get_404_2.status_code == 404

def test_erros_de_input_doentes_confirmados(auth_client):
    """
    Testa se a API rejeita inputs inválidos (400 Bad Request).
    """
    
    # 1. Tentar criar com lista vazia
    resp_post_empty = auth_client.post('/doentes_confirmados', json=[])
    assert resp_post_empty.status_code == 400
    assert "lista não vazia" in resp_post_empty.json['error']

    # 2. Tentar criar sem campo obrigatório 'rua'
    resp_post_no_rua = auth_client.post('/doentes_confirmados', json=[
        {"tipo_da_doenca": "Dengue", "nome": "Paciente Sem Rua"}
    ])
    assert resp_post_no_rua.status_code == 400
    assert "Campos 'tipo_da_doenca' e 'rua' são obrigatórios" in resp_post_no_rua.json['error']
    
    # 3. Tentar criar sem campo obrigatório 'tipo_da_doenca'
    resp_post_no_tipo = auth_client.post('/doentes_confirmados', json=[
        {"rua": "Rua Sem Doença", "nome": "Paciente Sem Doença"}
    ])
    assert resp_post_no_tipo.status_code == 400
    assert "Campos 'tipo_da_doenca' e 'rua' são obrigatórios" in resp_post_no_tipo.json['error']

    # 4. Tentar atualizar (PUT) sem campo obrigatório 'rua'
    resp_put_no_rua = auth_client.put('/doentes_confirmados/1', json={
        "tipo_da_doenca": "Dengue"
    })
    assert resp_put_no_rua.status_code == 400
    assert "Campos 'tipo_da_doenca' e 'rua' são obrigatórios" in resp_put_no_rua.json['error']