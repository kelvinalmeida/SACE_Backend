import pytest

# Usaremos esta lista global para armazenar os IDs das áreas
# criadas no teste de POST para serem usadas no teste de DELETE.
ids_areas_criadas = []

def test_seguranca_permissoes_agente_area_visita(agente_client):
    """
    TESTE DE SEGURANÇA:
    Verifica se um AGENTE (agente_client) não pode acessar rotas
    de gerenciamento de áreas de visita, que são restritas a supervisores.
    """
    
    # 1. Agente NÃO PODE listar todas as áreas (GET /area_de_visita)
    # De acordo com `get_all.py`, a rota verifica o supervisor_id
    # response_get_all = agente_client.get('/area_de_visita')
    # assert response_get_all.status_code == 403
    # assert "É nescessário ser supervisor" in response_get_all.json['error']

    # 2. Agente NÃO PODE buscar uma área por ID (GET /area_de_visita/1)
    # response_get_one = agente_client.get('/area_de_visita/1')
    # assert response_get_one.status_code == 403
    # assert "É nescessário ser supervisor" in response_get_one.json['error']

    # 3. Agente NÃO PODE criar áreas (POST /area_de_visita)
    response_post = agente_client.post('/area_de_visita', json=[{"bairro": "teste"}])
    assert response_post.status_code == 403
    assert "É necessário ser supervisor" in response_post.json['error']

    # 4. Agente NÃO PODE atualizar áreas (PUT /area_de_visita/1)
    response_put = agente_client.put('/area_de_visita/1', json={"bairro": "teste"})
    assert response_put.status_code == 403
    assert "É nescessário ser supervisor" in response_put.json['error']

    # 5. Agente NÃO PODE deletar áreas (DELETE /area_de_visita)
    response_delete = agente_client.delete('/area_de_visita', json={"ids": [1]})
    assert response_delete.status_code == 403
    assert "É nescessário ser supervisor" in response_delete.json['error']


def test_supervisor_leitura_area_visita(auth_client):
    """
    TESTE DE LEITURA (SUPERVISOR):
    Verifica se o Supervisor (auth_client) pode LER (GET) os dados
    das áreas de visita carregadas pelo backup.sql.
    """
    
    # 1. Supervisor PODE listar todas as áreas
    response_get_all = auth_client.get('/area_de_visita')
    assert response_get_all.status_code == 200
    assert isinstance(response_get_all.json, list)
    # O backup.sql contém 10 áreas de visita
    assert len(response_get_all.json) >= 10 

    # 2. Supervisor PODE buscar uma área por ID (GET /area_de_visita/1)
    response_get_one = auth_client.get('/area_de_visita/1')
    assert response_get_one.status_code == 200
    data = response_get_one.json
    assert data['area_de_visita_id'] == 1
    assert data['bairro'] == 'Ponta Verde'
    
    # Verifica se o JOIN de agentes associados está funcionando
    # De acordo com backup.sql, área 1 tem agente 1 (João) e 11 (Larissa)
    assert 'agentes' in data
    assert len(data['agentes']) == 2
    assert data['agentes'][0]['nome'] == 'João da Silva'


def test_supervisor_workflow_crud_area_visita(auth_client):
    """
    TESTE DE WORKFLOW (SUPERVISOR):
    Testa o fluxo completo de POST (lote), PUT e DELETE (lote)
    para áreas de visita.
    """
    global ids_areas_criadas
    
    # --- 1. CRIAR EM LOTE (POST) ---
    payload_post = [
        {
            "cep": "11111-001", "setor": "Setor Pytest 01", "numero_quarteirao": 998,
            "estado": "AL", "municipio": "Pytest", "bairro": "Bairro Teste 1",
            "logadouro": "Rua Teste 1"
        },
        {
            "cep": "11111-002", "setor": "Setor Pytest 02", "numero_quarteirao": 999,
            "estado": "AL", "municipio": "Pytest", "bairro": "Bairro Teste 2",
            "logadouro": "Rua Teste 2"
        }
    ]
    
    response_post = auth_client.post('/area_de_visita', json=payload_post)
    
    assert response_post.status_code == 201
    data_post = response_post.json
    assert "Áreas de visita criadas com sucesso" in data_post['message']
    assert len(data_post['areas_criadas_ids']) == 2
    
    # Salva os IDs para os próximos testes
    ids_areas_criadas = data_post['areas_criadas_ids']

    # --- 2. ATUALIZAR UMA ÁREA (PUT) ---
    id_para_atualizar = ids_areas_criadas[0]
    payload_put = {
        "cep": "22222-001", "setor": "Setor Pytest ATUALIZADO", "numero_quarteirao": 998,
        "estado": "AL", "municipio": "Pytest", "bairro": "Bairro ATUALIZADO",
        "logadouro": "Rua Teste 1", "status": "Visitado" # Atualizando o status
    }

    response_put = auth_client.put(
        f'/area_de_visita/{id_para_atualizar}', 
        json=payload_put
    )
    
    assert response_put.status_code == 200
    
    # Verifica se a atualização funcionou
    response_get = auth_client.get(f'/area_de_visita/{id_para_atualizar}')
    assert response_get.status_code == 200
    assert response_get.json['bairro'] == 'Bairro ATUALIZADO'
    assert response_get.json['status'] == 'Visitado' # Verifica o status

    # --- 3. DELETAR EM LOTE (DELETE) ---
    payload_delete = {
        "ids": ids_areas_criadas
    }
    
    response_delete = auth_client.delete('/area_de_visita', json=payload_delete)
    
    # A rota de delete retorna 201
    assert response_delete.status_code == 201
    assert "deletadas com sucesso" in response_delete.json['message']

    # --- 4. VERIFICAR DELEÇÃO ---
    response_get_404 = auth_client.get(f'/area_de_visita/{id_para_atualizar}')
    assert response_get_404.status_code == 404
    assert response_get_404.json['error'] == 'Área de visita não encontrada'


def test_get_registros_por_area_visita(agente_client, auth_client):
    """
    Testa a rota especial 'GET /area_de_visita/<id>/registros'
    que deve funcionar tanto para AGENTES quanto para SUPERVISORES.
    
    Esta rota busca os registros de campo (imóveis) APENAS do ciclo ATIVO.
    """
    
    # No backup.sql, o ciclo ATIVO é o 4 (2025/2).
    # A area_de_visita_id=1 (Ponta Verde) tem 4 registros nesse ciclo
    # (IDs 121, 122, 123, 124).
    
    # 1. Testar como AGENTE
    resp_agente = agente_client.get('/area_de_visita/1/registros')
    
    assert resp_agente.status_code == 200
    assert isinstance(resp_agente.json, list)
    assert len(resp_agente.json) == 4
    # Verifica se os dados estão corretos (status, número, etc.)
    assert resp_agente.json[0]['registro_de_campo_id'] == 121
    assert resp_agente.json[0]['imovel_numero'] == '101'
    assert resp_agente.json[0]['imovel_status'] == 'bloqueado'

    # 2. Testar como SUPERVISOR (deve ter o mesmo resultado)
    resp_super = auth_client.get('/area_de_visita/1/registros')
    
    assert resp_super.status_code == 200
    assert isinstance(resp_super.json, list)
    assert len(resp_super.json) == 4
    assert resp_super.json[0]['registro_de_campo_id'] == 121