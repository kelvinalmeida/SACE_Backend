# ⚠️ Ponto Importante sobre as Cores (Níveis de Risco):

# Sua base de dados atual não armazena diretamente o nível de risco (Preta, Vermelha, Laranja, Amarela) para cada area_de_visita. Para calcular isso, precisamos definir os critérios.

#     Como exemplo, vou usar a seguinte lógica hipotética baseada nas contagens por area_de_visita dentro do ciclo:

#         Preta (Emergência): >= 5 casos confirmados E >= 10 focos encontrados

#         Vermelha (Perigo): >= 3 casos confirmados E >= 5 focos encontrados

#         Laranja (Alerta): >= 1 caso confirmado OU >= 3 focos encontrados

#         Amarela (Atenção): >= 1 foco encontrado (e não se encaixa nas anteriores)

#         (Implícito) Normal/Sem Risco: 0 casos e 0 focos


from flask import jsonify, current_app
from db import create_connection
# from routes.login.token_required import token_required # Descomente se precisar de autenticação
from .bluprint import graficos
import logging
from collections import Counter # Usaremos Counter para contar as cores

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

def calculate_risk_level(casos, focos):
    """
    Define o nível de risco (cor) baseado no número de casos e focos.
    *** AJUSTE ESTA LÓGICA CONFORME OS SEUS CRITÉRIOS REAIS ***
    """
    if casos >= 5 and focos >= 10:
        return "Preta"
    elif casos >= 3 and focos >= 5:
        return "Vermelha"
    elif casos >= 1 or focos >= 3:
        return "Laranja"
    elif focos >= 1:
        return "Amarela"
    else:
        return "Normal" # Ou None, se não quiser contar áreas sem risco

