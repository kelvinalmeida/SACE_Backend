import pytest

def test_permissoes_agente_ciclos(agente_client):
    """
    Testa as permissões de um AGENTE:
    - PODE ler as rotas GET.
    - NÃO PODE modificar (POST).
    """
    
    # 1. Agente PODE ler /ciclos/status
    # No estado inicial do backup.sql, o ciclo 4 (2025/2) está ativo.
    resp_status = agente_client.get('/ciclos/status')
    assert resp_status.status_code == 200
    assert resp_status.json['status'] == 'ativo' 

    # 2. Agente PODE ler /anos_ciclos
    resp_anos = agente_client.get('/anos_ciclos')
    assert resp_anos.status_code == 200
    assert '2024' in resp_anos.json
    assert '2025' in resp_anos.json
    # Verifica o estado inicial do backup (2025 tem ciclos 1 e 2)
    assert resp_anos.json['2025'] == [1, 2, 3, 4]

    # 3. Agente NÃO PODE /finalizar_ciclo
    resp_finalizar = agente_client.post('/finalizar_ciclo')
    assert resp_finalizar.status_code == 403
    assert "Acesso negado" in resp_finalizar.json['error']

    # 4. Agente NÃO PODE /criar_ciclo
    resp_criar = agente_client.post('/criar_ciclo')
    assert resp_criar.status_code == 403
    assert "Acesso negado" in resp_criar.json['error']


def test_workflow_supervisor_ciclo_completo(auth_client):
    """
    Testa o fluxo completo de 'finalizar' e 'criar' um ciclo
    como SUPERVISOR.
    
    Este teste MUDA O ESTADO do banco de dados de teste (o que é esperado).
    
    1. Verifica se o ciclo 4 (2025/2) está ativo (estado inicial do backup).
    2. Tenta criar um novo ciclo (deve falhar, pois já existe um ativo).
    3. Finaliza o ciclo 4.
    4. Verifica se o status da API mudou para 'inativo'.
    5. Cria um novo ciclo (deve ser o ciclo 5, que é o 2025/3).
    6. Verifica se o status mudou para 'ativo' novamente (com o ciclo 5).
    7. Verifica se a rota /anos_ciclos agora reflete o novo ciclo (2025: [1, 2, 3]).
    """
    
    # --- 1. Verificar estado inicial (Ciclo 4, 2025/2, ativo) ---
    resp_status_1 = auth_client.get('/ciclos/status')
    assert resp_status_1.status_code == 200
    assert resp_status_1.json['status'] == 'ativo'
    detalhes_1 = resp_status_1.json['detalhes']
    assert detalhes_1['ciclo_id'] == 8
    assert detalhes_1['ano'] == 2025
    assert detalhes_1['ciclo_numero'] == 4

    # --- 2. Tentar criar ciclo (deve falhar, pois o 4 está ativo) ---
    # (Baseado na lógica de 'routes/ciclo/criar_ciclo.py')
    resp_criar_fail = auth_client.post('/criar_ciclo')
    assert resp_criar_fail.status_code == 400
    assert "Já existe um ciclo ativo" in resp_criar_fail.json['error']

    # --- 3. Finalizar o ciclo 4 ---
    resp_finalizar = auth_client.post('/finalizar_ciclo')
    # A rota 'finalizar_ciclo.py' retorna 201
    assert resp_finalizar.status_code == 201 
    assert "Ciclo desativado" in resp_finalizar.json['message']
    # Confirma que o ciclo finalizado foi o ID 4
    assert resp_finalizar.json['novo_ciclo']['id'] == 4 

    # --- 4. Verificar estado (agora deve ser 'inativo') ---
    resp_status_2 = auth_client.get('/ciclos/status')
    assert resp_status_2.status_code == 200
    assert resp_status_2.json['status'] == 'inativo'

    # --- 5. Criar novo ciclo (deve ser 2025/3, ID 5) ---
    resp_criar_ok = auth_client.post('/criar_ciclo')
    assert resp_criar_ok.status_code == 201
    assert "Novo ciclo criado com sucesso!" in resp_criar_ok.json['message']
    
    novo_ciclo = resp_criar_ok.json['novo_ciclo']
    assert novo_ciclo['ano'] == 2025  # O ano não mudou
    assert novo_ciclo['numero'] == 3  # O ciclo incrementou (de 2 para 3)
    assert novo_ciclo['id'] == 5      # O ID da tabela (PK) incrementou (de 4 para 5)

    # --- 6. Verificar estado (ativo novamente, com o ciclo 5) ---
    resp_status_3 = auth_client.get('/ciclos/status')
    assert resp_status_3.status_code == 200
    assert resp_status_3.json['status'] == 'ativo'
    detalhes_3 = resp_status_3.json['detalhes']
    assert detalhes_3['ciclo_id'] == 5
    assert detalhes_3['ciclo_numero'] == 3

    # --- 7. Verificar /anos_ciclos (agora deve ter 2025: [1, 2, 3]) ---
    resp_anos = auth_client.get('/anos_ciclos')
    assert resp_anos.status_code == 200
    assert resp_anos.json['2025'] == [1, 2, 3] # A lista deve ter sido atualizada