# testes/test_registro_de_campo.py
import pytest
import io
import json

def test_registro_de_campo_crud_workflow(agente_client, mocker):
    """
    Testa o fluxo completo de CRUD (Create -> Update -> Delete)
    para um 'registro_de_campo'.
    Este teste simula:
    - Autenticação como Agente
    - Upload de múltiplos arquivos para o blob
    - Envio de dados complexos (JSON em strings)
    - Deleção de arquivos do blob
    """

    # --- 1. SETUP: MOCK (Simulação) do Vercel Blob ---
    
    # Criamos uma lista para rastrear todas as URLs que o mock "criou".
    urls_criadas_no_blob = []

    def mock_put_side_effect(path, data, options):
        """
        Esta função será chamada toda vez que 'put()' for invocado.
        Ela cria uma URL falsa e a adiciona à nossa lista de rastreamento.
        """
        url = f'https://fake-blob.com/{path}'
        urls_criadas_no_blob.append(url)
        return {'url': url}

    
    # Mock 'put' na sua rota POST
    mock_put_post = mocker.patch(
        'routes.registro_de_campo.post_one_registro_de_campo.put', # Caminho para a função 'put' usada no POST
        side_effect=mock_put_side_effect
    )
    
    # Mock 'put' na sua rota PUT (Update)
    mock_put_update = mocker.patch(
        'routes.registro_de_campo.update.put', # Caminho para a função 'put' usada no UPDATE
        side_effect=mock_put_side_effect
    )

    # Mock 'del_blob' na sua rota DELETE
    mock_del = mocker.patch(
        'routes.registro_de_campo.delete.delete', # Caminho para a função 'delete' usada no DELETE
        return_value=None
    )
    
    # Variável para armazenar o ID do registro criado
    registro_id_criado = None


    # --- 2. ETAPA CREATE (POST) ---
    try:
        # 2.1 Preparar dados do POST
        larvicidas_post = [{'tipo': 'temefos', 'forma': 'g', 'quantidade': 10}]
        fake_file_1 = (io.BytesIO(b"dados_do_arquivo_1"), 'foto_larva.jpg')
        fake_file_2 = (io.BytesIO(b"dados_do_arquivo_2"), 'foto_casa.png')

        payload_post = {
            'imovel_numero': 123,
            'imovel_lado': 'A',
            'imovel_categoria_da_localidade': 'L',
            'imovel_tipo': 'C',
            'imovel_status': 'N',
            'imovel_complemento': 'Fundos',
            'formulario_tipo': 'F1',
            'li': 'true',
            'pe': 'false',
            't': 'false',
            'df': 'false',
            'pve': 'false',
            'numero_da_amostra': 'A123',
            'quantiade_tubitos': 2,
            'observacao': 'Observação do teste POST.',
            'area_de_visita_id': 1, # ID válido do backup.sql (agente_client tem acesso)
            'a1': 5, 'a2': 0, 'b': 2, 'c': 0, 'd1': 0, 'd2': 0, 'e': 0,
            'larvicidas': json.dumps(larvicidas_post),
            'adulticidas': json.dumps([]),
            'files': [fake_file_1, fake_file_2] # Lista de arquivos
        }
        
        # 2.2 Fazer a requisição POST
        response_post = agente_client.post('/registro_de_campo', data=payload_post)
        
        # 2.3 Verificar POST
        assert response_post.status_code == 201, f"Erro no POST: {response_post.json}"
        data_post = response_post.json['data']
        registro_id_criado = data_post['registro_de_campo_id']
        
        assert registro_id_criado is not None
        assert data_post['imovel_numero'] == '123'
        assert data_post['observacao'] == 'Observação do teste POST.'
        assert len(data_post['files']) == 2 # Verificou os 2 arquivos
        assert data_post['files']['Arquivo 1'].endswith('foto_larva.jpg')
        
        # Verificar se o mock 'put' foi chamado 2 vezes
        assert mock_put_post.call_count == 2
        # Verificar se nossa lista de rastreamento tem 2 URLs
        assert len(urls_criadas_no_blob) == 2


        # --- 3. ETAPA UPDATE (PUT) ---
        
        # 3.1 Preparar dados do PUT
        larvicidas_put = [
            {'tipo': 'temefos', 'forma': 'g', 'quantidade': 5}, # Mudou a quantidade
            {'tipo': 'pyriproxyfen', 'forma': 'l', 'quantidade': 2} # Adicionou um novo
        ]
        fake_file_3 = (io.BytesIO(b"novo_relatorio"), 'relatorio.pdf')

        payload_put = {
            # É preciso enviar todos os campos obrigatórios novamente
            'imovel_numero': 456, # Valor ATUALIZADO
            'imovel_lado': 'B',
            'imovel_categoria_da_localidade': 'L',
            'imovel_tipo': 'T',
            'imovel_status': 'F',
            'imovel_complemento': 'Casa da frente',
            'formulario_tipo': 'F2',
            'li': 'false', 'pe': 'true', 't': 'false', 'df': 'false', 'pve': 'true',
            'numero_da_amostra': 'B456',
            'quantiade_tubitos': 3,
            'observacao': 'Observação ATUALIZADA pelo PUT.', # Valor ATUALIZADO
            'area_de_visita_id': 1,
            'a1': 1, 'a2': 1, 'b': 1, 'c': 1, 'd1': 1, 'd2': 1, 'e': 1,
            'larvicidas': json.dumps(larvicidas_put), # Valor ATUALIZADO
            'adulticidas': json.dumps([]),
            'files': [fake_file_3] # Adiciona 1 novo arquivo
        }

        # 3.2 Fazer a requisição PUT
        response_put = agente_client.put(
            f'/registro_de_campo/{registro_id_criado}', 
            data=payload_put
        )
        
        # 3.3 Verificar PUT
        assert response_put.status_code == 200, f"Erro no PUT: {response_put.json}"
        data_put = response_put.json['data']
        
        assert data_put['imovel_numero'] == '456'
        assert data_put['observacao'] == 'Observação ATUALIZADA pelo PUT.'
        assert len(data_put['files']) == 1 # Resposta do PUT mostra só o novo arquivo
        assert data_put['files']['Arquivo 1'].endswith('relatorio.pdf')
        assert data_put['larvicidas'] == larvicidas_put # Verifica se o JSON foi atualizado

        # Verificar se o mock 'put' do update foi chamado 1 vez
        assert mock_put_update.call_count == 1
        # Verificar se nossa lista de rastreamento agora tem 3 URLs no total
        assert len(urls_criadas_no_blob) == 3


    finally:
        # --- 4. ETAPA DELETE (Cleanup) ---
        
        # Este 'finally' garante que o DELETE sempre rode,
        # mesmo se o PUT falhar, limpando o que o POST criou.
        
        if registro_id_criado is None:
            # Se o POST falhou, não há nada para deletar.
            # Força o teste a falhar se ainda não falhou.
            assert registro_id_criado is not None, "Falha na etapa CREATE. Nada para deletar."

        # 4.1 Fazer a requisição DELETE
        response_delete = agente_client.delete(
            f'/registro_de_campo/{registro_id_criado}'
        )
        
        # 4.2 Verificar DELETE
        assert response_delete.status_code == 200, f"Erro no DELETE: {response_delete.json}"
        assert f"ID {registro_id_criado}" in response_delete.json['message']

        # 4.3 VERIFICAR MOCKS (A parte mais importante)
        
        # Garantir que a função 'delete' (do blob) foi chamada exatamente 1 vez
        mock_del.assert_called_once()
        
        # Pegar a lista de URLs que foi passada para 'delete'
        # 'call_args[0]' é uma tupla de argumentos. [0] é o primeiro argumento.
        urls_deletadas = mock_del.call_args[0][0]
        
        # Comparamos as URLs que *esperamos* (que rastreamos)
        # com as URLs que a rota *realmente* tentou deletar.
        # Usamos 'set' para ignorar a ordem da lista.
        assert set(urls_deletadas) == set(urls_criadas_no_blob)
        assert len(urls_deletadas) == 3 # Garante que as 3 foram deletadas


