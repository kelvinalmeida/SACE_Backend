import pytest

# --- Variáveis Globais para os Testes ---
# Usamos 'None' e as preenchemos no teste de criação
# para que os testes de update e delete possam usar os IDs recém-criados.
new_agente_id_pytest = None
new_supervisor_id_pytest = None

def test_seguranca_agente_permissoes(agente_client):
    """
    Testa as permissões de um AGENTE.
    - PODE ler rotas GET.
    - NÃO PODE criar (POST) ou deletar (DELETE) outros usuários.
    """
    
    # 1. Agente PODE ler a lista de usuários
    resp_get_all = agente_client.get('/usuarios')
    assert resp_get_all.status_code == 200
    assert 'agentes' in resp_get_all.json
    assert 'supervisores' in resp_get_all.json

    # 2. Agente PODE ler seu próprio perfil (GET /usuarios/agente/<id>)
    # O 'agente_client' (João da Silva) tem agente_id=1
    resp_get_self = agente_client.get('/usuarios/agente/1')
    assert resp_get_self.status_code == 200
    assert resp_get_self.json['agente_id'] == 1

    # 3. Agente NÃO PODE criar usuários (POST /usuarios)
    resp_post = agente_client.post('/usuarios', json=[{
        "nome_completo": "Tentativa Agente",
        "cpf": "00000000000",
        "email": "falha@teste.com",
        "nivel_de_acesso": "agente" 
        # ... (não precisa de todos os campos, deve falhar na permissão)
    }])
    assert resp_post.status_code == 403
    assert "É necessário ser supervisor" in resp_post.json['error']

    # 4. Agente NÃO PODE deletar outro agente (DELETE /usuarios/agente/<id>)
    # Tenta deletar o agente_id=2 (Pedro Cavalcante)
    resp_delete_agente = agente_client.delete('/usuarios/agente/2')
    assert resp_delete_agente.status_code == 403
    assert "Acesso negado" in resp_delete_agente.json['error']

    # 5. Agente NÃO PODE deletar um supervisor (DELETE /usuarios/supervisor/<id>)
    # Tenta deletar o supervisor_id=1 (Pedro Cavalcante)
    resp_delete_super = agente_client.delete('/usuarios/supervisor/1')
    assert resp_delete_super.status_code == 403
    assert "Acesso negado" in resp_delete_super.json['error']

def test_supervisor_pode_ler_rotas_get_usuario(auth_client):
    """
    Testa se o SUPERVISOR (auth_client) pode acessar
    todas as rotas GET de usuário com sucesso.
    """
    
    # 1. GET /usuarios (Listar todos)
    resp_get_all = auth_client.get('/usuarios')
    assert resp_get_all.status_code == 200
    data = resp_get_all.json
    assert 'agentes' in data
    assert 'supervisores' in data
    # Verifica se os dados do backup.sql foram carregados
    assert len(data['agentes']) >= 17 
    assert len(data['supervisores']) >= 4 

    # 2. GET /usuarios/agente/1 (Agente Específico)
    resp_get_agente = auth_client.get('/usuarios/agente/1')
    assert resp_get_agente.status_code == 200
    assert resp_get_agente.json['nome_completo'] == 'João da Silva'
    # Verifica se o JOIN de 'setor_de_atuacao' funcionou
    assert len(resp_get_agente.json['setor_de_atuacao']) == 3 # Áreas 1, 9, 5

    # 3. GET /usuarios/supervisor/1 (Supervisor Específico)
    resp_get_super = auth_client.get('/usuarios/supervisor/1')
    assert resp_get_super.status_code == 200
    assert resp_get_super.json['nome_completo'] == 'Pedro Cavalcante'

    # 4. GET /area_de_visita_denuncias/1 (Dados de trabalho do Agente 1)
    resp_get_data = auth_client.get('/area_de_visita_denuncias/1')
    assert resp_get_data.status_code == 200
    assert 'areas_de_visitas' in resp_get_data.json
    assert 'denuncias' in resp_get_data.json
    # Verifica dados do backup.sql
    assert len(resp_get_data.json['areas_de_visitas']) == 3 # Agente 1 tem áreas 1, 9, 5
    assert len(resp_get_data.json['denuncias']) == 1 # Agente 1 é resp. pela denúncia 5

