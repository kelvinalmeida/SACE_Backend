import pytest
import json



def test_criar_registro_falha_como_supervisor(auth_client):
    """
    Testa se um SUPERVISOR (do fixture 'auth_client') NÃO PODE criar um registro de campo.
    Isso valida a proteção da sua rota.
    """
    # O 'auth_client' está logado como supervisor
    response = auth_client.post('/registro_de_campo', data={
        "imovel_numero": "123",
        "imovel_lado": "Par",
        # ... (não precisamos de todos os dados, esperamos que falhe antes)
    })
    
    # A rota retorna 401 com a mensagem de erro específica
    # print(">>>>>>>>>>>", response.json)
    assert response.status_code == 401
    assert "Invalid token: É nescessário ser agente para cadastrar registro de campo. Peça para um supervisor cadastrar você." in response.json['error']

def test_registro_de_campo_usuario_nao_pertence_area(agente_client):
    """
    Testa se um AGENTE NÃO PODE criar um registro de campo em uma área que não pertence a ele.
    Isso valida a proteção da sua rota.
    """
    # O 'agente_client' está logado como agente_id=1 (João da Silva)
    # Vamos tentar criar um registro em uma area_de_visita_id=999 (inexistente ou não pertencente)
    response = agente_client.post('/registro_de_campo', data={
        'imovel_numero': '101-TESTE',
        'imovel_lado': 'Par',
        'imovel_categoria_da_localidade': 'Urbana',
        'imovel_tipo': 'Residencial',
        'imovel_status': 'inspecionado',
        'imovel_complemento': 'Apto Teste',
        'formulario_tipo': 'Dengue',
        'li': 'false',  # Booleans são strings em forms
        'pe': 'false',
        't': 'true',
        'df': 'true',
        'pve': 'false',
        'numero_da_amostra': 'T-001',
        'quantiade_tubitos': '2',
        'observacao': 'Teste de observação',
        'area_de_visita_id': "999",  # Área que o agente não pertence
        'a1': '1',
        'a2': '2',
        'b': '0',
        'c': '1',
        'd1': '0',
        'd2': '3',
        'e': '0',
        # ... (outros dados mínimos)
    })
    
    # A rota deve retornar 403 Forbidden
    assert response.status_code == 403
    assert "Agente não está associado a área de visita informada." in response.json['error']

def test_registro_de_campo_workflow_completo(agente_client):
    """
    Testa o fluxo completo de CRUD (Criar, Ler, Deletar) para um registro de campo
    usando o cliente autenticado como AGENTE.
    """
    
    # --- 1. DADOS PARA O POST ---
    # Os dados são enviados como 'multipart/form-data', então tudo deve ser string.
    # O agente_id=1 (João da Silva) está associado à area_de_visita_id=1.
    # O ciclo_id=4 está ativo no backup.sql.
    payload = {
        'imovel_numero': '101-TESTE',
        'imovel_lado': 'Par',
        'imovel_categoria_da_localidade': 'Urbana',
        'imovel_tipo': 'Residencial',
        'imovel_status': 'inspecionado',
        'imovel_complemento': 'Apto Teste',
        'formulario_tipo': 'Dengue',
        'li': 'false',  # Booleans são strings em forms
        'pe': 'false',
        't': 'true',
        'df': 'true',
        'pve': 'false',
        'numero_da_amostra': 'T-001',
        'quantiade_tubitos': '2',
        'observacao': 'Teste de observação',
        'area_de_visita_id': '1',  # ID da área associada ao agente_id=1
        'a1': '1',
        'a2': '2',
        'b': '0',
        'c': '1',
        'd1': '0',
        'd2': '3',
        'e': '0',
        # Larvicidas e Adulticidas devem ser strings JSON
        'larvicidas': json.dumps([
            {"tipo": "Larvicida Teste", "forma": "g", "quantidade": 15}
        ]),
        'adulticidas': json.dumps([
            {"tipo": "Adulticida Teste", "quantidade": 100}
        ])
    }

    # --- 2. CRIAR (POST) ---
    response_post = agente_client.post('/registro_de_campo', data=payload)
    
    # Verifica se foi criado com sucesso
    assert response_post.status_code == 201, f"Erro: {response_post.json}"
    data_post = response_post.json['data']
    assert data_post['imovel_numero'] == '101-TESTE'
    assert data_post['a2'] == 2
    assert data_post['t'] is True  # Verifica se o boolean foi convertido
    assert 'registro_de_campo_id' in data_post
    
    # Guarda o ID do novo registro
    novo_registro_id = data_post['registro_de_campo_id']

    # --- 3. LER (GET) ---
    # Usamos o mesmo cliente (agente) para buscar o registro recém-criado
    response_get = agente_client.get(f'/registro_de_campo/{novo_registro_id}')
    
    assert response_get.status_code == 200
    data_get = response_get.json
    
    assert data_get['registro_de_campo_id'] == novo_registro_id
    assert data_get['imovel_numero'] == '101-TESTE'
    assert data_get['agente_nome'] == 'João da Silva' # Verifica o JOIN
    
    # Verifica os dados aninhados
    assert data_get['deposito']['a2'] == 2
    assert len(data_get['larvicidas']) == 1
    assert data_get['larvicidas'][0]['tipo'] == 'Larvicida Teste'
    assert len(data_get['adulticidas']) == 1
    assert data_get['adulticidas'][0]['tipo'] == 'Adulticida Teste'

    # --- 4. DELETAR (DELETE) ---
    # Qualquer usuário autenticado (agente ou supervisor) pode deletar
    response_delete = agente_client.delete(f'/registro_de_campo/{novo_registro_id}')
    
    assert response_delete.status_code == 200
    assert f"deleted successfully" in response_delete.json['message']

    # --- 5. VERIFICAR DELEÇÃO (GET) ---
    response_get_after_delete = agente_client.get(f'/registro_de_campo/{novo_registro_id}')
    
    # Deve retornar "Not Found"
    assert response_get_after_delete.status_code == 404