# --- Testes de Segurança e Permissões ---

def test_seguranca_supervisor_nao_pode_criar_registro(auth_client):
    """
    TESTE DE SEGURANÇA:
    Verifica se um SUPERVISOR (auth_client) NÃO PODE criar um registro de campo.
    A rota '/registro_de_campo' (POST) exige um 'agente_id' no token,
    que o supervisor não possui.
    """
    payload_post = {
        'imovel_numero': '777',
        'imovel_lado': 'A',
        'imovel_categoria_da_localidade': 'L',
        'imovel_tipo': 'C',
        'imovel_status': 'N',
        'area_de_visita_id': 1,
        'a1': 1, 'a2': 0, 'b': 0, 'c': 0, 'd1': 0, 'd2': 0, 'e': 0,
        'larvicidas': json.dumps([]),
        'adulticidas': json.dumps([])
    }
    
    response_post = auth_client.post('/registro_de_campo', data=payload_post)
    
    # A rota deve retornar 401 (Unauthorized) ou 403 (Forbidden) 
    # pois o token do supervisor não contém 'agente_id'.
    assert response_post.status_code == 401
    assert "É nescessário ser agente" in response_post.json['error']

def test_seguranca_agente_nao_pode_registrar_em_area_nao_associada(agente_client):
    """
    TESTE DE LÓGICA DE NEGÓCIO (403):
    Verifica se o Agente 1 (do 'agente_client') NÃO PODE registrar um 
    imóvel na Área de Visita 2, pois ele não está associado a ela no backup.sql.
    """
    payload_post = {
        'imovel_numero': '888',
        'imovel_lado': 'B',
        'imovel_categoria_da_localidade': 'U',
        'imovel_tipo': 'R',
        'imovel_status': 'F',
        'area_de_visita_id': 2, # <-- Área 2 (Jatiúca), agente 1 não tem acesso
        'a1': 1, 'a2': 0, 'b': 0, 'c': 0, 'd1': 0, 'd2': 0, 'e': 0,
        'larvicidas': json.dumps([]),
        'adulticidas': json.dumps([])
    }
    
    response_post = agente_client.post('/registro_de_campo', data=payload_post)
    
    # A rota deve retornar 403 (Forbidden)
    assert response_post.status_code == 403
    assert "Agente não está associado" in response_post.json['error']


