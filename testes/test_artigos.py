import pytest
import io

# Variável global para armazenar o ID do artigo criado
# para que os testes possam se comunicar (ex: um teste cria, outro deleta)
artigo_id_criado = None

def test_acesso_publico_get_artigos(client):
    """
    Testa se qualquer cliente (mesmo sem login) pode LER (GET) os artigos.
    """
    # 1. Testar GET /artigo (Listar todos)
    response_get_all = client.get('/artigo')
    assert response_get_all.status_code == 200
    
    # Verifica se o JSON retornado é uma lista
    assert isinstance(response_get_all.json, list)
    # Verifica se os artigos do backup.sql estão presentes
    assert len(response_get_all.json) >= 10
    assert response_get_all.json[0]['titulo'] == 'Boletins Epidemiológicos de Arboviroses'

    # 2. Testar GET /artigo/<id> (Buscar um)
    response_get_one = client.get('/artigo/1')
    assert response_get_one.status_code == 200
    assert response_get_one.json['artigo_id'] == 1
    assert response_get_one.json['titulo'] == 'Dengue: O que é, causas e tratamento'

    # 3. Testar GET /artigo/img/<id> (Buscar imagem)
    response_get_img = client.get('/artigo/img/1')
    assert response_get_img.status_code == 200
    assert response_get_img.mimetype == 'image/jpeg' # Verifica se é uma imagem

    # 4. Testar 404 para artigo/imagem inexistente
    response_get_404 = client.get('/artigo/99999')
    assert response_get_404.status_code == 404
    
    response_get_img_404 = client.get('/artigo/img/99999')
    assert response_get_img_404.status_code == 404

def test_falha_agente_criar_artigo(agente_client):
    """
    Testa a segurança: Garante que um AGENTE não pode criar,
    atualizar ou deletar artigos.
    """
    payload_post = {
        'titulo': 'Tentativa de Post por Agente',
        'descricao': 'Agente não pode postar',
        'link_artigo': 'https://agente.com'
    }
    response_post = agente_client.post('/artigo', data=payload_post)
    # A rota de artigo (post_one_artigo.py) retorna 403 Forbidden
    assert response_post.status_code == 403
    assert "Acesso negado: É necessário ser supervisor" in response_post.json['error']

    # Testar PUT
    response_put = agente_client.put('/artigo/1', data=payload_post)
    assert response_put.status_code == 403
    
    # Testar DELETE
    response_delete = agente_client.delete('/artigo/1')
    assert response_delete.status_code == 403

def test_supervisor_workflow_artigo_crud(auth_client):
    """
    Testa o fluxo completo de CRUD (Create, Update, Delete) para um artigo
    usando o cliente supervisor ('auth_client').
    
    NOTA: Este teste também testa o upload de imagem.
    """
    global artigo_id_criado
    
    # --- 1. CRIAR (POST) com Imagem ---
    
    # Criamos um arquivo de imagem falso em memória
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
    assert data_post['imagem_nome'] == 'teste.jpg'
    
    # Armazena o ID globalmente para os próximos testes
    artigo_id_criado = data_post['artigo_id']
    assert artigo_id_criado is not None

    # --- 2. ATUALIZAR (PUT) o artigo criado ---
    
    payload_put = {
        'titulo': 'Artigo de Teste ATUALIZADO (Pytest)',
        'descricao': 'Descrição atualizada.',
        'link_artigo': 'https://pytest.org/updated'
    }
    
    response_put = auth_client.put(
        f'/artigo/{artigo_id_criado}', 
        data=payload_put
    )
    
    assert response_put.status_code == 200
    data_put = response_put.json
    assert data_put['artigo_id'] == artigo_id_criado
    assert data_put['titulo'] == 'Artigo de Teste ATUALIZADO (Pytest)'
    # Verifica se a imagem (que não foi enviada no PUT) foi mantida
    assert data_put['imagem_nome'] == 'teste.jpg'


def test_supervisor_deletar_artigo(auth_client, client):
    """
    Testa o DELETE.
    Este teste depende que 'test_supervisor_workflow_artigo_crud' tenha rodado antes
    (o que o pytest geralmente faz em ordem de arquivo).
    """
    global artigo_id_criado
    assert artigo_id_criado is not None, "O teste de criação de artigo falhou ou não rodou."

    # --- 3. DELETAR (DELETE) ---
    response_delete = auth_client.delete(f'/artigo/{artigo_id_criado}')
    
    assert response_delete.status_code == 200
    assert response_delete.json['artigo_id_deletado'] == artigo_id_criado

    # --- 4. VERIFICAR (GET) ---
    # Usamos o cliente público para garantir que o artigo foi deletado
    response_get = client.get(f'/artigo/{artigo_id_criado}')
    assert response_get.status_code == 404