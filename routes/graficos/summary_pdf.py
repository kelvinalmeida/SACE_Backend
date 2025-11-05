import logging
from flask import jsonify, current_app, make_response
from db import create_connection
# from routes.login.token_required import token_required # Uncomment if this route needs to be protected
from .bluprint import graficos
from fpdf import FPDF
from datetime import datetime

# Configuração básica de log
logging.basicConfig(level=logging.INFO)

# --- Copied from your heatmap_data.py for consistent logic ---
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
        return "Normal"
# --- End of copied function ---


class PDF(FPDF):
    """
    Custom PDF class to create a standardized Header and Footer.
    """
    def __init__(self, ano, ciclo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ano = ano
        self.ciclo_num = ciclo
        self.alias_nb_pages() # Enables page numbering like "Page 1 of {nb}"
        self.col_widths = [] # To store agent table column widths

    def header(self):
        self.set_font('Arial', 'B', 15)
        # Center title
        self.cell(0, 10, f'Resumo do Ciclo {self.ciclo_num}/{self.ano}', 0, 1, 'C')
        self.ln(10) # Line break

    def footer(self):
        self.set_y(-15) # Position 1.5 cm from bottom
        self.set_font('Arial', 'I', 8)
        
        # Page number
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')
        
        # Generation date
        self.set_x(10) # Move to left
        self.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 0, 'L')

    def add_bairro_summary(self, row_data):
        """
        Adds a formatted block for a single neighborhood's summary.
        """
        # Check for page break before adding a new block
        if self.get_y() > (self.h - 80): # 80mm from bottom margin
            self.add_page()
            
        casos_total = int(row_data['total_casos_confirmados'])
        focos = int(row_data['focos_encontrados'])
        # Calculate risk using the consistent function
        nivel_risco = calculate_risk_level(casos_total, focos)

        # Section Title (Bairro)
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230) # Light gray background
        self.cell(0, 8, f"Resumo da Zona: {row_data['bairro']}", 1, 1, 'L', fill=True)

        # Key-Value pairs
        self.set_font('Arial', 'B', 10)
        self.cell(95, 7, "Nível de Risco:", 1, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(95, 7, f"{nivel_risco}", 1, 1, 'R')
        
        self.set_font('Arial', 'B', 10)
        self.cell(95, 7, "Total de Casos Confirmados:", 1, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(95, 7, f"{casos_total}", 1, 1, 'R')
        
        self.set_font('Arial', 'B', 10)
        self.cell(95, 7, "Total de Focos Encontrados:", 1, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(95, 7, f"{focos}", 1, 1, 'R')
        
        self.set_font('Arial', 'B', 10)
        self.cell(95, 7, "Casos de Dengue:", 1, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(95, 7, f"{int(row_data['casos_dengue'])}", 1, 1, 'R')
        
        self.set_font('Arial', 'B', 10)
        self.cell(95, 7, "Casos de Zika:", 1, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(95, 7, f"{int(row_data['casos_zika'])}", 1, 1, 'R')
        
        self.set_font('Arial', 'B', 10)
        self.cell(95, 7, "Casos de Chikungunya:", 1, 0, 'L')
        self.set_font('Arial', '', 10)
        self.cell(95, 7, f"{int(row_data['casos_chikungunya'])}", 1, 1, 'R')
        
        self.ln(5) # Add a small break after the block

    def add_agent_summary_table(self, agent_data):
        self.ln(5)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, "Resumo por Agente", 0, 1, 'C')
        self.ln(2)

        # Table Header
        self.set_font('Arial', 'B', 8)
        self.set_fill_color(230, 230, 230)
        
        # Calculate widths
        page_w = self.epw
        self.col_widths = {
            'name': page_w * 0.30,
            'other': page_w * 0.10
        }
        
        self.cell(self.col_widths['name'], 6, "Agente", 1, 0, 'C', fill=True)
        self.cell(self.col_widths['other'], 6, "Total", 1, 0, 'C', fill=True)
        self.cell(self.col_widths['other'], 6, "Inspec.", 1, 0, 'C', fill=True)
        self.cell(self.col_widths['other'], 6, "Bloq.", 1, 0, 'C', fill=True)
        self.cell(self.col_widths['other'], 6, "Fech.", 1, 0, 'C', fill=True)
        self.cell(self.col_widths['other'], 6, "Recus.", 1, 0, 'C', fill=True)
        self.cell(self.col_widths['other'], 6, "Focos", 1, 0, 'C', fill=True)
        self.cell(self.col_widths['other'], 6, "Casos", 1, 1, 'C', fill=True)

        # Table Rows
        self.set_font('Arial', '', 7)
        for agent in agent_data:
            # Check for page break
            if self.get_y() > (self.h - 30): # 30mm from bottom margin
                self.add_page()
                # Re-draw header on new page
                self.set_font('Arial', 'B', 8)
                self.cell(self.col_widths['name'], 6, "Agente", 1, 0, 'C', fill=True)
                self.cell(self.col_widths['other'], 6, "Total", 1, 0, 'C', fill=True)
                self.cell(self.col_widths['other'], 6, "Inspec.", 1, 0, 'C', fill=True)
                self.cell(self.col_widths['other'], 6, "Bloq.", 1, 0, 'C', fill=True)
                self.cell(self.col_widths['other'], 6, "Fech.", 1, 0, 'C', fill=True)
                self.cell(self.col_widths['other'], 6, "Recus.", 1, 0, 'C', fill=True)
                self.cell(self.col_widths['other'], 6, "Focos", 1, 0, 'C', fill=True)
                self.cell(self.col_widths['other'], 6, "Casos", 1, 1, 'C', fill=True)
                self.set_font('Arial', '', 7)

            # Agent Name
            self.cell(self.col_widths['name'], 6, f"{agent['nome_completo']}", 1, 0, 'L')
            
            # Numbers
            self.cell(self.col_widths['other'], 6, f"{agent['total_registros']}", 1, 0, 'C')
            self.cell(self.col_widths['other'], 6, f"{agent['inspecionados']}", 1, 0, 'C')
            self.cell(self.col_widths['other'], 6, f"{agent['bloqueados']}", 1, 0, 'C')
            self.cell(self.col_widths['other'], 6, f"{agent['fechados']}", 1, 0, 'C')
            self.cell(self.col_widths['other'], 6, f"{agent['recusados']}", 1, 0, 'C')
            self.cell(self.col_widths['other'], 6, f"{agent['total_focos']}", 1, 0, 'C')
            self.cell(self.col_widths['other'], 6, f"{agent['total_casos_confirmados']}", 1, 1, 'C')

    # --- START OF ORIGINAL METHOD ---
    def add_deposits_and_treatments_summary(self, deposits_data, larvicides_data, adulticides_data):
        self.ln(5)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, "Resumo de Depósitos e Tratamentos", 0, 1, 'C')
        self.ln(2)

        # --- Deposits Table ---
        self.set_font('Arial', 'B', 11)
        self.cell(0, 7, "Total de Depósitos Encontrados", 0, 1, 'L')
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(240, 240, 240) # Lighter gray for this
        
        # Calculate widths for 3 columns
        col_w = self.epw / 3 
        
        # Row 1
        self.cell(col_w, 6, "A1 (Armazen. elevado)", 1, 0, 'C', fill=True)
        self.cell(col_w, 6, "A2 (Armazen. ao solo)", 1, 0, 'C', fill=True)
        self.cell(col_w, 6, "B (Móveis)", 1, 1, 'C', fill=True) # New line
        self.set_font('Arial', '', 9)
        self.cell(col_w, 6, f"{deposits_data.get('total_a1', 0)}", 1, 0, 'C')
        self.cell(col_w, 6, f"{deposits_data.get('total_a2', 0)}", 1, 0, 'C')
        self.cell(col_w, 6, f"{deposits_data.get('total_b', 0)}", 1, 1, 'C') # New line
        
        # Row 2
        self.set_font('Arial', 'B', 9)
        self.cell(col_w, 6, "C (Fixos)", 1, 0, 'C', fill=True)
        self.cell(col_w, 6, "D1 (Pneus)", 1, 0, 'C', fill=True)
        self.cell(col_w, 6, "D2 (Lixo/Sucata)", 1, 1, 'C', fill=True) # New line
        self.set_font('Arial', '', 9)
        self.cell(col_w, 6, f"{deposits_data.get('total_c', 0)}", 1, 0, 'C')
        self.cell(col_w, 6, f"{deposits_data.get('total_d1', 0)}", 1, 0, 'C')
        self.cell(col_w, 6, f"{deposits_data.get('total_d2', 0)}", 1, 1, 'C') # New line

        # Row 3 (Just 'E')
        self.set_font('Arial', 'B', 9)
        self.cell(col_w, 6, "E (Naturais)", 1, 0, 'C', fill=True)
        self.set_font('Arial', '', 9)
        self.cell(col_w, 6, f"{deposits_data.get('total_e', 0)}", 1, 0, 'C')
        # Create "empty" cells to fill the row width
        self.set_font('Arial', 'B', 9)
        self.cell(col_w, 6, "", 1, 0, 'C', fill=True) 
        self.set_font('Arial', '', 9)
        self.cell(col_w, 6, "", 1, 1, 'C')
        self.ln(5)

        # --- Treatments Table (Side-by-side) ---
        # Splitting the page for two tables
        half_w = self.epw / 2 - 5 # Half page width minus a small gap
        
        # Get Y position before starting tables
        y_before_table = self.get_y()
        
        # --- Larvicides Table (Left) ---
        self.set_font('Arial', 'B', 11)
        self.cell(half_w, 7, "Total de Larvicidas", 0, 1, 'L')
        self.set_font('Arial', 'B', 9)
        self.cell(half_w * 0.7, 6, "Tipo", 1, 0, 'C', fill=True)
        self.cell(half_w * 0.3, 6, "Qtd.", 1, 1, 'C', fill=True)
        self.set_font('Arial', '', 9)
        if not larvicides_data:
            self.cell(half_w, 6, "Nenhum aplicado", 1, 1, 'C')
        for item in larvicides_data:
            self.cell(half_w * 0.7, 6, f"{item['tipo']}", 1, 0, 'L')
            self.cell(half_w * 0.3, 6, f"{item['total_quantidade']}", 1, 1, 'R')
        y_after_larv_table = self.get_y() # Save Y position after this table

        # --- Adulticides Table (Right) ---
        self.set_xy(10 + half_w + 5, y_before_table) # Move cursor to the right, at the same starting Y
        self.set_font('Arial', 'B', 11)
        self.cell(half_w, 7, "Total de Adulticidas", 0, 1, 'L')
        self.set_x(10 + half_w + 5) # Align table header
        self.set_font('Arial', 'B', 9)
        self.cell(half_w * 0.7, 6, "Tipo", 1, 0, 'C', fill=True)
        self.cell(half_w * 0.3, 6, "Qtd.", 1, 1, 'C', fill=True)
        self.set_font('Arial', '', 9)
        if not adulticides_data:
            self.set_x(10 + half_w + 5)
            self.cell(half_w, 6, "Nenhum aplicado", 1, 1, 'C')
        for item in adulticides_data:
            self.set_x(10 + half_w + 5)
            self.cell(half_w * 0.7, 6, f"{item['tipo']}", 1, 0, 'L')
            self.cell(half_w * 0.3, 6, f"{item['total_quantidade']}", 1, 1, 'R')
        y_after_adult_table = self.get_y() # Save Y position after this table
        
        # Set Y to the bottom of the *tallest* of the two tables
        self.set_y(max(y_after_larv_table, y_after_adult_table))
    # --- END OF ORIGINAL METHOD ---

    # --- INÍCIO DO NOVO MÉTODO ADICIONADO ---
    def add_doencas_confirmadas_table(self, doencas_data):
        """
        Adiciona uma tabela com o detalhamento de doenças confirmadas (tabela 'doencas_confirmadas').
        """
        self.ln(5)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 8, "Doenças Confirmadas (Tabela Oficial)", 0, 1, 'C')
        self.ln(2)

        if not doencas_data:
            self.set_font('Arial', '', 12)
            self.cell(0, 10, "Nenhum caso confirmado (tabela oficial) registrado para este ciclo.", 0, 1, 'C')
            return

        # --- Definição das Larguras da Tabela ---
        page_w = self.epw # Largura efetiva da página
        col_widths = {
            'nome': page_w * 0.30,      # 30%
            'doenca': page_w * 0.15,    # 15%
            'bairro': page_w * 0.20,    # 20%
            'rua': page_w * 0.25,       # 25%
            'numero': page_w * 0.10     # 10%
        }

        # --- Cabeçalho da Tabela ---
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(230, 230, 230)
        self.cell(col_widths['nome'], 6, "Nome do Paciente", 1, 0, 'C', fill=True)
        self.cell(col_widths['doenca'], 6, "Doença", 1, 0, 'C', fill=True)
        self.cell(col_widths['bairro'], 6, "Bairro", 1, 0, 'C', fill=True)
        self.cell(col_widths['rua'], 6, "Rua", 1, 0, 'C', fill=True)
        self.cell(col_widths['numero'], 6, "Nº", 1, 1, 'C', fill=True) # 1, 1 (quebra a linha)

        # --- Linhas da Tabela ---
        self.set_font('Arial', '', 8)
        for item in doencas_data:
            # Verifica se precisa pular a página
            if self.get_y() > (self.h - 30): # 30mm da margem inferior
                self.add_page()
                # Redesenha o cabeçalho
                self.set_font('Arial', 'B', 9)
                self.cell(col_widths['nome'], 6, "Nome do Paciente", 1, 0, 'C', fill=True)
                self.cell(col_widths['doenca'], 6, "Doença", 1, 0, 'C', fill=True)
                self.cell(col_widths['bairro'], 6, "Bairro", 1, 0, 'C', fill=True)
                self.cell(col_widths['rua'], 6, "Rua", 1, 0, 'C', fill=True)
                self.cell(col_widths['numero'], 6, "Nº", 1, 1, 'C', fill=True)
                self.set_font('Arial', '', 8)

            # Adiciona os dados (usando .get() e 'or' para tratar valores None)
            self.cell(col_widths['nome'], 6, f"{item.get('nome') or '-'}", 1, 0, 'L')
            self.cell(col_widths['doenca'], 6, f"{item.get('tipo_da_doenca') or '-'}", 1, 0, 'L')
            self.cell(col_widths['bairro'], 6, f"{item.get('bairro') or '-'}", 1, 0, 'L')
            self.cell(col_widths['rua'], 6, f"{item.get('rua') or '-'}", 1, 0, 'L')
            self.cell(col_widths['numero'], 6, f"{item.get('numero') or '-'}", 1, 1, 'C')

    # --- FIM DO NOVO MÉTODO ADICIONADO ---


# @token_required # Uncomment if this route needs to be protected
@graficos.route('/summary_pdf/<int:ano>/<int:ciclo>', methods=['GET'])
def get_summary_pdf(ano, ciclo):
    """
    Endpoint para obter um PDF com o resumo de dados agregados por área de visita.
    """
    conn = None
    cursor = None
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

        # --- 2. Query for Bairro Summary (Identical to heatmap_data.py) ---
        heatmap_query = """
            SELECT
                av.latitude, av.longitude, av.bairro,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Dengue' THEN 1 ELSE 0 END) AS casos_dengue,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Zica' THEN 1 ELSE 0 END) AS casos_zika,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE AND rc.formulario_tipo ILIKE 'Chikungunya' THEN 1 ELSE 0 END) AS casos_chikungunya,
                COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0) AS focos_encontrados,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE THEN 1 ELSE 0 END) AS total_casos_confirmados
            FROM area_de_visita av
            LEFT JOIN registro_de_campo rc ON av.area_de_visita_id = rc.area_de_visita_id AND rc.ciclo_id = %s
            LEFT JOIN depositos d ON rc.deposito_id = d.deposito_id
            WHERE av.latitude IS NOT NULL AND av.longitude IS NOT NULL
            GROUP BY av.latitude, av.longitude, av.bairro
            ORDER BY av.bairro;
        """
        cursor.execute(heatmap_query, (ciclo_id,))
        bairro_results = cursor.fetchall()
        logging.info(f"Dados para PDF (Resumo Bairros: {len(bairro_results)} pontos) recuperados.")

        # --- 3. Fetch Agent Summary Data ---
        agent_summary_query = """
            SELECT
                u.nome_completo,
                a.agente_id,
                COUNT(rc.registro_de_campo_id) AS total_registros,
                SUM(CASE WHEN rc.imovel_status = 'inspecionado' THEN 1 ELSE 0 END) AS inspecionados,
                SUM(CASE WHEN rc.imovel_status = 'bloqueado' THEN 1 ELSE 0 END) AS bloqueados,
                SUM(CASE WHEN rc.imovel_status = 'fechado' THEN 1 ELSE 0 END) AS fechados,
                SUM(CASE WHEN rc.imovel_status = 'recusado' THEN 1 ELSE 0 END) AS recusados,
                SUM(CASE WHEN rc.caso_comfirmado = TRUE THEN 1 ELSE 0 END) AS total_casos_confirmados,
                COALESCE(SUM(d.a1 + d.a2 + d.b + d.c + d.d1 + d.d2 + d.e), 0) AS total_focos
            FROM
                agente a
            JOIN
                usuario u ON a.usuario_id = u.usuario_id
            LEFT JOIN
                registro_de_campo rc ON a.agente_id = rc.agente_id AND rc.ciclo_id = %s
            LEFT JOIN
                depositos d ON rc.deposito_id = d.deposito_id
            GROUP BY
                a.agente_id, u.nome_completo
            ORDER BY
                u.nome_completo;
        """
        cursor.execute(agent_summary_query, (ciclo_id,))
        agent_results = cursor.fetchall()
        logging.info(f"Dados para PDF (Resumo Agentes: {len(agent_results)} agentes) recuperados.")

        # --- 4. START OF ORIGINAL QUERIES ---
        # Query for Total Deposits
        deposits_query = """
            SELECT
                COALESCE(SUM(d.a1), 0) AS total_a1,
                COALESCE(SUM(d.a2), 0) AS total_a2,
                COALESCE(SUM(d.b), 0) AS total_b,
                COALESCE(SUM(d.c), 0) AS total_c,
                COALESCE(SUM(d.d1), 0) AS total_d1,
                COALESCE(SUM(d.d2), 0) AS total_d2,
                COALESCE(SUM(d.e), 0) AS total_e
            FROM registro_de_campo rc
            LEFT JOIN depositos d ON rc.deposito_id = d.deposito_id
            WHERE rc.ciclo_id = %s;
        """
        cursor.execute(deposits_query, (ciclo_id,))
        deposits_result = cursor.fetchone()

        # Query for Larvicides
        larvicides_query = """
            SELECT
                l.tipo,
                SUM(l.quantidade) AS total_quantidade
            FROM larvicida l
            JOIN registro_de_campo rc ON l.registro_de_campo_id = rc.registro_de_campo_id
            WHERE rc.ciclo_id = %s AND l.tipo IS NOT NULL
            GROUP BY l.tipo
            ORDER BY l.tipo;
        """
        cursor.execute(larvicides_query, (ciclo_id,))
        larvicides_result = cursor.fetchall()

        # Query for Adulticides
        adulticides_query = """
            SELECT
                a.tipo,
                SUM(a.quantidade) AS total_quantidade
            FROM adulticida a
            JOIN registro_de_campo rc ON a.registro_de_campo_id = rc.registro_de_campo_id
            WHERE rc.ciclo_id = %s AND a.tipo IS NOT NULL
            GROUP BY a.tipo
            ORDER BY a.tipo;
        """
        cursor.execute(adulticides_query, (ciclo_id,))
        adulticides_result = cursor.fetchall()
        logging.info("Dados de depósitos e tratamentos recuperados.")
        # --- END OF ORIGINAL QUERIES ---

        # --- INÍCIO DA NOVA QUERY ADICIONADA ---
        # --- 5. Fetch Doenças Confirmadas Data ---
        doencas_query = """
            SELECT nome, tipo_da_doenca, rua, numero, bairro
            FROM doencas_confirmadas
            WHERE ciclo_id = %s
            ORDER BY bairro, rua, nome;
        """
        cursor.execute(doencas_query, (ciclo_id,))
        doencas_results = cursor.fetchall()
        logging.info(f"Dados para PDF (Doenças Confirmadas: {len(doencas_results)} casos) recuperados.")
        # --- FIM DA NOVA QUERY ADICIONADA ---


        # --- 6. Generate the PDF (ORDER CHANGED) ---
        pdf = PDF(ano=ano, ciclo=ciclo)
        pdf.add_page()
        
        # --- Section 1: Agent Summary (First) ---
        if agent_results:
            pdf.add_agent_summary_table(agent_results)
        else:
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, "Nenhum dado de agente encontrado para este ciclo.", 0, 1, 'C')
            
        # --- Section 2: Deposits and Treatments (Second) ---
        pdf.add_deposits_and_treatments_summary(
            deposits_result, 
            larvicides_result, 
            adulticides_result
        )

        # --- Section 3: Bairro/Zone Summary (Third, on a new page) ---
        pdf.add_page() 
        if not bairro_results:
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 10, "Nenhum dado de resumo por zona encontrado para este ciclo.", 0, 1, 'C')
        else:
            # Add a title for this section
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 8, "Resumo por Zona de Risco", 0, 1, 'C')
            pdf.ln(2)
            
            for row in bairro_results:
                pdf.add_bairro_summary(row)

        # --- INÍCIO DA NOVA SEÇÃO ADICIONADA ---
        # --- Section 4: Doenças Confirmadas (Fourth, on a new page) ---
        pdf.add_page()
        pdf.add_doencas_confirmadas_table(doencas_results)
        # --- FIM DA NOVA SEÇÃO ADICIONADA ---


        # --- 7. Prepare and return the PDF response ---
        pdf_output = bytes(pdf.output(dest='B'))
        
        response = make_response(pdf_output)
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set(
            'Content-Disposition', 
            'inline',
            filename=f'resumo_ciclo_{ano}_{ciclo}.pdf'
        )
        return response

    except Exception as e:
        logging.error(f"Erro ao gerar PDF: {e}", exc_info=True)
        return jsonify({"error": "Ocorreu um erro interno ao gerar o PDF.", "details": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()