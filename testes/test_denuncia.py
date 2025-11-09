import pytest
import io

# (Variável global e os dois primeiros testes permanecem iguais)
# ...

def test_supervisor_workflow_denuncia_crud(auth_client, mocker): # <-- Adicionado 'mocker'
    """
    TESTE DE WORKFLOW (SUPERVISOR):
    Testa o fluxo completo de CRUD (Criar, Atualizar, Deletar) para um supervisor.
    """
    global denuncia_id_criada
    
    # --- 1. SETUP: MOCK DO VERCEL BLOB ---
    # URL falsa que o mock 'put' retornará
    mock_url_retornada = 'https://fake.blob.url/denuncia_id_X_foto_teste_denuncia.jpg'

    # Mock 'put' na rota de CRIAR (post_one_denuncia.py)
    mock_put_post = mocker.patch(
        'routes.denuncia.post_one_denuncia.put', 
        return_value={'url': mock_url_retornada}
    )
    
    # Mock 'put' na rota de ATUALIZAR (update.py)
    # (Caso o teste de update também enviasse arquivos)
    mock_put_update = mocker.patch(
        'routes.denuncia.update.put', 
        return_value={'url': 'https://fake.blob.url/update.jpg'}
    )

    # Mock 'delete' na rota de DELETAR (delete.py)
    mock_del = mocker.patch(
        'routes.denuncia.delete.delete', 
        return_value=None
    )

    # --- 2. CRIAR DENÚNCIA (POST) ---
    try:
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
            'files': [fake_file] 
        }
        
        response_post = auth_client.post('/denuncia', data=payload_post)
        
        assert response_post.status_code == 201, f"Erro: {response_post.json}"
        data_post = response_post.json['data']
        
        assert data_post['rua_avenida'] == 'Rua do Teste Pytest'
        assert data_post['bairro'] == 'Bairro Pytest'
        assert data_post['agente_responsavel_id'] == '2'
        
        # --- CORREÇÃO AQUI ---
        # Verifica se o mock foi chamado
        mock_put_post.assert_called_once()
        # Verifica se a URL retornada pelo mock está no JSON
        assert data_post['files']['Arquivo 1'] == mock_url_retornada
        # (Opcional) Verifica se a URL termina com o nome do arquivo
        assert data_post['files']['Arquivo 1'].endswith('foto_teste_denuncia.jpg')
        # --- FIM DA CORREÇÃO ---

        denuncia_id_criada = data_post['denuncia_id']
        assert denuncia_id_criada is not None

        # --- 3. ATUALIZAR DENÚNCIA (PUT) ---
        payload_put = {
            'rua_avenida': 'Rua ATUALIZADA Pytest',
            'numero': 888,
            'bairro': 'Bairro Pytest (Atualizado)',
            'tipo_imovel': 'Terreno Baldio (Teste)',
            'data_denuncia': '2025-11-01',
            'hora_denuncia': '15:00:00',
            'status': 'Pendente', # Campo obrigatório na rota de update
            'observacoes': 'Registro atualizado pelo teste.',
            'agente_responsavel_id': 4,
        }
        
        response_put = auth_client.put(
            f'/denuncia/{denuncia_id_criada}',
            data=payload_put
        )
        
        assert response_put.status_code == 201
        data_put = response_put.json['data']
        assert data_put['denuncia_id'] == denuncia_id_criada
        assert data_put['rua_avenida'] == 'Rua ATUALIZADA Pytest'
        assert data_put['status'] == 'Pendente'
        assert data_put['numero'] == 888
        assert data_put['bairro'] == 'Bairro Pytest (Atualizado)'
        assert data_put['tipo_imovel'] == 'Terreno Baldio (Teste)'
        assert data_put['data_denuncia'] == '2025-11-01'
        assert data_put['hora_denuncia'] == '15:00:00'
        assert data_put['agente_responsavel_id'] == '4'


    finally:
        # --- 4. DELETAR DENÚNCIA (DELETE) ---
        # O 'finally' garante que o delete rode mesmo se o 'assert' do PUT falhar
        
        if denuncia_id_criada is None:
            pytest.fail("Falha na etapa de CRIAÇÃO. O ID da denúncia não foi criado.")

        response_delete = auth_client.delete(f'/denuncia/{denuncia_id_criada}')
        
        assert response_delete.status_code == 200
        assert response_delete.json['denuncia_id'] == denuncia_id_criada
        
        # Verifica se o mock de DELETAR foi chamado com a URL correta
        # A rota 'delete.py' busca a URL no DB antes de deletar.
        # O mock_url_retornada é a URL que foi "salva" no DB pelo POST mockado.
        mock_del.assert_called_once_with([mock_url_retornada])

        # --- 5. VERIFICAR DELEÇÃO (GET) ---
        response_get_final = auth_client.get(f'/denuncia/{denuncia_id_criada}')
        assert response_get_final.status_code == 404
        assert response_get_final.json['error'] == 'denuncia não encontrada'