# Descomente o decorator se precisar de autenticação
# @token_required
# def get_dashboard_summary(current_user, ano, ciclo):
@graficos.route('/dashboard_summary/<int:ano>/<int:ciclo>', methods=['GET'])
def get_dashboard_summary(ano, ciclo):
    """
    Endpoint para obter um resumo de dados para o dashboard de um ciclo específico.

    Retorna contagem de depósitos por tipo, casos confirmados por doença e
    contagem de áreas de visita por nível de risco (cores).
    """
    conn = None
    cursor = None
    summary_data = {
        "depositos": {"a1": 0, "a2": 0, "b": 0, "c": 0, "d1": 0, "d2": 0, "e": 0},
        "casos_confirmados": {"dengue": 0, "zika": 0, "chikungunya": 0},
        "areas_risco": {"Preta": 0, "Vermelha": 0, "Laranja": 0, "Amarela": 0}
    }

    try:
        conn = create_connection(current_app.config['SQLALCHEMY_DATABASE_URI'])
        if conn is None:
            logging.error("Falha na conexão com o banco de dados")
            return jsonify({"error": "Falha na conexão com o banco de dados"}), 500

        cursor = conn.cursor()

        # --- 1. Encontrar o ciclo_id ---
        find_ciclo_id_query = """
            SELECT ciclo_id
            FROM ciclos
            WHERE EXTRACT(YEAR FROM ano_de_criacao)::INTEGER = %s AND ciclo = %s
            LIMIT 1;
        """
        cursor.execute(find_ciclo_id_query, (ano, ciclo))
        ciclo_result = cursor.fetchone()

        if not ciclo_result:
            logging.warning(f"Ciclo não encontrado para ano {ano}, ciclo {ciclo}")
            return jsonify({"error": f"Ciclo {ciclo} do ano {ano} não encontrado."}), 404

        ciclo_id = ciclo_result['ciclo_id']
        logging.info(f"Ciclo ID encontrado: {ciclo_id} para Ano: {ano}, Ciclo: {ciclo}")

        # --- 2. Query para Depósitos e Casos Confirmados (Agregado Total) ---
        counts_query = """
            SELECT
                -- Soma dos depósitos
                COALESCE(SUM(d.a1), 0) AS total_a1,
                COALESCE(SUM(d.a2), 0) AS total_a2,
                COALESCE(SUM(d.b), 0) AS total_b,
                COALESCE(SUM(d.c), 0) AS total_c,
                COALESCE(SUM(d.d1), 0) AS total_d1,
                COALESCE(SUM(d.d2), 0) AS total_d2,
                COALESCE(SUM(d.e), 0) AS total_e,
                -- Contagem de casos confirmados por tipo
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Dengue' THEN 1 ELSE 0 END) AS casos_dengue,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Zica' THEN 1 ELSE 0 END) AS casos_zika,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Chikungunya' THEN 1 ELSE 0 END) AS casos_chikungunya
            FROM
                registro_de_campo rc
            LEFT JOIN
                depositos d ON rc.deposito_id = d.deposito_id
            WHERE
                rc.ciclo_id = %s;
        """
        cursor.execute(counts_query, (ciclo_id,))
        counts_result = cursor.fetchone()

        if counts_result:
            summary_data["depositos"]["a1"] = int(counts_result["total_a1"])
            summary_data["depositos"]["a2"] = int(counts_result["total_a2"])
            summary_data["depositos"]["b"] = int(counts_result["total_b"])
            summary_data["depositos"]["c"] = int(counts_result["total_c"])
            summary_data["depositos"]["d1"] = int(counts_result["total_d1"])
            summary_data["depositos"]["d2"] = int(counts_result["total_d2"])
            summary_data["depositos"]["e"] = int(counts_result["total_e"])
            summary_data["casos_confirmados"]["dengue"] = int(counts_result["casos_dengue"])
            summary_data["casos_confirmados"]["zika"] = int(counts_result["casos_zika"])
            summary_data["casos_confirmados"]["chikungunya"] = int(counts_result["casos_chikungunya"])

        # --- 3. Query para calcular Níveis de Risco por Área ---
        risk_level_query = """
            SELECT
                -- Removido av.area_de_visita_id, não é mais necessário aqui
                av.latitude,  -- Incluído para o GROUP BY
                av.longitude, -- Incluído para o GROUP BY
                av.bairro,    -- Incluído para o GROUP BY
                -- Soma total de depósitos (focos) por ponto geográfico
                COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0) AS focos_encontrados_agg,
                -- Contagem total de casos confirmados por ponto geográfico
                SUM(CASE WHEN rc.caso_comfirmado = TRUE THEN 1 ELSE 0 END) AS total_casos_confirmados_agg
            FROM
                area_de_visita av
            LEFT JOIN
                registro_de_campo rc ON av.area_de_visita_id = rc.area_de_visita_id
                                   AND rc.ciclo_id = %s -- Filtro do ciclo no JOIN
            LEFT JOIN
                depositos d ON rc.deposito_id = d.deposito_id
            WHERE
                 av.latitude IS NOT NULL AND av.longitude IS NOT NULL
            GROUP BY
                -- MODIFICADO: Agrupa por ponto geográfico, não por area_id individual
                av.latitude,
                av.longitude,
                av.bairro;
        """
        cursor.execute(risk_level_query, (ciclo_id,))
        area_results = cursor.fetchall() # Agora contém dados agregados por ponto geográfico

        # --- 4. Calcular e Contar os Níveis de Risco (a lógica aqui permanece a mesma) ---
        risk_counts = Counter()
        for area_agg in area_results: # Itera sobre os dados agregados
            # MODIFICADO: Usa os nomes das colunas agregadas da nova query
            casos = int(area_agg['total_casos_confirmados_agg'])
            focos = int(area_agg['focos_encontrados_agg'])
            level = calculate_risk_level(casos, focos)
            if level != "Normal":
                 risk_counts[level] += 1

        # Atualiza o dicionário de resumo com as contagens (esta parte não muda)
        summary_data["areas_risco"]["Preta"] = risk_counts.get("Preta", 0)
        summary_data["areas_risco"]["Vermelha"] = risk_counts.get("Vermelha", 0)
        summary_data["areas_risco"]["Laranja"] = risk_counts.get("Laranja", 0)
        summary_data["areas_risco"]["Amarela"] = risk_counts.get("Amarela", 0)

        logging.info(f"Resumo do dashboard gerado para Ciclo ID {ciclo_id}.")

        return jsonify(summary_data), 200

    except Exception as e:
        logging.error(f"Erro ao gerar resumo do dashboard: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": "Ocorreu um erro interno ao processar a solicitação.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()