# --- Testes de Validação de Entrada (Erros 400) ---

def test_falha_post_campos_obrigatorios_ausentes(agente_client):
    """
    TESTE DE VALIDAÇÃO (400):
    Verifica se a API retorna 400 Bad Request se um campo obrigatório
    (como 'imovel_status') estiver faltando.
    """
    payload_post = {
        'imovel_numero': '999',
        'imovel_lado': 'A',
        'imovel_categoria_da_localidade': 'L',
        'imovel_tipo': 'C',
        # 'imovel_status': 'N', <-- CAMPO FALTANDO
        'area_de_visita_id': 1,
        'a1': 1, 'a2': 0, 'b': 0, 'c': 0, 'd1': 0, 'd2': 0, 'e': 0,
        'larvicidas': json.dumps([]),
        'adulticidas': json.dumps([])
    }
    
    response_post = agente_client.post('/registro_de_campo', data=payload_post)
    
    assert response_post.status_code == 400
    assert "imovel_status is required" in response_post.json['error']

def test_falha_post_tipo_de_dado_invalido(agente_client):
    """
    TESTE DE VALIDAÇÃO (400):
    Verifica se a API retorna 400 Bad Request se um campo numérico
    (como 'a1') for enviado como texto não-numérico.
    """
    payload_post = {
        'imovel_numero': '1000',
        'imovel_lado': 'A',
        'imovel_categoria_da_localidade': 'L',
        'imovel_tipo': 'C',
        'imovel_status': 'N',
        'area_de_visita_id': 1,
        'a1': "texto_invalido", # <-- TIPO INVÁLIDO (deveria ser int)
        'a2': 0, 'b': 0, 'c': 0, 'd1': 0, 'd2': 0, 'e': 0,
        'larvicidas': json.dumps([]),
        'adulticidas': json.dumps([])
    }
    
    response_post = agente_client.post('/registro_de_campo', data=payload_post)
    
    assert response_post.status_code == 400
    assert "Invalid input for" in response_post.json['error']


