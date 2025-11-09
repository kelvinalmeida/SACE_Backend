import pytest
import io

# Variável global não é mais necessária
# artigo_id_criado = None

def test_acesso_publico_get_artigos(public_client):
    """
    Testa se qualquer cliente (mesmo sem login) pode LER (GET) os artigos.
    """
    # 1. Testar GET /artigo (Listar todos)
    response_get_all = public_client.get('/artigo')
    assert response_get_all.status_code == 200
    
    assert isinstance(response_get_all.json, list)
    assert len(response_get_all.json) >= 10 # Do backup.sql

    # 2. Testar GET /artigo/<id> (Buscar um)
    response_get_one = public_client.get('/artigo/1')
    assert response_get_one.status_code == 200
    assert response_get_one.json['artigo_id'] == 1
    assert response_get_one.json['titulo'] == 'Dengue: O que é, causas e tratamento'

    # 3. Testar GET /artigo/img/<id> (Buscar imagem)
    # --- CORREÇÃO PARA BLOB ---
    # A rota agora REDIRECIONA (302) para a URL.
    response_get_img = public_client.get('/artigo/img/1')
    assert response_get_img.status_code == 302
    assert 'Location' in response_get_img.headers
    assert response_get_img.headers['Location'].startswith('https://')

    # 4. Testar 404 para artigo/imagem inexistente
    response_get_404 = public_client.get('/artigo/99999')
    assert response_get_404.status_code == 404
    
    response_get_img_404 = public_client.get('/artigo/img/99999')
    assert response_get_img_404.status_code == 404

def test_falha_agente_criar_artigo(agente_client):
    """
    Testa a segurança: Garante que um AGENTE não pode criar,
    atualizar ou deletar artigos. (Sem alterações)
    """
    payload_post = {
        'titulo': 'Tentativa de Post por Agente',
        'descricao': 'Agente não pode postar',
        'link_artigo': 'https://agente.com'
    }
    response_post = agente_client.post('/artigo', data=payload_post)
    assert response_post.status_code == 403
    assert "Acesso negado: É necessário ser supervisor" in response_post.json['error']

    # Testar PUT
    response_put = agente_client.put('/artigo/1', data=payload_post)
    assert response_put.status_code == 403

    # Testar DELETE
    response_delete = agente_client.delete('/artigo/1')
    assert response_delete.status_code == 403


# --- NOVO TESTE DE WORKFLOW (Substitui os 2 testes de supervisor) ---

def test_supervisor_artigo_crud_workflow(auth_client, public_client, mocker):
    """
    Testa o fluxo CRUD (Create, Update, Delete) para um artigo
    usando o cliente supervisor ('auth_client') e mocks.
    
    Este teste substitui 'test_supervisor_workflow_artigo_crud' 
    e 'test_supervisor_deletar_artigo'.
    """
    
    # --- 1. MOCK (Simulação) do Vercel Blob ---
    mock_url_retornada = 'https://fake.blob.url/artigo_teste_pytest.jpg'
    
    # Simula o 'put' na rota de CRIAR
    mock_blob_put = mocker.patch(
        'routes.artigo.post_one_artigo.put', 
        return_value={'url': mock_url_retornada}
    )

    # Simula o 'delete' na rota de DELETAR
    mock_blob_del = mocker.patch(
        'routes.artigo.delete.delete', 
        return_value=None
    )

    # Variáveis locais para armazenar o estado (IDs, URLs)
    artigo_id_criado = None
    url_imagem_criada = None
    
    # O try...finally garante que o delete seja chamado
    # mesmo se um 'assert' no meio do teste falhar.
    try:
        # --- 2. CRIAR (POST) com Imagem ---
        fake_image = (io.BytesIO(b"meus-dados-de-imagem-falsa"), 'teste.jpg')
        
        payload_post = {
            'titulo': 'Artigo de Teste (Pytest)',
            'descricao': 'Descrição de um artigo criado via teste.',
            'link_artigo': 'https://pytest.org',
            'imagem': fake_image
        }
        
        response_post = auth_client.post('/artigo', data=payload_post)
        
        assert response_post.status_code == 201
        data_post = response_post.json
        assert data_post['titulo'] == 'Artigo de Teste (Pytest)'
        
        # O campo 'imagem_nome' agora armazena a URL
        assert data_post['imagem_nome'] == mock_url_retornada
        
        # O mock 'put' foi chamado 1 vez?
        mock_blob_put.assert_called_once()
        
        # Armazena os IDs localmente
        artigo_id_criado = data_post['artigo_id']
        url_imagem_criada = data_post['imagem_nome']
        assert artigo_id_criado is not None

        # --- 3. ATUALIZAR (PUT) o artigo (só texto) ---
        payload_put = {
            'titulo': 'Artigo de Teste ATUALIZADO (Pytest)',
            'descricao': 'Descrição atualizada.',
            'link_artigo': 'https://pytest.org/updated'
            # Sem 'imagem'
        }
        
        response_put = auth_client.put(
            f'/artigo/{artigo_id_criado}', 
            data=payload_put
        )
        
        assert response_put.status_code == 200
        data_put = response_put.json
        assert data_put['artigo_id'] == artigo_id_criado
        assert data_put['titulo'] == 'Artigo de Teste ATUALIZADO (Pytest)'
        # Verifica se a imagem (que não foi enviada) foi mantida
        assert data_put['imagem_nome'] == url_imagem_criada

    finally:
        # --- 4. DELETAR (DELETE) ---
        # Este bloco 'finally' garante que o delete sempre execute
        # (se o 'artigo_id_criado' foi definido), limpando o DB.
        
        assert artigo_id_criado is not None, "Falha na etapa de CRIAÇÃO, nada para deletar."

        response_delete = auth_client.delete(f'/artigo/{artigo_id_criado}')
        
        assert response_delete.status_code == 200
        assert response_delete.json['artigo_id_deletado'] == artigo_id_criado

        # O mock 'del' foi chamado 1 vez com a URL correta?
        mock_blob_del.assert_called_once_with([url_imagem_criada])

        # --- 5. VERIFICAR (GET) ---
        # Usamos o cliente público para garantir que o artigo foi deletado
        response_get = public_client.get(f'/artigo/{artigo_id_criado}')
        assert response_get.status_code == 404