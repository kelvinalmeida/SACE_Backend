import pytest

# Usaremos esta variável global para passar o ID do nudge
# recém-criado para os testes de update e delete.
nudge_id_criado = None


def test_acesso_publico_e_agente_pode_ler_nudges(client, agente_client):
    """
    TESTE DE LEITURA (PÚBLICO / AGENTE):
    Verifica se qualquer usuário (logado ou não) pode LER (GET) os nudges,
    já que estas são rotas públicas.
    """
    
    # --- 1. Testar como cliente PÚBLICO (não logado) ---
    
    # GET /nudges (Listar todos)
    resp_all_public = client.get('/nudges')
    assert resp_all_public.status_code == 200
    assert isinstance(resp_all_public.json, list)
    # Verifica os 6 nudges do seu backup.sql
    assert len(resp_all_public.json) >= 6
    # O backup ordena por ID DESC, então o primeiro item é o ID 6
    assert resp_all_public.json[0]['titulo'] == "Caixa d'água vedada" 

    # GET /nudges/1 (Buscar um)
    resp_one_public = client.get('/nudges/1')
    assert resp_one_public.status_code == 200
    assert resp_one_public.json['nudges_id'] == 1
    assert resp_one_public.json['titulo'] == "Não se esqueça da vistoria!"

    # GET /nudges/9999 (Buscar 404)
    resp_404_public = client.get('/nudges/99999')
    assert resp_404_public.status_code == 404
    assert resp_404_public.json['error'] == "Nudge não encontrado."

    # --- 2. Testar como AGENTE (logado) ---
    # (Deve ter o mesmo resultado, pois as rotas são públicas)
    
    resp_all_agente = agente_client.get('/nudges')
    assert resp_all_agente.status_code == 200
    assert len(resp_all_agente.json) >= 6

    resp_one_agente = agente_client.get('/nudges/1')
    assert resp_one_agente.status_code == 200
    assert resp_one_agente.json['nudges_id'] == 1


def test_seguranca_agente_nao_pode_modificar_nudges(agente_client):
    """
    TESTE DE SEGURANÇA (AGENTE):
    Verifica se um usuário com nível 'agente' NÃO PODE criar (POST),
    atualizar (PUT) ou deletar (DELETE) nudges.
    """
    
    # 1. Agente NÃO PODE Criar (POST)
    payload_post = {
        "titulo": "Nudge Teste Agente",
        "descricao": "Agente não pode criar.",
        "url": "https://teste.com"
    }
    resp_post = agente_client.post('/nudges', json=payload_post)
    assert resp_post.status_code == 403
    assert "Acesso negado: Apenas supervisores" in resp_post.json['error']

    # 2. Agente NÃO PODE Atualizar (PUT)
    resp_put = agente_client.put('/nudges/1', json=payload_post)
    assert resp_put.status_code == 403
    assert "Acesso negado: Apenas supervisores" in resp_put.json['error']

    # 3. Agente NÃO PODE Deletar (DELETE)
    resp_del = agente_client.delete('/nudges/1')
    assert resp_del.status_code == 403
    assert "Acesso negado: Apenas supervisores" in resp_del.json['error']


def test_supervisor_workflow_crud_nudges(auth_client):
    """
    TESTE DE WORKFLOW (SUPERVISOR):
    Testa o fluxo completo de CRUD (Criar, Atualizar, Deletar)
    para um supervisor.
    """
    global nudge_id_criado
    
    # --- 1. CRIAR (POST /nudges) ---
    payload_post = {
        "titulo": "Nudge Criado pelo Pytest",
        "descricao": "Esta é a descrição do teste.",
        "url": "https://pytest.org/nudge"
    }
    
    resp_post = auth_client.post('/nudges', json=payload_post)
    
    assert resp_post.status_code == 201
    data_post = resp_post.json
    assert data_post['titulo'] == "Nudge Criado pelo Pytest"
    assert data_post['descricao'] == "Esta é a descrição do teste."
    assert data_post['url'] == "https://pytest.org/nudge"
    assert "nudges_id" in data_post
    
    # Salva o ID para os testes seguintes
    nudge_id_criado = data_post['nudges_id']
    assert nudge_id_criado is not None

    # --- 2. ATUALIZAR (PUT /nudges/<id>) ---
    payload_put = {
        "titulo": "Nudge ATUALIZADO (Pytest)",
        "descricao": "Descrição foi atualizada.",
        "url": "https://pytest.org/nudge-updated"
    }
    
    resp_put = auth_client.put(f'/nudges/{nudge_id_criado}', json=payload_put)
    
    assert resp_put.status_code == 200
    data_put = resp_put.json
    assert data_put['nudges_id'] == nudge_id_criado
    assert data_put['titulo'] == "Nudge ATUALIZADO (Pytest)"
    assert data_put['url'] == "https://pytest.org/nudge-updated"

    # --- 3. VERIFICAR ATUALIZAÇÃO (GET) ---
    # (Verifica se a atualização foi persistida)
    resp_get = auth_client.get(f'/nudges/{nudge_id_criado}')
    assert resp_get.status_code == 200
    assert resp_get.json['titulo'] == "Nudge ATUALIZADO (Pytest)"


def test_supervisor_delete_nudge_e_validacao(auth_client):
    """
    TESTE DE DELEÇÃO (SUPERVISOR):
    Deleta o nudge criado no teste anterior e testa a validação de 404.
    """
    global nudge_id_criado
    assert nudge_id_criado is not None, "O teste de criação de nudge falhou ou não rodou."

    # --- 1. DELETAR (DELETE) ---
    resp_del = auth_client.delete(f'/nudges/{nudge_id_criado}')
    
    assert resp_del.status_code == 200
    assert resp_del.json['id_deletado'] == nudge_id_criado
    assert resp_del.json['message'] == "Nudge deletado com sucesso."

    # --- 2. VERIFICAR DELEÇÃO (GET) ---
    resp_get_404 = auth_client.get(f'/nudges/{nudge_id_criado}')
    assert resp_get_404.status_code == 404
    assert resp_get_404.json['error'] == "Nudge não encontrado."
    
    # --- 3. VERIFICAR DELEÇÃO DE NOVO (DELETE) ---
    # Tentar deletar um ID que não existe mais
    resp_del_404 = auth_client.delete(f'/nudges/{nudge_id_criado}')
    assert resp_del_404.status_code == 404
    assert resp_del_404.json['error'] == "Nudge não encontrado."


def test_supervisor_input_validation(auth_client):
    """
    TESTE DE VALIDAÇÃO (SUPERVISOR):
    Verifica se a API retorna 400 Bad Request para dados inválidos.
    """
    
    # 1. Tentar CRIAR (POST) sem campo obrigatório 'titulo'
    payload_post = {
        "descricao": "Falta o título",
        "url": "https://pytest.org"
    }
    resp_post = auth_client.post('/nudges', json=payload_post)
    assert resp_post.status_code == 400
    assert "Campos 'titulo', 'descricao' e 'url' são obrigatórios" in resp_post.json['error']

    # 2. Tentar ATUALIZAR (PUT) sem campo obrigatório 'url'
    payload_put = {
        "titulo": "Nudge ATUALIZADO (Pytest)",
        "descricao": "Falta a URL."
    }
    resp_put = auth_client.put('/nudges/1', json=payload_put)
    assert resp_put.status_code == 400
    assert "Campos 'titulo', 'descricao' e 'url' são obrigatórios" in resp_put.json['error']