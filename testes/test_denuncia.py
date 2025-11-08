import pytest
import io

# Usaremos esta variável global para passar o ID da denúncia
# recém-criada para os testes de update e delete.
denuncia_id_criada = None

def test_seguranca_agente_nao_pode_modificar_denuncia(agente_client):
    """
    TESTE DE SEGURANÇA:
    Verifica se um usuário com nível 'agente' NÃO PODE criar,
    atualizar ou deletar uma denúncia.
    """
    
    # --- 1. Tentar CRIAR (POST) ---
    payload_post = {
        'rua_avenida': 'Rua de Teste do Agente',
        'numero': 123,
        'bairro': 'Bairro Teste',
        'tipo_imovel': 'Residencial'
    }
    response_post = agente_client.post('/denuncia', data=payload_post)
    
    # A API deve proibir (Forbidden)
    assert response_post.status_code == 403
    assert "É nescessário ser supervisor" in response_post.json['error']

    # --- 2. Tentar ATUALIZAR (PUT) ---
    # Tenta atualizar a denúncia com ID 1 (do backup.sql)
    response_put = agente_client.put('/denuncia/1', data=payload_post)
    
    assert response_put.status_code == 403
    assert "É nescessário ser supervisor" in response_put.json['error']

    # --- 3. Tentar DELETAR (DELETE) ---
    response_delete = agente_client.delete('/denuncia/1')
    
    assert response_delete.status_code == 403
    assert "É nescessário ser supervisor" in response_delete.json['error']


def test_agente_pode_ler_denuncias(agente_client):
    """
    TESTE DE LEITURA:
    Verifica se um 'agente' (ou qualquer usuário logado) pode LER as denúncias.
    """
    
    # --- 1. LER TUDO (GET /denuncia) ---
    response_get_all = agente_client.get('/denuncia')
    assert response_get_all.status_code == 200
    
    # Verifica se o JSON retornado é uma lista
    assert isinstance(response_get_all.json, list)
    # Verifica se os 5 itens do backup.sql estão lá
    assert len(response_get_all.json) >= 5 

    # --- 2. LER UM (GET /denuncia/1) ---
    response_get_one = agente_client.get('/denuncia/1')
    assert response_get_one.status_code == 200
    assert response_get_one.json['denuncia_id'] == 1
    assert response_get_one.json['rua_avenida'] == 'Rua Engenheiro Mário de Gusmão'
    # Verifica se os arquivos foram anexados corretamente
    assert len(response_get_one.json['arquivos']) == 2
    assert response_get_one.json['arquivos'][0]['arquivo_nome'] == 'denuncia_1_foto_vasos_01.jpg'

    # --- 3. LER 404 (GET /denuncia/9999) ---
    response_get_404 = agente_client.get('/denuncia/99999')
    assert response_get_404.status_code == 404
    assert response_get_404.json['error'] == 'denuncia não encontrada'


def test_supervisor_workflow_denuncia_crud(auth_client):
    """
    TESTE DE WORKFLOW (SUPERVISOR):
    Testa o fluxo completo de CRUD (Criar, Atualizar, Deletar) para um supervisor.
    """
    global denuncia_id_criada
    
    # --- 1. CRIAR DENÚNCIA (POST) ---
    
    # Simula um arquivo de upload
    fake_file = (io.BytesIO(b"dados do arquivo de imagem"), 'foto_teste_denuncia.jpg')
    
    payload_post = {
        'rua_avenida': 'Rua do Teste Pytest',
        'numero': 777,
        'bairro': 'Bairro Pytest',
        'tipo_imovel': 'Terreno Baldio (Teste)',
        'data_denuncia': '2025-10-31',
        'hora_denuncia': '14:30:00',
        'observacoes': 'Criado pelo teste automatizado',
        'agente_responsavel_id': 2, # Agente 'admin' (Pedro C.)
        'files': [fake_file] # Envia como uma lista de arquivos
    }
    
    response_post = auth_client.post('/denuncia', data=payload_post)
    
    # A rota de criação retorna 201
    assert response_post.status_code == 201, f"Erro: {response_post.json}"
    data_post = response_post.json['data']
    
    assert data_post['rua_avenida'] == 'Rua do Teste Pytest'
    assert data_post['bairro'] == 'Bairro Pytest'
    assert data_post['agente_responsavel_id'] == '2'
    assert data_post['files']['Arquivo 1'] == 'foto_teste_denuncia.jpg'
    
    # Armazena o ID para os próximos testes
    denuncia_id_criada = data_post['denuncia_id']
    assert denuncia_id_criada is not None

    # --- 2. ATUALIZAR DENÚNCIA (PUT) ---
    
    payload_put = {
        'rua_avenida': 'Rua ATUALIZADA Pytest', # Alterado
        'numero': 888, # Alterado
        'bairro': 'Bairro Pytest (Atualizado)', # Alterado
        'tipo_imovel': 'Terreno Baldio (Teste)',
        'data_denuncia': '2025-11-01', # Alterado
        'hora_denuncia': '15:00:00', # Alterado
        'observacoes': 'Registro atualizado pelo teste.', # Alterado
        'agente_responsavel_id': 4, # Agente 'Carlos'
    }
    
    response_put = auth_client.put(
        f'/denuncia/{denuncia_id_criada}',
        data=payload_put
    )
    
    # A rota de update também retorna 201 (conforme o código)
    assert response_put.status_code == 201
    data_put = response_put.json['data']
    assert data_put['denuncia_id'] == denuncia_id_criada
    assert data_put['rua_avenida'] == 'Rua ATUALIZADA Pytest'
    assert data_put['numero'] == 888
    assert data_put['agente_responsavel_id'] == '4'

    # --- 3. DELETAR DENÚNCIA (DELETE) ---
    
    response_delete = auth_client.delete(f'/denuncia/{denuncia_id_criada}')
    
    assert response_delete.status_code == 200
    assert response_delete.json['denuncia_id'] == denuncia_id_criada
    
    # --- 4. VERIFICAR DELEÇÃO (GET) ---
    # Usamos o mesmo cliente para verificar se o ID sumiu
    response_get_final = auth_client.get(f'/denuncia/{denuncia_id_criada}')
    assert response_get_final.status_code == 404