def test_supervisor_workflow_crud_usuarios_completo(auth_client):
    """
    Testa o fluxo completo de CRUD (Create, Update, Delete)
    para um AGENTE e um SUPERVISOR novos.
    """
    global new_agente_id_pytest, new_supervisor_id_pytest
    
    # --- 1. CRIAR (POST /usuarios) ---
    # (CPFs e Emails devem ser únicos para o teste passar)
    agente_payload = {
        "nome_completo": "Agente Pytest Criado",
        "cpf": "11111111111",
        "rg": "111111",
        "data_nascimento": "2000-01-01",
        "email": "agente@pytest.com",
        "telefone_ddd": 82, "telefone_numero": "999999999",
        "estado": "AL", "municipio": "Maceió", "bairro": "Teste",
        "logradouro": "Rua Teste", "numero": 123,
        "registro_do_servidor": "PYTEST001",
        "cargo": "Agente Teste", "situacao_atual": True,
        "data_de_admissao": "2025-01-01",
        "senha": "123",
        "nivel_de_acesso": "agente",
        "setor_de_atuacao": [1, 2] # Áreas 1 e 2 do backup
    }
    
    supervisor_payload = {
        "nome_completo": "Supervisor Pytest Criado",
        "cpf": "22222222222",
        "rg": "222222",
        "data_nascimento": "1990-01-01",
        "email": "supervisor@pytest.com",
        "telefone_ddd": 82, "telefone_numero": "988888888",
        "estado": "AL", "municipio": "Maceió", "bairro": "Teste",
        "logradouro": "Rua Teste", "numero": 456,
        "registro_do_servidor": "PYTEST002",
        "cargo": "Supervisor Teste", "situacao_atual": True,
        "data_de_admissao": "2024-01-01",
        "senha": "123",
        "nivel_de_acesso": "supervisor",
        "setor_de_atuacao": [] # Supervisor não tem setor
    }
    
    resp_post = auth_client.post('/usuarios', json=[agente_payload, supervisor_payload])
    
    assert resp_post.status_code == 201
    assert "Usuários criados com sucesso" in resp_post.json['message']
    
    # Precisamos encontrar os IDs de AGENTE e SUPERVISOR (não apenas o usuario_id)
    # Então, listamos todos os usuários e procuramos pelos que criamos
    resp_get_all = auth_client.get('/usuarios')
    
    created_agente = next((u for u in resp_get_all.json['agentes'] if u['cpf'] == "11111111111"), None)
    created_supervisor = next((u for u in resp_get_all.json['supervisores'] if u['cpf'] == "22222222222"), None)
    
    assert created_agente is not None, "O agente de teste não foi encontrado após a criação."
    assert created_supervisor is not None, "O supervisor de teste não foi encontrado após a criação."
    
    # Armazena os IDs para os próximos testes
    new_agente_id_pytest = created_agente['agente_id']
    new_supervisor_id_pytest = created_supervisor['supervisor_id']

    # --- 2. ATUALIZAR (PUT /usuarios/agente/<id>) ---
    update_agente_payload = {
        "nome_completo": "Agente Pytest ATUALIZADO",
        "cargo": "Agente Senior",
        "setor_de_atuacao": [3, 4] # Muda as áreas de 1,2 para 3,4
    }
    
    resp_put_agente = auth_client.put(
        f'/usuarios/agente/{new_agente_id_pytest}',
        json=update_agente_payload
    )
    assert resp_put_agente.status_code == 200
    
    # Verifica a atualização
    resp_get_agente = auth_client.get(f'/usuarios/agente/{new_agente_id_pytest}')
    assert resp_get_agente.json['nome_completo'] == "Agente Pytest ATUALIZADO"
    assert resp_get_agente.json['cargo'] == "Agente Senior"
    assert len(resp_get_agente.json['setor_de_atuacao']) == 2
    assert resp_get_agente.json['setor_de_atuacao'][0]['area_de_visita_id'] == 3 # Confirma que a área mudou

    # --- 3. ATUALIZAR (PUT /usuarios/supervisor/<id>) ---
    update_super_payload = {
        "nome_completo": "Supervisor Pytest ATUALIZADO",
        "cargo": "Supervisor Senior"
    }
    resp_put_super = auth_client.put(
        f'/usuarios/supervisor/{new_supervisor_id_pytest}',
        json=update_super_payload
    )
    assert resp_put_super.status_code == 200
    
    # Verifica a atualização
    resp_get_super = auth_client.get(f'/usuarios/supervisor/{new_supervisor_id_pytest}')
    assert resp_get_super.json['nome_completo'] == "Supervisor Pytest ATUALIZADO"

    # --- 4. DELETAR (DELETE /usuarios/agente/<id>) ---
    resp_del_agente = auth_client.delete(f'/usuarios/agente/{new_agente_id_pytest}')
    assert resp_del_agente.status_code == 200
    assert resp_del_agente.json['agente_id'] == new_agente_id_pytest
    
    # Verifica a deleção
    resp_get_agente_404 = auth_client.get(f'/usuarios/agente/{new_agente_id_pytest}')
    assert resp_get_agente_404.status_code == 404

    # --- 5. DELETAR (DELETE /usuarios/supervisor/<id>) ---
    resp_del_super = auth_client.delete(f'/usuarios/supervisor/{new_supervisor_id_pytest}')
    assert resp_del_super.status_code == 200
    assert resp_del_super.json['supervisor_id'] == new_supervisor_id_pytest

    # Verifica a deleção
    resp_get_super_404 = auth_client.get(f'/usuarios/supervisor/{new_supervisor_id_pytest}')
    assert resp_get_super_404.status_code == 404