# --- Testes de Rotas Auxiliares e 404 ---

def test_rotas_nao_encontrado_404(agente_client):
    """
    TESTE DE 404:
    Verifica se as rotas GET, PUT e DELETE retornam 404 (Not Found)
    ao tentar acessar um ID que não existe.
    """
    id_inexistente = 999999
    
    # GET /registro_de_campo/<id>
    response_get = agente_client.get(f'/registro_de_campo/{id_inexistente}')
    assert response_get.status_code == 404
    assert response_get.json['error'] == "Registro de campo not found"

    # PUT /registro_de_campo/<id>
    # (Envia um payload mínimo apenas para a rota de PUT ser atingida)
    payload_put = {
        'imovel_numero': '1', 'imovel_lado': 'A', 'imovel_categoria_da_localidade': 'L',
        'imovel_tipo': 'C', 'imovel_status': 'N', 'area_de_visita_id': 1,
        'a1': 0, 'a2': 0, 'b': 0, 'c': 0, 'd1': 0, 'd2': 0, 'e': 0,
        'larvicidas': '[]', 'adulticidas': '[]'
    }
    response_put = agente_client.put(f'/registro_de_campo/{id_inexistente}', data=payload_put)
    assert response_put.status_code == 404
    assert "não encontrado" in response_put.json['error']

    # DELETE /registro_de_campo/<id>
    response_delete = agente_client.delete(f'/registro_de_campo/{id_inexistente}')
    assert response_delete.status_code == 404
    assert response_delete.json['error'] == "Registro de campo not found"

def test_marcar_caso_confirmado(agente_client):
    """
    Testa a rota auxiliar 'PUT /casos_confirmado/<id>'.
    
    1. Busca o registro ID 1 (do backup) e verifica se 'caso_comfirmado' é 'true'.
       (No backup, o registro 1 já é 'true', então vamos verificar isso).
    2. Busca o registro ID 2 (do backup) e verifica se 'caso_comfirmado' é 'false'.
    3. Chama a rota PUT para marcar o ID 2.
    4. Busca o registro ID 2 novamente e verifica se 'caso_comfirmado' agora é 'true'.
    """
    
    # 1. Verifica o estado inicial do Registro 1 (já é true no backup)
    resp_get_1 = agente_client.get('/registro_de_campo/1')
    assert resp_get_1.status_code == 200
    assert resp_get_1.json['caso_comfirmado'] == True

    # 2. Verifica o estado inicial do Registro 2 (é false no backup)
    resp_get_2_antes = agente_client.get('/registro_de_campo/2')
    assert resp_get_2_antes.status_code == 200
    assert resp_get_2_antes.json['caso_comfirmado'] == False
    
    # 3. Chama a rota PUT para marcar o Registro 2
    resp_put = agente_client.put('/casos_confirmado/2')
    assert resp_put.status_code == 200
    assert "Caso confirmado com sucesso" in resp_put.json['message']
    
    # 4. Verifica se o Registro 2 foi atualizado
    resp_get_2_depois = agente_client.get('/registro_de_campo/2')
    assert resp_get_2_depois.status_code == 200
    assert resp_get_2_depois.json['caso_comfirmado'] == True