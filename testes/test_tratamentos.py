import pytest

@pytest.fixture(scope='function')
def agente_client(client):
    """
    Cria um fixture de cliente autenticado como um AGENTE.
    Usaremos o agente 'Maria Oliveira Santos' (agente_id=3) do backup.sql,
    pois já corrigimos os testes anteriores para ela.
    
    Qualquer usuário autenticado (agente ou supervisor) funcionaria aqui,
    pois as rotas de tratamento exigem apenas @token_required.
    """
    # Login como o Agente (cpf: '23456789012', senha: 'outrasenha456')
    response = client.post('/login', json={
        "username": "23456789012",
        "password": "outrasenha456"
    })
    
    if response.status_code != 200:
        pytest.fail("Falha ao autenticar o cliente agente.")

    token = response.json['token']
    
    # Adiciona o token de agente ao cabeçalho
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
    
    return client

# --- Testes de Larvicida ---

def test_larvicida_update_e_delete(agente_client):
    """
    Testa o fluxo completo de UPDATE (PUT) e DELETE para um larvicida existente.
    """
    # De acordo com seu backup.sql, o larvicida com ID 1 existe.
    ULTIMO_LARVICIDA_ID_PARA_TESTE = 1
    
    # --- 1. TESTE DE UPDATE (PUT) ---
    # Dados para a atualização (enviados como form-data)
    update_payload = {
        'tipo': 'Tipo Larvicida Atualizado',
        'forma': 'Forma Teste PUT',
        'quantidade': 99
    }
    
    response_put = agente_client.put(
        f'/larvicida/{ULTIMO_LARVICIDA_ID_PARA_TESTE}', 
        data=update_payload
    )
    
    assert response_put.status_code == 200
    data_put = response_put.json['data']
    assert data_put['larvicida_id'] == ULTIMO_LARVICIDA_ID_PARA_TESTE
    assert data_put['tipo'] == 'Tipo Larvicida Atualizado'
    assert data_put['quantidade'] == '99'


    # # --- 2. TESTE DE DELETE ---
    response_delete_1 = agente_client.delete(f'/larvicida/{ULTIMO_LARVICIDA_ID_PARA_TESTE}')
    
    assert response_delete_1.status_code == 200
    assert response_delete_1.json['message'] == f"larvicida with ID {ULTIMO_LARVICIDA_ID_PARA_TESTE} deleted successfully."

    # --- 3. VERIFICAÇÃO (DELETE NOVAMENTE) ---
    # Tentamos deletar o *mesmo* ID novamente.
    # A API deve agora retornar 404 (Not Found), provando que foi deletado.
    response_delete_2 = agente_client.delete(f'/larvicida/{ULTIMO_LARVICIDA_ID_PARA_TESTE}')
    
    assert response_delete_2.status_code == 404
    assert response_delete_2.json['error'] == "larvicida de campo not found"


# --- Testes de Adulticida ---

def test_adulticida_update_e_delete(agente_client):
    """
    Testa o fluxo completo de UPDATE (PUT) e DELETE para um adulticida existente.
    """
    # De acordo com seu backup.sql, o adulticida com ID 1 existe.
    ADULTICIDA_ID_PARA_TESTE = 1
    
    # --- 1. TESTE DE UPDATE (PUT) ---
    update_payload = {
        'tipo': 'Tipo Adulticida Atualizado',
        'quantidade': 77
    }
    
    response_put = agente_client.put(
        f'/adulticida/{ADULTICIDA_ID_PARA_TESTE}', 
        data=update_payload
    )
    
    assert response_put.status_code == 200
    data_put = response_put.json['data']
    assert data_put['adulticida_id'] == ADULTICIDA_ID_PARA_TESTE
    assert data_put['tipo'] == 'Tipo Adulticida Atualizado'
    assert data_put['quantidade'] == '77'

    # --- 2. TESTE DE DELETE ---
    response_delete_1 = agente_client.delete(f'/adulticida/{ADULTICIDA_ID_PARA_TESTE}')
    
    assert response_delete_1.status_code == 200
    assert response_delete_1.json['message'] == f"adulticida with ID {ADULTICIDA_ID_PARA_TESTE} deleted successfully."

    # --- 3. VERIFICAÇÃO (DELETE NOVAMENTE) ---
    response_delete_2 = agente_client.delete(f'/adulticida/{ADULTICIDA_ID_PARA_TESTE}')
    
    assert response_delete_2.status_code == 404
    assert response_delete_2.json['error'] == "adulticida de campo not found"