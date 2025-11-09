import pytest

# Usaremos o ano 2025 e o ciclo 2, que existem e têm dados no backup.sql
TEST_ANO = 2025
TEST_CICLO = 2

def test_graficos_rotas_publicas(client):
    """
    Testa todas as rotas de gráfico PÚBLICAS (sem necessidade de login).
    Elas devem retornar 200 OK e dados no formato correto.
    """
    
    # Rota: /grafico/acoes_bloqueio/<ano>
    resp_acoes = client.get(f'/grafico/acoes_bloqueio/{TEST_ANO}')
    assert resp_acoes.status_code == 200
    assert 'labels' in resp_acoes.json
    assert 'datasets' in resp_acoes.json

    # Rota: /grafico/atividades_realizadas/<ano>/<ciclo>
    resp_atividades = client.get(f'/grafico/atividades_realizadas/{TEST_ANO}/{TEST_CICLO}')
    assert resp_atividades.status_code == 200
    assert 'LI' in resp_atividades.json
    assert 'PE' in resp_atividades.json

    # Rota: /grafico/casos_confirmados/<ano>/<ciclo>
    resp_casos = client.get(f'/grafico/casos_confirmados/{TEST_ANO}/{TEST_CICLO}')
    assert resp_casos.status_code == 200
    assert 'dados_grafico' in resp_casos.json
    assert 'resumo_ciclo_atual' in resp_casos.json

    # Rota: /grafico/casos_por_ciclo/<ano>
    resp_casos_ciclo = client.get(f'/grafico/casos_por_ciclo/{TEST_ANO}')
    assert resp_casos_ciclo.status_code == 200
    assert 'labels' in resp_casos_ciclo.json
    assert 'datasets' in resp_casos_ciclo.json

    # Rota: /grafico/depositos_identificados/<ano>/<ciclo>
    resp_dep_id = client.get(f'/grafico/depositos_identificados/{TEST_ANO}/{TEST_CICLO}')
    assert resp_dep_id.status_code == 200
    assert 'dados_grafico' in resp_dep_id.json
    assert 'resumo_ciclo_atual' in resp_dep_id.json

    # Rota: /grafico/depositos_por_ciclo/<ano>
    resp_dep_ciclo = client.get(f'/grafico/depositos_por_ciclo/{TEST_ANO}')
    assert resp_dep_ciclo.status_code == 200
    assert 'labels' in resp_dep_ciclo.json
    assert 'datasets' in resp_dep_ciclo.json

    # Rota: /grafico/depositos_tratados/<ano>/<ciclo>
    resp_dep_trat = client.get(f'/grafico/depositos_tratados/{TEST_ANO}/{TEST_CICLO}')
    assert resp_dep_trat.status_code == 200
    assert 'larvicidas' in resp_dep_trat.json
    assert 'adulticidas' in resp_dep_trat.json

    # Rota: /grafico/focos_positivos/<ano>/<ciclo>
    resp_focos = client.get(f'/grafico/focos_positivos/{TEST_ANO}/{TEST_CICLO}')
    assert resp_focos.status_code == 200
    assert 'dados_grafico' in resp_focos.json
    assert 'resumo_ciclo_atual' in resp_focos.json

    # Rota: /heatmap_data/<ano>/<ciclo>
    resp_heatmap = client.get(f'/heatmap_data/{TEST_ANO}/{TEST_CICLO}')
    assert resp_heatmap.status_code == 200
    assert isinstance(resp_heatmap.json, list)

    # Rota: /heatmap_data/latest
    resp_heatmap_latest = client.get('/heatmap_data/latest')
    assert resp_heatmap_latest.status_code == 200
    assert isinstance(resp_heatmap_latest.json, list)

    # Rota: /dashboard_summary/<ano>/<ciclo>
    resp_dash = client.get(f'/dashboard_summary/{TEST_ANO}/{TEST_CICLO}')
    assert resp_dash.status_code == 200
    assert 'depositos' in resp_dash.json
    assert 'casos_confirmados' in resp_dash.json
    assert 'areas_risco' in resp_dash.json

    # Rota: /dashboard_summary/latest
    resp_dash_latest = client.get('/dashboard_summary/latest')
    assert resp_dash_latest.status_code == 200
    assert 'depositos' in resp_dash_latest.json
    assert 'casos_confirmados' in resp_dash_latest.json
    
    # Rota: /grafico/imoveis_trabalhados/<ano>/<ciclo>
    resp_imoveis = client.get(f'/grafico/imoveis_trabalhados/{TEST_ANO}/{TEST_CICLO}')
    assert resp_imoveis.status_code == 200
    assert 'inspecionados' in resp_imoveis.json
    assert 'total' in resp_imoveis.json

    # Rota: /grafico/taxa_de_reincidencia/<ano>/<ciclo>
    resp_reincidencia = client.get(f'/grafico/taxa_de_reincidencia/{TEST_ANO}/{TEST_CICLO}')
    assert resp_reincidencia.status_code == 200
    assert isinstance(resp_reincidencia.json, dict) # Espera um dicionário de bairros

    # Rota: /grafico/total_doentes_confirmados/<ano>/<ciclo>
    resp_doentes = client.get(f'/grafico/total_doentes_confirmados/{TEST_ANO}/{TEST_CICLO}')
    assert resp_doentes.status_code == 200
    assert 'dados_grafico' in resp_doentes.json
    assert 'resumo_ciclo_atual' in resp_doentes.json

def test_grafico_summary_pdf_permissoes(public_client, agente_client, auth_client):
    """
    Testa a rota protegida do PDF.
    - 401 para PÚBLICO
    - 200 para AGENTE
    - 200 para SUPERVISOR
    """
    
    # 1. Testar como PÚBLICO (sem login)
    resp_public = public_client.get(f'/summary_pdf/{TEST_ANO}/{TEST_CICLO}')
    # A rota é protegida por @token_required
    assert resp_public.status_code == 401
    assert "O token está faltando!" in resp_public.json['error']

    # 2. Testar como AGENTE (agente_client)
    resp_agente = agente_client.get(f'/summary_pdf/{TEST_ANO}/{TEST_CICLO}')
    
    assert resp_agente.status_code == 200
    # Verifica se o servidor retornou um arquivo PDF
    assert resp_agente.mimetype == 'application/pdf'
    # Verifica se o arquivo tem um tamanho razoável (não está vazio)
    assert len(resp_agente.data) > 1000 

    # 3. Testar como SUPERVISOR (auth_client)
    resp_super = auth_client.get(f'/summary_pdf/{TEST_ANO}/{TEST_CICLO}')
    
    assert resp_super.status_code == 200
    assert resp_super.mimetype == 'application/pdf'
    assert len(resp_super.data) > 1000

    # (Uma verificação mais profunda poderia comparar os tamanhos dos PDFs
    # para garantir que o PDF do supervisor (com todos os agentes) é
    # maior que o PDF do agente (apenas com ele mesmo), mas isso é complexo.
    # Por enquanto, verificar o acesso 200 é o mais importante.)
    assert len(resp_super.data) >= len(resp_agente.data)