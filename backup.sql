--
-- PostgreSQL database dump
--

\restrict 3qEAE0GpvPeZ3AliDPoHJn2PHJmacy9g8pVfhKK5bUgxXGh0vyhJt0ObrkIzHqJ

-- Dumped from database version 18.0 (Debian 18.0-1.pgdg13+3)
-- Dumped by pg_dump version 18.0 (Debian 18.0-1.pgdg13+3)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: adulticida; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.adulticida (
    adulticida_id integer NOT NULL,
    registro_de_campo_id integer,
    tipo character varying(100),
    quantidade smallint
);


ALTER TABLE public.adulticida OWNER TO "user";

--
-- Name: adulticida_adulticida_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.adulticida ALTER COLUMN adulticida_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.adulticida_adulticida_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agente; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.agente (
    agente_id integer NOT NULL,
    usuario_id integer
);


ALTER TABLE public.agente OWNER TO "user";

--
-- Name: agente_agente_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.agente ALTER COLUMN agente_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.agente_agente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agente_area_de_visita; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.agente_area_de_visita (
    agente_area_de_visita_id integer NOT NULL,
    agente_id integer,
    area_de_visita_id integer
);


ALTER TABLE public.agente_area_de_visita OWNER TO "user";

--
-- Name: agente_area_de_visita_agente_area_de_visita_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.agente_area_de_visita ALTER COLUMN agente_area_de_visita_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.agente_area_de_visita_agente_area_de_visita_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: area_de_visita; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.area_de_visita (
    area_de_visita_id integer NOT NULL,
    supervisor_id integer,
    cep character varying(10),
    setor character varying(100),
    numero_quarteirao smallint,
    estado character varying(2),
    municipio character varying(100),
    bairro character varying(100),
    status character varying(50) NOT NULL,
    logadouro character varying(100)
);


ALTER TABLE public.area_de_visita OWNER TO "user";

--
-- Name: area_de_visita_area_de_visita_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.area_de_visita ALTER COLUMN area_de_visita_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.area_de_visita_area_de_visita_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: arquivos_denuncia; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.arquivos_denuncia (
    arquivo_denuncia_id integer NOT NULL,
    arquivo_nome character varying(100) NOT NULL,
    denuncia_id integer
);


ALTER TABLE public.arquivos_denuncia OWNER TO "user";

--
-- Name: arquivos_denuncia_arquivo_denuncia_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.arquivos_denuncia ALTER COLUMN arquivo_denuncia_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.arquivos_denuncia_arquivo_denuncia_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: artigo; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.artigo (
    artigo_id integer NOT NULL,
    supervisor_id integer,
    link_artigo character varying(500),
    titulo character varying(100) NOT NULL,
    data_criacao date,
    descricao character varying(300) NOT NULL,
    imagem_nome character varying(300)
);


ALTER TABLE public.artigo OWNER TO "user";

--
-- Name: artigo_artigo_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.artigo ALTER COLUMN artigo_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.artigo_artigo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ciclo_area_de_visita; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.ciclo_area_de_visita (
    ciclo_area_de_visita_id integer NOT NULL,
    ciclo_id integer,
    area_de_visita_id integer
);


ALTER TABLE public.ciclo_area_de_visita OWNER TO "user";

--
-- Name: ciclo_area_de_visita_ciclo_area_de_visita_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.ciclo_area_de_visita ALTER COLUMN ciclo_area_de_visita_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.ciclo_area_de_visita_ciclo_area_de_visita_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: ciclos; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.ciclos (
    ciclo_id integer NOT NULL,
    supervisor_id integer,
    ano_de_criacao date NOT NULL,
    encerramento date,
    ativo boolean NOT NULL,
    ciclo smallint NOT NULL
);


ALTER TABLE public.ciclos OWNER TO "user";

--
-- Name: ciclos_ciclo_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.ciclos ALTER COLUMN ciclo_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.ciclos_ciclo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: denuncia; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.denuncia (
    denuncia_id integer NOT NULL,
    supervisor_id integer,
    deposito_id integer,
    agente_responsavel_id integer,
    rua_avenida character varying(100) NOT NULL,
    numero smallint NOT NULL,
    bairro character varying(50) NOT NULL,
    tipo_imovel character varying(100) NOT NULL,
    status character varying(50) NOT NULL,
    endereco_complemento character varying(200),
    data_denuncia date,
    hora_denuncia time without time zone,
    observacoes character varying(255)
);


ALTER TABLE public.denuncia OWNER TO "user";

--
-- Name: denuncia_denuncia_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.denuncia ALTER COLUMN denuncia_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.denuncia_denuncia_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: depositos; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.depositos (
    deposito_id integer NOT NULL,
    a1 smallint,
    a2 smallint,
    b smallint,
    c smallint,
    d1 smallint,
    d2 smallint,
    e smallint
);


ALTER TABLE public.depositos OWNER TO "user";

--
-- Name: depositos_deposito_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.depositos ALTER COLUMN deposito_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.depositos_deposito_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: larvicida; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.larvicida (
    larvicida_id integer NOT NULL,
    registro_de_campo_id integer,
    tipo character varying(100),
    forma character varying(100),
    quantidade smallint
);


ALTER TABLE public.larvicida OWNER TO "user";

--
-- Name: larvicida_larvicida_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.larvicida ALTER COLUMN larvicida_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.larvicida_larvicida_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: registro_de_campo; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.registro_de_campo (
    registro_de_campo_id integer NOT NULL,
    imovel_numero smallint NOT NULL,
    imovel_lado character varying(10) NOT NULL,
    imovel_categoria_da_localidade character varying(20) NOT NULL,
    imovel_tipo character varying(20) NOT NULL,
    imovel_status character varying(20) NOT NULL,
    imovel_complemento character varying(100),
    formulario_tipo character varying(50),
    li boolean,
    pe boolean,
    t boolean,
    df boolean,
    pve boolean,
    numero_da_amostra character varying(15),
    quantiade_tubitos smallint,
    observacao character varying(200),
    area_de_visita_id integer,
    agente_id integer,
    deposito_id integer,
    ciclo_id integer
);


ALTER TABLE public.registro_de_campo OWNER TO "user";

--
-- Name: registro_de_campo_arquivos; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.registro_de_campo_arquivos (
    registro_de_campo_arquivo_id integer CONSTRAINT registro_de_campo_arquivos_registro_de_campo_arquivo_i_not_null NOT NULL,
    registro_de_campo_id integer,
    arquivo_nome character varying(100)
);


ALTER TABLE public.registro_de_campo_arquivos OWNER TO "user";

--
-- Name: registro_de_campo_arquivos_registro_de_campo_arquivo_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.registro_de_campo_arquivos ALTER COLUMN registro_de_campo_arquivo_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.registro_de_campo_arquivos_registro_de_campo_arquivo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: registro_de_campo_registro_de_campo_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.registro_de_campo ALTER COLUMN registro_de_campo_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.registro_de_campo_registro_de_campo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: supervisor; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.supervisor (
    supervisor_id integer NOT NULL,
    usuario_id integer
);


ALTER TABLE public.supervisor OWNER TO "user";

--
-- Name: supervisor_supervisor_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.supervisor ALTER COLUMN supervisor_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.supervisor_supervisor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.usuario (
    usuario_id integer NOT NULL,
    nome_completo character varying(100) NOT NULL,
    cpf character varying(11) NOT NULL,
    rg character varying(10),
    data_nascimento date NOT NULL,
    email character varying(200) NOT NULL,
    telefone_ddd smallint NOT NULL,
    telefone_numero character varying(9) NOT NULL,
    estado character varying(3) NOT NULL,
    municipio character varying(50) NOT NULL,
    bairro character varying(50) NOT NULL,
    logradouro character varying(50) NOT NULL,
    numero smallint NOT NULL,
    registro_do_servidor character varying(50) NOT NULL,
    cargo character varying(50) NOT NULL,
    situacao_atual boolean NOT NULL,
    data_de_admissao date NOT NULL,
    senha character varying(50) NOT NULL,
    nivel_de_acesso character varying(50) NOT NULL
);


ALTER TABLE public.usuario OWNER TO "user";

--
-- Name: usuario_usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.usuario ALTER COLUMN usuario_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.usuario_usuario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: adulticida; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.adulticida (adulticida_id, registro_de_campo_id, tipo, quantidade) FROM stdin;
1	6	Adulticida de Borrifação Residual (Piretróide)	20
2	13	Adulticida de Borrifação Residual (Piretróide)	25
3	26	Adulticida de Borrifação Residual (Piretróide)	15
4	42	Adulticida de Borrifação Residual (Piretróide)	30
5	72	Adulticida de Borrifação Residual (Piretróide)	20
6	85	Adulticida de Borrifação Residual (Piretróide)	22
7	93	Adulticida de Borrifação Residual (Piretróide)	35
8	101	Adulticida de Borrifação Residual (Piretróide)	18
9	121	Adulticida de Borrifação Residual (Piretróide)	25
10	134	Adulticida de Borrifação Residual (Piretróide)	20
11	138	Adulticida de Borrifação Residual (Piretróide)	30
12	160	Adulticida de Borrifação Residual (Piretróide)	15
\.


--
-- Data for Name: agente; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.agente (agente_id, usuario_id) FROM stdin;
1	1
2	2
3	3
4	4
5	5
6	7
7	8
8	9
9	11
10	12
11	13
12	14
13	15
14	16
15	17
16	18
17	20
\.


--
-- Data for Name: agente_area_de_visita; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.agente_area_de_visita (agente_area_de_visita_id, agente_id, area_de_visita_id) FROM stdin;
1	1	1
2	11	1
3	3	2
4	12	2
5	2	2
6	4	3
7	13	3
8	5	4
9	14	4
10	7	5
11	15	5
12	8	6
13	16	6
14	9	7
15	15	7
16	11	8
17	16	8
18	12	9
19	1	9
20	13	10
21	16	10
22	1	5
23	7	2
24	9	4
25	15	6
26	16	7
\.


--
-- Data for Name: area_de_visita; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.area_de_visita (area_de_visita_id, supervisor_id, cep, setor, numero_quarteirao, estado, municipio, bairro, status, logadouro) FROM stdin;
1	1	57035-180	Setor Ponta Verde 01	15	AL	Maceió	Ponta Verde	Visitado	Avenida Álvaro Otacílio
2	1	57036-000	Setor Jatiúca 03	42	AL	Maceió	Jatiúca	Visitado	Avenida Doutor Antônio Gomes de Barros
3	2	57030-170	Setor Pajuçara 02	28	AL	Maceió	Pajuçara	Visitado	Rua Jangadeiros Alagoanos
4	2	57051-500	Setor Farol 05	112	AL	Maceió	Farol	Visitado	Avenida Fernandes Lima
5	3	57036-540	Setor Cruz das Almas 01	67	AL	Maceió	Cruz das Almas	Visitado	Avenida Brigadeiro Eduardo Gomes de Brito
6	3	57040-000	Setor Jacintinho 11	153	AL	Maceió	Jacintinho	Não Visitado	Rua Cleto Campelo
7	4	57085-000	Setor Benedito Bentes 24	201	AL	Maceió	Benedito Bentes	Visitado	Avenida Cachoeira do Meirim
8	4	57046-140	Setor Serraria 08	95	AL	Maceió	Serraria	Não Visitado	Avenida Menino Marcelo
9	2	57052-480	Setor Gruta 04	78	AL	Maceió	Gruta de Lourdes	Visitado	Rua Artur Vital da Silva
10	1	57035-160	Setor Mangabeiras 02	33	AL	Maceió	Mangabeiras	Visitado	Rua Professora Maria Esther da Costa Barros
\.


--
-- Data for Name: arquivos_denuncia; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.arquivos_denuncia (arquivo_denuncia_id, arquivo_nome, denuncia_id) FROM stdin;
1	denuncia_1_foto_vasos_01.jpg	1
2	denuncia_1_foto_vasos_02.png	1
3	denuncia_2_foto_terreno_geral.jpg	2
4	denuncia_2_detalhe_pneus.jpg	2
5	denuncia_2_video_local.mp4	2
6	denuncia_3_foto_caixa_dagua.jpg	3
7	denuncia_4_foto_patio.jpg	4
8	denuncia_4_foto_baldes.jpg	4
\.


--
-- Data for Name: artigo; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.artigo (artigo_id, supervisor_id, link_artigo, titulo, data_criacao, descricao, imagem_nome) FROM stdin;
1	1	https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/d/dengue	Dengue: O que é, causas e tratamento	2025-02-15	Página oficial do Ministério da Saúde com informações completas sobre a Dengue, incluindo sintomas, prevenção e manejo clínico da doença.	infografico-sintomas-dengue.jpg
2	2	https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/z/zika-virus	Zika Vírus: Informações Gerais	2025-02-28	Guia do Ministério da Saúde sobre o Zika Vírus, abordando a transmissão, sintomas, diagnóstico e a relação com a microcefalia.	mosquito-aedes-aegypti-zika.png
3	3	https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/c/chikungunya	Chikungunya: Sintomas e Prevenção	2025-03-10	Detalhes sobre a febre Chikungunya, com foco nos sintomas característicos de dores nas articulações, tratamento e formas de prevenção.	articulacoes-afetadas-chikungunya.jpg
4	4	https://www.paho.org/pt/topicos/dengue	Dengue (OPAS/OMS)	2025-04-01	Portal da Organização Pan-Americana da Saúde com dados, estratégias de controle e informações técnicas sobre a dengue nas Américas.	mapa-americas-casos-dengue.png
5	1	https://www.bio.fiocruz.br/index.php/br/dengue-zika-e-chikungunya-sintomas-e-prevencao	Diferenças entre Dengue, Zika e Chikungunya	2025-05-20	Artigo da Fiocruz que ajuda a diferenciar os sintomas das três principais arboviroses transmitidas pelo Aedes aegypti.	tabela-comparativa-dengue-zika-chikungunya.jpg
6	2	https://www.gov.br/saude/pt-br/assuntos/combate-ao-aedes	Combate ao Aedes aegypti	2025-06-18	Página central do Ministério da Saúde com todas as campanhas, materiais e estratégias para a eliminação dos focos do mosquito transmissor.	agente-de-saude-visitando-casa.jpg
7	3	https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/aedes-aegypti/monitoramento-das-arboviroses	Monitoramento de Arboviroses no Brasil	2025-07-25	Painel de dados interativo do Ministério da Saúde com números atualizados de casos de dengue, zika e chikungunya por região.	grafico-monitoramento-arboviroses.png
8	4	https://agenciabrasil.ebc.com.br/saude/noticia/2024-02/saiba-diferenciar-os-sintomas-de-dengue-zika-e-chikungunya	Saiba diferenciar os sintomas (Agência Brasil)	2025-08-14	Reportagem que explica de forma clara e visual as principais diferenças entre os sintomas de dengue, zika e chikungunya.	medico-examinando-paciente.jpg
9	1	https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/a/aedes-aegypti/boletins-epidemiologicos	Boletins Epidemiológicos de Arboviroses	2025-09-30	Acesso à página com os boletins epidemiológicos oficiais, com análises técnicas da situação das arboviroses no território nacional.	capa-boletim-epidemiologico.png
10	2	https://www.gov.br/saude/pt-br/assuntos/protocolos-clinicos-e-diretrizes-terapeuticas-pcdt/arquivos/2024/portal-dengue-manejo-adulto-crianca-fluxo-2024.pdf	Protocolo de Manejo Clínico da Dengue (PDF)	2025-10-05	Documento técnico oficial (2024) do Ministério da Saúde para profissionais, detalhando o fluxo de atendimento e manejo de pacientes.	fluxograma-atendimento-medico.jpg
\.


--
-- Data for Name: ciclo_area_de_visita; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.ciclo_area_de_visita (ciclo_area_de_visita_id, ciclo_id, area_de_visita_id) FROM stdin;
1	1	1
2	1	2
3	1	3
4	1	4
5	1	5
6	1	6
7	1	7
8	1	8
9	1	9
10	1	10
11	2	1
12	2	2
13	2	3
14	2	4
15	2	5
16	2	6
17	2	7
18	2	8
19	2	9
20	2	10
21	3	1
22	3	2
23	3	3
24	3	4
25	3	5
26	3	6
27	3	7
28	3	8
29	3	9
30	3	10
31	4	1
32	4	2
33	4	3
34	4	4
35	4	5
36	4	6
37	4	7
38	4	8
39	4	9
40	4	10
41	5	1
42	5	2
43	5	3
44	5	4
45	5	5
46	5	6
47	5	7
48	5	8
49	5	9
50	5	10
51	6	1
52	6	2
53	6	3
54	6	4
55	6	5
56	6	6
57	6	7
58	6	8
59	6	9
60	6	10
\.


--
-- Data for Name: ciclos; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.ciclos (ciclo_id, supervisor_id, ano_de_criacao, encerramento, ativo, ciclo) FROM stdin;
1	3	2024-01-16	2024-06-16	f	1
2	1	2024-06-18	2024-12-18	f	2
3	2	2025-01-18	2025-06-18	f	1
4	3	2025-06-19	\N	t	2
\.


--
-- Data for Name: denuncia; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.denuncia (denuncia_id, supervisor_id, deposito_id, agente_responsavel_id, rua_avenida, numero, bairro, tipo_imovel, status, endereco_complemento, data_denuncia, hora_denuncia, observacoes) FROM stdin;
1	1	1	2	Rua Engenheiro Mário de Gusmão	980	Ponta Verde	Condomínio	Concluída	Bloco A, perto da área da piscina	2025-09-18	10:30:00	Vários vasos de planta com água parada na área comum.
2	2	2	\N	Avenida Doutor Júlio Marques Luz	1210	Jatiúca	Terreno Baldio	Em Análise	Ao lado de uma oficina mecânica.	2025-09-18	14:00:00	Acúmulo de lixo e pneus velhos com água da chuva.
3	3	3	4	Rua Professor Guedes de Miranda	455	Farol	Residência	Concluída	Casa de esquina com muro branco e portão azul.	2025-09-19	09:15:00	Caixa d'água destampada no quintal, visível da rua.
4	1	4	\N	Rua Desportista Humberto Guimarães	789	Ponta Verde	Comércio	Pendente	Restaurante	2025-09-19	16:45:00	Garrafas e baldes acumulados no pátio traseiro do estabelecimento.
5	2	5	1	Rua Buarque de Macedo	550	Centro	Imóvel abandonado	Concluída	Prédio antigo com janelas quebradas.	2025-09-20	08:00:00	Calhas entupidas e muito lixo no interior do imóvel.
\.


--
-- Data for Name: depositos; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.depositos (deposito_id, a1, a2, b, c, d1, d2, e) FROM stdin;
1	0	0	2	0	0	0	0
2	0	0	0	0	0	0	0
3	0	0	0	0	0	0	0
4	0	0	0	1	0	0	0
5	0	0	0	0	0	0	0
6	1	0	0	0	0	0	0
7	0	0	0	0	0	0	0
8	0	0	0	0	3	2	0
9	0	0	0	0	0	0	0
10	0	1	0	0	0	0	0
11	0	0	0	0	0	0	0
12	0	0	0	0	0	0	0
13	0	0	0	0	8	5	0
14	0	0	0	0	0	0	0
15	0	0	0	0	0	0	0
16	0	0	2	0	0	1	0
17	0	0	0	0	0	0	0
18	0	0	0	0	0	4	0
19	0	0	0	0	0	0	0
20	0	0	0	0	0	0	0
21	0	0	0	0	0	0	0
22	0	0	0	0	0	0	0
23	0	0	1	0	0	0	0
24	0	0	0	0	0	0	0
25	0	0	0	0	0	0	0
26	0	0	2	0	0	3	0
27	0	0	0	0	0	0	0
28	0	0	0	0	0	0	0
29	0	0	0	0	0	0	0
30	0	0	0	0	0	0	0
31	0	0	3	0	0	2	0
32	0	0	0	0	0	0	0
33	0	0	0	2	0	0	0
34	0	0	0	0	0	0	0
35	0	0	0	0	0	5	0
36	0	0	0	0	0	0	0
37	0	0	0	0	0	0	1
38	0	0	0	0	0	0	0
39	0	0	0	0	0	0	0
40	0	1	0	0	0	0	0
41	0	0	0	0	0	0	0
42	0	0	1	0	0	2	0
43	0	0	0	0	0	0	0
44	0	0	0	0	0	0	0
45	0	0	0	0	0	0	0
46	0	0	0	0	0	0	0
47	0	0	0	0	0	0	0
48	0	0	0	0	0	0	0
49	0	0	0	0	0	0	0
50	0	0	0	0	0	0	0
51	0	0	2	0	0	0	0
52	0	0	0	0	0	0	0
53	0	0	0	0	0	0	0
54	0	0	0	0	0	0	0
55	0	0	0	0	0	0	0
56	0	0	0	0	0	0	0
57	0	0	0	0	0	0	0
58	0	0	0	0	0	0	0
59	0	0	0	0	0	0	0
60	0	0	0	0	0	0	0
61	0	0	0	0	0	0	0
62	0	0	0	0	0	0	0
63	0	0	0	0	0	0	0
64	0	0	0	0	0	0	0
65	0	0	0	0	0	0	0
66	0	0	0	0	1	0	0
67	0	1	0	0	0	0	0
68	0	0	0	0	0	0	0
69	0	0	0	0	0	0	0
70	0	0	0	0	0	0	0
71	0	0	0	0	0	0	0
72	0	0	0	0	0	8	0
73	0	0	0	0	0	0	0
74	0	0	0	0	0	0	0
75	0	0	0	0	0	10	0
76	0	0	0	0	0	0	0
77	0	0	0	0	0	0	0
78	0	0	0	0	0	0	0
79	0	0	0	0	0	0	0
80	0	0	0	0	0	0	0
81	0	0	0	0	0	0	0
82	0	0	0	0	0	0	0
83	0	0	0	0	0	0	0
84	0	0	0	0	0	0	0
85	0	1	0	0	0	0	0
86	0	0	0	0	0	0	0
87	0	0	0	0	0	0	0
88	0	0	0	0	0	0	0
89	0	0	0	0	0	0	0
90	0	0	0	0	0	0	0
91	0	0	0	0	0	0	0
92	0	0	0	0	0	0	0
93	0	0	0	0	0	4	0
94	0	0	0	0	0	0	0
95	0	0	0	0	0	0	0
96	0	0	0	0	0	0	0
97	0	0	0	0	1	0	0
98	0	0	0	0	0	0	0
99	0	0	0	0	0	0	0
100	0	0	0	0	0	0	0
101	0	0	3	0	0	2	0
102	0	0	0	0	0	0	0
103	0	0	0	0	0	0	0
104	0	0	0	0	0	0	0
105	0	0	0	0	0	0	0
106	0	0	1	0	0	0	0
107	0	0	0	0	0	0	0
108	0	0	1	0	0	1	0
109	0	0	0	0	0	0	0
110	0	0	0	0	0	0	0
111	0	0	0	0	0	0	0
112	0	0	0	0	0	0	0
113	0	0	0	1	0	0	0
114	0	0	1	0	0	0	0
115	0	0	0	0	0	0	0
116	0	0	0	0	0	0	0
117	0	0	0	0	0	0	0
118	0	0	0	0	0	0	0
119	0	0	0	0	0	0	0
120	0	0	0	0	0	0	0
121	0	0	0	1	0	0	0
122	0	0	0	0	0	0	0
123	0	0	0	0	0	0	0
124	0	0	0	0	0	0	0
125	0	0	0	0	0	0	0
126	0	0	0	0	0	0	0
127	0	0	0	0	0	0	0
128	0	0	0	0	0	0	0
129	0	0	0	0	0	0	0
130	0	0	1	0	0	0	0
131	0	0	0	0	0	0	0
132	0	0	0	0	0	0	0
133	0	0	0	0	0	0	0
134	0	0	0	0	1	0	0
135	0	0	0	0	0	0	0
136	0	0	0	0	0	0	0
137	0	0	0	0	0	0	0
138	0	0	0	0	0	5	0
139	0	0	0	0	0	0	0
140	0	0	0	0	0	0	0
141	0	0	0	0	0	0	0
142	0	0	0	0	0	0	0
143	0	0	0	0	0	0	0
144	0	0	0	0	0	0	0
145	0	0	1	0	0	0	0
146	0	0	0	0	0	0	0
147	0	0	0	0	0	0	0
148	0	0	0	0	0	0	0
149	0	1	0	0	0	0	0
150	0	0	0	0	0	0	0
151	0	0	0	0	0	0	0
152	0	0	0	0	0	0	0
153	0	0	0	0	0	0	0
154	0	0	0	0	0	0	0
155	0	0	0	0	0	0	0
156	0	0	0	0	0	0	0
157	0	0	0	0	0	0	0
158	0	0	0	0	0	0	0
159	0	0	0	0	0	0	0
160	0	0	0	0	0	0	0
161	0	0	0	0	0	0	0
162	0	0	0	0	0	0	0
163	0	0	0	0	0	0	0
164	0	0	2	0	0	1	0
165	0	0	0	0	0	0	0
166	0	0	0	0	0	0	0
167	0	0	0	0	0	0	0
168	0	0	0	0	0	0	0
169	0	0	0	0	0	0	0
170	0	0	0	0	0	0	0
171	0	0	0	0	0	0	0
172	0	0	0	0	0	0	0
173	0	0	0	0	0	0	0
174	0	0	0	0	0	0	0
175	0	0	0	0	0	0	0
176	0	0	0	0	0	0	0
177	0	0	0	0	0	0	0
178	0	0	0	0	0	0	0
179	0	0	0	0	0	0	0
180	0	0	0	0	0	0	0
181	0	0	0	0	0	0	0
182	0	0	0	0	0	0	0
183	0	0	0	0	0	0	0
184	0	0	0	0	0	0	0
185	0	0	0	0	0	0	0
186	0	0	0	0	0	0	0
187	0	0	0	0	0	0	0
188	0	0	0	0	0	0	0
189	0	0	0	0	0	0	0
190	0	0	0	0	0	0	0
191	0	0	0	0	0	0	0
192	0	0	0	0	0	0	0
193	0	0	0	0	0	0	0
194	0	0	0	0	0	0	0
195	0	0	0	0	0	0	0
196	0	0	0	0	0	0	0
197	0	0	0	0	0	0	0
198	0	0	0	0	0	0	0
199	0	0	0	0	0	0	0
200	0	0	0	0	0	0	0
201	0	0	0	0	0	0	0
202	0	0	0	0	0	0	0
203	0	0	0	0	0	0	0
204	0	0	0	0	0	0	0
205	0	0	0	0	0	0	0
206	0	0	0	0	0	0	0
207	0	0	0	0	0	0	0
208	0	0	0	0	0	0	0
209	0	0	0	0	0	0	0
210	0	0	0	0	0	0	0
211	0	0	0	0	0	0	0
212	0	0	0	0	0	0	0
213	0	0	0	0	0	0	0
214	0	0	0	0	0	0	0
215	0	0	0	0	0	0	0
216	0	0	0	0	0	0	0
217	0	0	0	0	0	0	0
218	0	0	0	0	0	0	0
219	0	0	0	0	0	0	0
220	0	0	0	0	0	0	0
221	0	0	0	0	0	0	0
222	0	0	0	0	0	0	0
223	0	0	0	0	0	0	0
224	0	0	0	0	0	0	0
225	0	0	0	0	0	0	0
226	0	0	0	0	0	0	0
227	0	0	0	0	0	0	0
228	0	0	0	0	0	0	0
229	0	0	0	0	0	0	0
230	0	0	0	0	0	0	0
231	0	0	0	0	0	0	0
232	0	0	0	0	0	0	0
233	0	0	0	0	0	0	0
234	0	0	0	0	0	0	0
235	0	0	0	0	0	0	0
236	0	0	0	0	0	0	0
237	0	0	0	0	0	0	0
238	0	0	0	0	0	0	0
239	0	0	0	0	0	0	0
240	0	0	0	0	0	0	0
\.


--
-- Data for Name: larvicida; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.larvicida (larvicida_id, registro_de_campo_id, tipo, forma, quantidade) FROM stdin;
1	1	Pyriproxyfen	Granulado	2
2	1	Bti (Bacillus thuringiensis israelensis)	Tablete	1
3	4	Bti (Bacillus thuringiensis israelensis)	Tablete	2
4	6	Pyriproxyfen	Granulado	5
5	8	Spinosad	Tablete	1
6	10	Methoprene	Líquido	10
7	13	Bti (Bacillus thuringiensis israelensis)	Granulado	15
8	16	Pyriproxyfen	Granulado	3
9	18	Spinosad	Tablete	1
10	20	Methoprene	Líquido	20
11	23	Bti (Bacillus thuringiensis israelensis)	Tablete	2
12	26	Pyriproxyfen	Granulado	4
13	31	Pyriproxyfen	Granulado	2
14	33	Bti (Bacillus thuringiensis israelensis)	Granulado	10
15	40	Bti (Bacillus thuringiensis israelensis)	Tablete	1
16	42	Pyriproxyfen	Granulado	3
17	51	Spinosad	Tablete	1
18	67	Bti (Bacillus thuringiensis israelensis)	Tablete	1
19	72	Pyriproxyfen	Granulado	8
20	75	Bti (Bacillus thuringiensis israelensis)	Granulado	12
21	85	Pyriproxyfen	Granulado	2
22	93	Bti (Bacillus thuringiensis israelensis)	Granulado	10
23	101	Spinosad	Tablete	1
24	108	Pyriproxyfen	Granulado	3
25	113	Methoprene	Líquido	15
26	121	Bti (Bacillus thuringiensis israelensis)	Tablete	2
27	134	Pyriproxyfen	Granulado	4
28	138	Spinosad	Tablete	1
29	160	Pyriproxyfen	Granulado	2
\.


--
-- Data for Name: registro_de_campo; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.registro_de_campo (registro_de_campo_id, imovel_numero, imovel_lado, imovel_categoria_da_localidade, imovel_tipo, imovel_status, imovel_complemento, formulario_tipo, li, pe, t, df, pve, numero_da_amostra, quantiade_tubitos, observacao, area_de_visita_id, agente_id, deposito_id, ciclo_id) FROM stdin;
1	101	Ímpar	Urbana	Residência	Inspecionado	Casa A	Dengue	f	f	t	t	f	\N	\N	Foco encontrado em prato de planta.	1	1	1	1
2	102	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Nenhum foco encontrado.	1	11	2	1
3	103	Ímpar	Urbana	Comércio	Fechados	Loja 3	\N	f	f	f	f	f	\N	\N	Estabelecimento fechado.	1	1	3	1
4	104	Par	Urbana	Residência	Inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Morador orientado.	1	11	4	1
5	201	Ímpar	Urbana	Comércio	Inspecionado	Loja 02	Dengue	f	t	f	f	f	\N	\N	Nenhum foco encontrado.	2	2	5	1
6	202	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	t	t	f	\N	\N	Caixa d'água destampada.	2	3	6	1
7	203	Ímpar	Urbana	Residência	Recusados	\N	\N	f	f	f	f	f	\N	\N	Morador não permitiu a entrada.	2	7	7	1
8	204	Par	Urbana	Comércio	Inspecionado	Oficina	Chikungunya	f	t	f	f	f	\N	\N	Local inspecionado, sem larvas.	2	12	8	1
9	301	Ímpar	Urbana	Residência	Fechados	\N	\N	f	f	f	f	f	\N	\N	Morador ausente.	3	4	9	1
10	302	Par	Urbana	Residência	bloqueado	Apto 101	Dengue	t	f	t	t	t	A001	2	Amostra coletada de ralo e local tratado.	3	13	10	1
11	303	Ímpar	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Sem focos.	3	4	11	1
12	304	Par	Urbana	Comércio	Inspecionado	Borracharia	Dengue	f	t	f	f	f	\N	\N	Pneus armazenados corretamente.	3	13	12	1
13	401	Ímpar	Urbana	Terreno Baldio	bloqueado	\N	Zica	f	t	t	t	t	\N	\N	Limpeza e tratamento de focos em pneus.	4	5	13	1
14	402	Par	Urbana	Residência	Inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Nenhum foco encontrado.	4	9	14	1
15	403	Ímpar	Urbana	Comércio	Fechados	Supermercado	\N	f	f	f	f	f	\N	\N	Fechado para balanço.	4	14	15	1
16	404	Par	Urbana	Residência	Inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Ok.	4	5	16	1
17	501	Ímpar	Urbana	Residência	Inspecionado	\N	Dengue	t	f	f	t	f	A002	1	Coleta de amostra positiva.	5	1	17	1
18	502	Par	Urbana	Terreno Baldio	Inspecionado	Murado	Dengue	f	t	t	f	f	\N	\N	Tratamento com larvicida granulado.	5	7	18	1
19	503	Ímpar	Urbana	Residência	Recusados	\N	\N	f	f	f	f	f	\N	\N	Morador não permitiu a entrada.	5	15	19	1
20	504	Par	Urbana	Outros	Inspecionado	Posto de Saúde	Zica	f	t	f	f	f	\N	\N	Inspeção de rotina, sem focos.	5	15	20	1
21	601	Ímpar	Urbana	Residência	Inspecionado	Apto 202	Zica	f	f	f	f	f	\N	\N	Sem focos.	6	8	21	1
22	602	Par	Urbana	Residência	Fechados	\N	\N	f	f	f	f	f	\N	\N	Ninguém atendeu.	6	16	22	1
23	603	Ímpar	Urbana	Residência	Inspecionado	Casa com piscina	Dengue	f	f	t	t	f	\N	\N	Piscina tratada com larvicida.	6	15	23	1
24	604	Par	Urbana	Comércio	Fechados	\N	\N	f	f	f	f	f	\N	\N	Comércio fechado permanentemente.	6	16	24	1
25	701	Ímpar	Urbana	Comércio	Inspecionado	Restaurante	Chikungunya	f	t	f	f	f	\N	\N	Sem focos na área externa.	7	9	25	1
26	702	Par	Urbana	Residência	Inspecionado	Casa dos Fundos	Chikungunya	f	f	t	t	f	\N	\N	Foco em balde, tratado.	7	16	26	1
27	703	Ímpar	Urbana	Comércio	Fechados	Clínica	\N	f	f	f	f	f	\N	\N	Fechado, horário de almoço.	7	15	27	1
28	704	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Morador orientado sobre prevenção.	7	16	28	1
29	801	Ímpar	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ambiente limpo e sem depósitos.	8	11	29	1
30	802	Par	Urbana	Residência	Fechados	\N	\N	f	f	f	f	f	\N	\N	Cachorro bravo, morador ausente.	8	16	30	1
31	803	Ímpar	Urbana	Residência	bloqueado	Cond. Fechado	Chikungunya	f	f	t	t	t	\N	\N	Foco em área comum do condomínio.	8	11	31	1
32	804	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ok.	8	16	32	1
33	901	Ímpar	Urbana	Outros	Inspecionado	Escola	Dengue	f	t	f	f	f	\N	\N	Ok.	9	1	33	1
34	902	Par	Urbana	Residência	Fechados	\N	\N	f	f	f	f	f	\N	\N	Ninguém em casa.	9	12	34	1
35	903	Ímpar	Urbana	Terreno Baldio	Inspecionado	Aberto	Chikungunya	f	t	f	t	f	\N	\N	Encontrado lixo com água, eliminado mecanicamente.	9	1	35	1
36	904	Par	Urbana	Residência	Recusados	\N	\N	f	f	f	f	f	\N	\N	Morador informou que não recebe visitas.	9	12	36	1
37	1001	Ímpar	Urbana	Residência	Inspecionado	Bloco B Apto 1002	Zica	f	f	f	t	f	\N	\N	Foco em bromélia na varanda, eliminado.	10	13	37	1
38	1002	Par	Urbana	Residência	Fechados	\N	\N	f	f	f	f	f	\N	\N	Ninguém atendeu.	10	16	38	1
39	1003	Ímpar	Urbana	Residência	Recusados	\N	\N	f	f	f	f	f	\N	\N	Recusa.	10	13	39	1
40	1004	Par	Urbana	Terreno Baldio	Fechados	\N	\N	f	f	f	f	f	\N	\N	Portão trancado.	10	16	40	1
41	101	Ímpar	Urbana	Residência	Inspecionado	Casa A	Dengue	f	f	f	f	f	\N	\N	Revisita. Local limpo.	1	1	41	2
42	102	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	t	t	f	\N	\N	Novo foco em garrafa no quintal.	1	11	42	2
43	103	Ímpar	Urbana	Comércio	Inspecionado	Loja 3	Dengue	f	t	f	f	f	\N	\N	Estabelecimento aberto, tudo ok.	1	1	43	2
44	104	Par	Urbana	Residência	Inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Calha limpa, sem água acumulada.	1	11	44	2
45	201	Ímpar	Urbana	Comércio	Inspecionado	Loja 02	Dengue	f	t	f	f	f	\N	\N	Segunda visita, tudo ok.	2	2	45	2
46	202	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Caixa d'água agora está tampada.	2	3	46	2
47	203	Ímpar	Urbana	Residência	Inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Morador permitiu entrada. Sem focos.	2	7	47	2
48	204	Par	Urbana	Comércio	Inspecionado	Oficina	Dengue	f	t	f	f	f	\N	\N	Inspeção de rotina, ok.	2	12	48	2
49	301	Ímpar	Urbana	Residência	Inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Morador encontrado. Casa inspecionada.	3	4	49	2
50	302	Par	Urbana	Residência	Inspecionado	Apto 101	Zica	f	f	f	f	f	\N	\N	Revisita, sem necessidade de nova amostra.	3	13	50	2
51	303	Ímpar	Urbana	Residência	Inspecionado	\N	Dengue	f	f	t	t	f	\N	\N	Pequeno foco em vaso de planta. Tratado.	3	4	51	2
52	304	Par	Urbana	Comércio	Inspecionado	Borracharia	Dengue	f	t	f	f	f	\N	\N	Pneus permanecem secos e cobertos.	3	13	52	2
53	401	Ímpar	Urbana	Terreno Baldio	Inspecionado	\N	Zica	f	t	f	f	f	\N	\N	Terreno permanece limpo.	4	5	53	2
54	402	Par	Urbana	Residência	Inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Tudo ok.	4	9	54	2
55	403	Ímpar	Urbana	Comércio	Inspecionado	Supermercado	Dengue	f	t	f	f	f	\N	\N	Sem alterações.	4	14	55	2
56	404	Par	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Morador em viagem.	4	5	56	2
57	501	Ímpar	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Revisita de acompanhamento, sem larvas.	5	1	57	2
58	502	Par	Urbana	Terreno Baldio	Inspecionado	Murado	Dengue	f	t	f	f	f	\N	\N	Sem novos focos.	5	7	58	2
59	503	Ímpar	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Morador continua recusando a visita.	5	15	59	2
60	504	Par	Urbana	Outros	Inspecionado	Posto de Saúde	Zica	f	t	f	f	f	\N	\N	Inspeção de rotina, tudo ok.	5	15	60	2
61	601	Ímpar	Urbana	Residência	Inspecionado	Apto 202	Zica	f	f	f	f	f	\N	\N	Ok.	6	8	61	2
62	602	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Sem alterações.	6	16	62	2
63	603	Ímpar	Urbana	Residência	bloqueado	\N	Dengue	f	f	t	t	t	\N	\N	Piscina com água parada. Tratada.	6	15	63	2
64	604	Par	Urbana	Comércio	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Comércio fechado permanentemente.	6	16	64	2
65	701	Ímpar	Urbana	Comércio	Inspecionado	Restaurante	Chikungunya	f	t	f	f	f	\N	\N	Revisita, local limpo.	7	9	65	2
66	702	Par	Urbana	Residência	Inspecionado	Casa dos Fundos	Chikungunya	f	f	f	f	f	\N	\N	Sem novos focos.	7	16	66	2
67	703	Ímpar	Urbana	Comércio	Inspecionado	Clínica	Dengue	f	t	t	t	f	\N	\N	Foco em ralo externo. Tratado.	7	15	67	2
68	704	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ok.	7	16	68	2
69	801	Ímpar	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Ninguém atendeu.	8	11	69	2
70	802	Par	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Ninguém em casa.	8	16	70	2
71	803	Ímpar	Urbana	Residência	Inspecionado	Cond. Fechado	Chikungunya	f	f	f	f	f	\N	\N	Área comum permanece limpa.	8	11	71	2
72	804	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	t	t	f	\N	\N	Lixo acumulado no quintal com água.	8	16	72	2
73	901	Ímpar	Urbana	Outros	Inspecionado	Escola	Dengue	f	t	f	f	f	\N	\N	Inspeção de rotina, sem focos.	9	1	73	2
74	902	Par	Urbana	Residência	Inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Ok.	9	12	74	2
75	903	Ímpar	Urbana	Terreno Baldio	Inspecionado	Aberto	Chikungunya	f	t	t	t	f	\N	\N	Novo acúmulo de lixo com água.	9	1	75	2
76	904	Par	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Recusa persistente.	9	12	76	2
77	1001	Ímpar	Urbana	Residência	Inspecionado	Bloco B Apto 1002	Zica	f	f	f	f	f	\N	\N	Sem novos focos.	10	13	77	2
78	1002	Par	Urbana	Residência	Inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Morador encontrado. Casa inspecionada.	10	16	78	2
79	1003	Ímpar	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Recusa.	10	13	79	2
80	1004	Par	Urbana	Terreno Baldio	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Acesso bloqueado.	10	16	80	2
81	101	Ímpar	Urbana	Residência	Inspecionado	Casa A	Dengue	f	f	f	f	f	\N	\N	Terceira visita de rotina. Sem alterações.	1	1	81	3
82	102	Par	Urbana	Residência	Inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Revisita. Local permanece limpo.	1	11	82	3
83	103	Ímpar	Urbana	Comércio	Inspecionado	Loja 3	Dengue	f	t	f	f	f	\N	\N	Estabelecimento aberto. Inspecionado, ok.	1	1	83	3
84	104	Par	Urbana	Residência	Inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Tudo certo.	1	11	84	3
85	201	Ímpar	Urbana	Comércio	inspecionado	Loja 02	Dengue	f	t	t	t	f	\N	\N	Pequeno foco em ralo dos fundos.	2	2	85	3
86	202	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Tudo ok.	2	3	86	3
87	203	Ímpar	Urbana	Residência	inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Sem alterações.	2	7	87	3
88	204	Par	Urbana	Comércio	inspecionado	Oficina	Chikungunya	f	t	f	f	f	\N	\N	Terceira inspeção. Sem irregularidades.	2	12	88	3
89	301	Ímpar	Urbana	Residência	inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Sem focos.	3	4	89	3
90	302	Par	Urbana	Residência	inspecionado	Apto 101	Dengue	f	f	f	f	f	\N	\N	Tudo ok.	3	13	90	3
91	303	Ímpar	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Sem alterações.	3	4	91	3
92	304	Par	Urbana	Comércio	inspecionado	Borracharia	Dengue	f	t	f	f	f	\N	\N	Tudo certo.	3	13	92	3
93	401	Ímpar	Urbana	Terreno Baldio	bloqueado	\N	Zica	f	t	t	t	t	\N	\N	Novo descarte irregular de lixo.	4	5	93	3
94	402	Par	Urbana	Residência	inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Ok.	4	9	94	3
95	403	Ímpar	Urbana	Comércio	inspecionado	Supermercado	Dengue	f	t	t	t	f	\N	\N	Foco na área dos carrinhos.	4	14	95	3
96	404	Par	Urbana	Residência	inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Morador presente, tudo ok.	4	5	96	3
97	501	Ímpar	Urbana	Residência	inspecionado	\N	Dengue	f	f	t	t	f	\N	\N	Foco em pneu velho no quintal.	5	1	97	3
98	502	Par	Urbana	Terreno Baldio	inspecionado	Murado	Dengue	f	t	f	f	f	\N	\N	Ok.	5	7	98	3
99	503	Ímpar	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Recusa.	5	15	99	3
100	504	Par	Urbana	Outros	inspecionado	Posto de Saúde	Zica	f	t	f	f	f	\N	\N	Ok.	5	15	100	3
101	601	Ímpar	Urbana	Residência	inspecionado	Apto 202	Zica	f	f	t	t	f	\N	\N	Foco em vaso de planta na sacada.	6	8	101	3
102	602	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ok.	6	16	102	3
103	603	Ímpar	Urbana	Residência	inspecionado	Casa com piscina	Dengue	f	f	f	f	f	\N	\N	Ok.	6	15	103	3
104	604	Par	Urbana	Comércio	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Comércio fechado permanentemente.	6	16	104	3
105	701	Ímpar	Urbana	Comércio	inspecionado	Restaurante	Chikungunya	f	t	f	f	f	\N	\N	Ok.	7	9	105	3
106	702	Par	Urbana	Residência	inspecionado	\N	Chikungunya	f	f	t	t	f	\N	\N	Foco em tambor de água.	7	16	106	3
107	703	Ímpar	Urbana	Comércio	inspecionado	Clínica	Dengue	f	t	f	f	f	\N	\N	Ok.	7	15	107	3
108	704	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	t	f	f	\N	\N	Pequeno foco em brinquedo no quintal.	7	16	108	3
109	801	Ímpar	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ok.	8	11	109	3
110	802	Par	Urbana	Residência	inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Morador encontrado. Tudo certo.	8	16	110	3
111	803	Ímpar	Urbana	Residência	inspecionado	Cond. Fechado	Chikungunya	f	f	f	f	f	\N	\N	Ok.	8	11	111	3
112	804	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ok.	8	16	112	3
113	901	Ímpar	Urbana	Outros	bloqueado	Escola	Dengue	f	t	t	t	t	\N	\N	Início do período letivo, tratamento preventivo.	9	1	113	3
114	902	Par	Urbana	Residência	inspecionado	\N	Zica	f	f	t	t	f	\N	\N	Foco em ralo.	9	12	114	3
115	903	Ímpar	Urbana	Terreno Baldio	inspecionado	Aberto	Chikungunya	f	t	f	f	f	\N	\N	Terreno permanece limpo.	9	1	115	3
116	904	Par	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Recusa.	9	12	116	3
117	1001	Ímpar	Urbana	Residência	inspecionado	Bloco B Apto 1002	Zica	f	f	f	f	f	\N	\N	Ok.	10	13	117	3
118	1002	Par	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Ninguém atendeu novamente.	10	16	118	3
119	1003	Ímpar	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Recusa.	10	13	119	3
120	1004	Par	Urbana	Terreno Baldio	inspecionado	\N	Zica	f	t	f	f	f	\N	\N	Ok.	10	16	120	3
121	101	Ímpar	Urbana	Residência	bloqueado	Casa A	Zica	f	f	t	t	t	\N	\N	Visita de Zica, foco encontrado na calha.	1	1	121	4
122	102	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Local limpo.	1	11	122	4
123	103	Ímpar	Urbana	Comércio	inspecionado	Loja 3	Dengue	f	t	f	f	f	\N	\N	Tudo ok.	1	1	123	4
124	104	Par	Urbana	Residência	inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Ok.	1	11	124	4
125	201	Ímpar	Urbana	Comércio	inspecionado	Loja 02	Dengue	f	t	f	f	f	\N	\N	Ok.	2	2	125	4
126	202	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ok.	2	3	126	4
127	203	Ímpar	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Morador não estava em casa na 4a visita.	2	7	127	4
128	204	Par	Urbana	Comércio	inspecionado	Oficina	Chikungunya	f	t	f	f	f	\N	\N	Ok.	2	12	128	4
129	301	Ímpar	Urbana	Residência	inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Visita de rotina, ok.	3	4	129	4
130	302	Par	Urbana	Residência	inspecionado	Apto 101	Dengue	t	f	t	t	f	\N	\N	Foco recorrente em ralo. Tratado.	3	13	130	4
131	303	Ímpar	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ok.	3	4	131	4
132	304	Par	Urbana	Comércio	inspecionado	Borracharia	Dengue	f	t	f	f	f	\N	\N	Ok.	3	13	132	4
133	401	Ímpar	Urbana	Terreno Baldio	inspecionado	\N	Zica	f	t	f	f	f	\N	\N	Terreno limpo.	4	5	133	4
134	402	Par	Urbana	Residência	inspecionado	\N	Zica	f	f	t	t	f	\N	\N	Foco em pneu de enfeite no jardim.	4	9	134	4
135	403	Ímpar	Urbana	Comércio	inspecionado	Supermercado	Dengue	f	t	f	f	f	\N	\N	Ok.	4	14	135	4
136	404	Par	Urbana	Residência	inspecionado	\N	Chikungunya	f	f	f	f	f	\N	\N	Ok.	4	5	136	4
137	501	Ímpar	Urbana	Residência	inspecionado	\N	Dengue	f	f	t	t	f	\N	\N	Água acumulada em laje. Tratado.	5	1	137	4
138	502	Par	Urbana	Terreno Baldio	inspecionado	Murado	Dengue	f	t	t	f	f	\N	\N	Novo foco de lixo.	5	7	138	4
139	503	Ímpar	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Recusa.	5	15	139	4
140	504	Par	Urbana	Outros	inspecionado	Posto de Saúde	Zica	f	t	f	f	f	\N	\N	Ok.	5	15	140	4
141	601	Ímpar	Urbana	Residência	inspecionado	Apto 202	Zica	f	f	f	f	f	\N	\N	Ok.	6	8	141	4
142	602	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Ok.	6	16	142	4
143	603	Ímpar	Urbana	Residência	inspecionado	Casa com piscina	Dengue	f	f	f	f	f	\N	\N	Piscina ok.	6	15	143	4
144	604	Par	Urbana	Comércio	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Comércio fechado permanentemente.	6	16	144	4
145	701	Ímpar	Urbana	Comércio	bloqueado	Restaurante	Chikungunya	f	t	t	t	t	\N	\N	Foco em tambor nos fundos.	7	9	145	4
146	702	Par	Urbana	Residência	inspecionado	Casa dos Fundos	Chikungunya	f	f	f	f	f	\N	\N	Tudo ok.	7	16	146	4
147	703	Ímpar	Urbana	Comércio	inspecionado	Clínica	Dengue	f	t	f	f	f	\N	\N	Tudo ok.	7	15	147	4
148	704	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	t	t	f	\N	\N	Foco em caixa d'água no telhado.	7	16	148	4
149	801	Ímpar	Urbana	Residência	inspecionado	\N	Dengue	f	f	t	t	f	\N	\N	Foco em ralo.	8	11	149	4
150	802	Par	Urbana	Residência	inspecionado	\N	Zica	f	f	f	f	f	\N	\N	Morador presente, tudo certo.	8	16	150	4
151	803	Ímpar	Urbana	Residência	inspecionado	Cond. Fechado	Chikungunya	f	f	f	f	f	\N	\N	Tudo ok.	8	11	151	4
152	804	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Tudo ok.	8	16	152	4
153	901	Ímpar	Urbana	Outros	inspecionado	Escola	Dengue	f	t	f	f	f	\N	\N	Tudo ok.	9	1	153	4
154	902	Par	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Ninguém em casa.	9	12	154	4
155	903	Ímpar	Urbana	Terreno Baldio	inspecionado	Aberto	Chikungunya	f	t	t	t	f	\N	\N	Foco em entulho.	9	1	155	4
156	904	Par	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Recusa.	9	12	156	4
157	1001	Ímpar	Urbana	Residência	inspecionado	Bloco B Apto 1002	Zica	f	f	f	f	f	\N	\N	Tudo ok.	10	13	157	4
158	1002	Par	Urbana	Residência	inspecionado	\N	Dengue	f	f	f	f	f	\N	\N	Morador atendeu. Ok.	10	16	158	4
159	1003	Ímpar	Urbana	Residência	nao_inspecionado	\N	\N	f	f	f	f	f	\N	\N	Recusa.	10	13	159	4
160	1004	Par	Urbana	Terreno Baldio	inspecionado	\N	Zica	f	t	t	t	f	\N	\N	Água parada em lona. Tratado.	10	16	160	4
\.


--
-- Data for Name: registro_de_campo_arquivos; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.registro_de_campo_arquivos (registro_de_campo_arquivo_id, registro_de_campo_id, arquivo_nome) FROM stdin;
1	1	foco_prato_planta.jpg
2	3	comercio_fechado_ciclo1.jpg
3	4	calha_com_agua.jpg
4	6	caixa_dagua_destampada_antes.jpg
5	6	caixa_dagua_tampada_depois.jpg
6	7	prova_recusa_morador.mp4
7	8	pneu_com_foco.jpg
8	9	aviso_de_visita_deixado.jpg
9	13	terreno_antes_limpeza.jpg
10	13	terreno_depois_tratamento.jpg
11	19	recusa_ciclo1.jpg
12	24	comercio_fechado_permanente.jpg
13	30	morador_ausente_ciclo1.jpg
14	36	recusa_visita_904.jpg
15	38	ninguem_atendeu_1002.jpg
16	42	foco_garrafa_quintal_ciclo2.jpg
17	51	vaso_planta_tratado.jpg
18	56	morador_em_viagem_aviso.jpg
19	59	recusa_ciclo2.jpg
20	72	lixo_acumulado_quintal.jpg
21	75	novo_lixo_terreno_903.jpg
22	85	foco_ralo_externo.jpg
23	93	descarte_irregular_lixo.png
24	101	foco_vaso_sacada.jpg
25	104	comercio_fechado_ciclo3.jpg
26	108	foco_brinquedo_quintal.jpg
27	116	recusa_ciclo3.jpg
28	118	morador_ausente_ciclo3.jpg
29	121	calha_com_foco_ciclo4.jpg
30	127	morador_ausente_ciclo4.jpg
31	134	pneu_enfeite_jardim.jpg
32	138	novo_foco_lixo_terreno_502.jpg
33	139	recusa_ciclo4.jpg
34	145	foco_balde_ciclo5.jpg
35	144	recusa_ciclo5.jpg
36	155	comercio_fechado_ciclo5.jpg
37	142	recusa_ciclo5.jpg
38	133	recusa_ciclo5.jpg
39	143	recusa_final_ciclo6.jpg
40	142	comercio_fechado_ciclo6.jpg
41	111	recusa_final_ciclo6.jpg
42	123	recusa_final_ciclo6.jpg
\.


--
-- Data for Name: supervisor; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.supervisor (supervisor_id, usuario_id) FROM stdin;
1	2
2	6
3	10
4	19
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.usuario (usuario_id, nome_completo, cpf, rg, data_nascimento, email, telefone_ddd, telefone_numero, estado, municipio, bairro, logradouro, numero, registro_do_servidor, cargo, situacao_atual, data_de_admissao, senha, nivel_de_acesso) FROM stdin;
1	João da Silva	12345678901	1234567	1985-06-15	joao.silva@example.com	11	987654321	SP	São Paulo	Centro	Rua das Flores	123	RS-2025-001	Analista	t	2025-01-10	senhaSegura123	agente
2	Pedro Cavalcante	admin	212324567	1983-06-15	pedro.silva@example.com	11	987354321	SP	São Paulo	Centro	Rua das Flores	123	RS-2025-001	Analista	t	2025-01-10	123456	supervisor
3	Maria Oliveira Santos	23456789012	2345678	1990-03-22	maria.santos@example.com	21	912345678	RJ	Rio de Janeiro	Copacabana	Avenida Atlântica	1702	RS-2025-002	Gerente de Projetos	t	2024-05-20	outrasenha456	agente
4	Carlos Pereira Costa	34567890123	3456789	1988-11-01	carlos.costa@example.com	31	988776655	MG	Belo Horizonte	Savassi	Rua Fernandes Tourinho	500	RS-2025-003	Desenvolvedor Sênior	t	2023-08-15	senhaDev321	agente
5	Ana Clara Ferreira	45678901234	4567890	1995-09-10	ana.ferreira@example.com	41	977665544	PR	Curitiba	Batel	Avenida do Batel	1868	RS-2025-004	Analista de RH	f	2024-02-01	senhaRH987	agente
6	Pedro Rodrigues Alves	56789012345	5678901	1982-01-30	pedro.alves@example.com	51	966554433	RS	Porto Alegre	Moinhos de Vento	Rua Padre Chagas	415	RS-2025-005	Coordenador Financeiro	t	2022-11-25	senhaFin159	supervisor
7	Juliana Souza Lima	67890123456	6789012	1998-07-12	juliana.lima@example.com	61	955443322	DF	Brasília	Asa Sul	SCS Quadra 07	10	RS-2025-006	Estagiária	t	2025-07-01	senhaEstagio753	agente
8	Lucas Martins	78901234567	7890123	1992-04-25	lucas.martins@example.com	71	944332211	BA	Salvador	Barra	Avenida Oceânica	2400	RS-2025-007	Analista de Marketing	t	2023-03-18	senhaMkt357	agente
9	Fernanda Gonçalves	89012345678	8901234	1986-12-08	fernanda.g@example.com	81	933221100	PE	Recife	Boa Viagem	Avenida Boa Viagem	97	RS-2025-008	Designer Gráfico	t	2024-09-02	senhaDesign123	agente
10	Ricardo Almeida	90123456789	9012345	1979-05-19	ricardo.a@example.com	11	922110099	SP	São Paulo	Pinheiros	Rua dos Pinheiros	1000	RS-2025-009	Diretor de TI	t	2020-01-15	senhaDiretorTop	supervisor
11	Beatriz Rocha	01234567890	0123456	2000-02-28	beatriz.rocha@example.com	21	911009988	RJ	Niterói	Icaraí	Rua Gavião Peixoto	30	RS-2025-010	Assistente Administrativo	t	2025-06-11	senhaAdmin456	agente
12	Guilherme Barbosa	11223344556	1122334	1993-10-03	guilherme.b@example.com	31	988887777	MG	Contagem	Eldorado	Avenida João César de Oliveira	1275	RS-2025-011	Técnico de Suporte	t	2024-04-10	senhaSup555	agente
13	Larissa Azevedo	22334455667	2233445	1991-08-14	larissa.azevedo@example.com	48	977776666	SC	Florianópolis	Centro	Rua Felipe Schmidt	515	RS-2025-012	Analista de Negócios	t	2023-10-09	senhaNegocios333	agente
14	Rafael Ribeiro	33445566778	3344556	1987-03-29	rafael.r@example.com	85	966665555	CE	Fortaleza	Meireles	Avenida Beira Mar	4260	RS-2025-013	Desenvolvedor Pleno	t	2025-02-20	senhaPleno777	agente
15	Camila Nogueira	44556677889	4455667	1999-01-05	camila.n@example.com	92	955554444	AM	Manaus	Adrianópolis	Rua Teresina	151	RS-2025-014	Desenvolvedor Júnior	t	2025-08-12	senhaJunior888	agente
16	Felipe Monteiro	55667788990	5566778	1984-06-07	felipe.m@example.com	62	944443333	GO	Goiânia	Setor Bueno	Avenida T-10	100	RS-2025-015	Contador	t	2021-07-22	senhaContador999	agente
17	Vanessa Dias	66778899001	6677889	1996-09-21	vanessa.dias@example.com	27	933332222	ES	Vitória	Jardim da Penha	Rua da Lama	50	RS-2025-016	Assistente de Marketing	f	2024-01-30	senhaAssistMkt111	agente
18	Bruno Medeiros	77889900112	7788990	1990-11-18	bruno.m@example.com	11	922221111	SP	Guarulhos	Macedo	Avenida Paulo Faccini	1500	RS-2025-017	Analista de Logística	t	2023-05-16	senhaLog222	agente
19	Helena Justino	88990011223	8899001	1980-02-13	helena.j@example.com	41	911110000	PR	São José dos Pinhais	Centro	Rua XV de Novembro	210	RS-2025-018	Gerente de RH	t	2019-12-05	senhaGerenteRH321	supervisor
20	Igor Fernandes	99001122334	9900112	1997-07-07	igor.f@example.com	21	999998888	RJ	Duque de Caxias	Vila São Luís	Rua Genaro Lomba	15	RS-2025-019	Recrutador	t	2025-03-03	senhaRecrutador444	agente
21	Tiago Moreira	00112233445	0011223	1989-10-26	tiago.m@example.com	11	988887777	SP	Campinas	Cambuí	Rua Coronel Quirino	200	RS-2025-020	Arquiteto de Soluções	t	2022-09-01	senhaArquiteto555	agente
\.


--
-- Name: adulticida_adulticida_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.adulticida_adulticida_id_seq', 12, true);


--
-- Name: agente_agente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.agente_agente_id_seq', 17, true);


--
-- Name: agente_area_de_visita_agente_area_de_visita_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.agente_area_de_visita_agente_area_de_visita_id_seq', 26, true);


--
-- Name: area_de_visita_area_de_visita_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.area_de_visita_area_de_visita_id_seq', 10, true);


--
-- Name: arquivos_denuncia_arquivo_denuncia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.arquivos_denuncia_arquivo_denuncia_id_seq', 8, true);


--
-- Name: artigo_artigo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.artigo_artigo_id_seq', 10, true);


--
-- Name: ciclo_area_de_visita_ciclo_area_de_visita_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.ciclo_area_de_visita_ciclo_area_de_visita_id_seq', 60, true);


--
-- Name: ciclos_ciclo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.ciclos_ciclo_id_seq', 4, true);


--
-- Name: denuncia_denuncia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.denuncia_denuncia_id_seq', 5, true);


--
-- Name: depositos_deposito_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.depositos_deposito_id_seq', 240, true);


--
-- Name: larvicida_larvicida_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.larvicida_larvicida_id_seq', 29, true);


--
-- Name: registro_de_campo_arquivos_registro_de_campo_arquivo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.registro_de_campo_arquivos_registro_de_campo_arquivo_id_seq', 42, true);


--
-- Name: registro_de_campo_registro_de_campo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.registro_de_campo_registro_de_campo_id_seq', 160, true);


--
-- Name: supervisor_supervisor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.supervisor_supervisor_id_seq', 4, true);


--
-- Name: usuario_usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.usuario_usuario_id_seq', 21, true);


--
-- Name: adulticida adulticida_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.adulticida
    ADD CONSTRAINT adulticida_pkey PRIMARY KEY (adulticida_id);


--
-- Name: agente_area_de_visita agente_area_de_visita_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.agente_area_de_visita
    ADD CONSTRAINT agente_area_de_visita_pkey PRIMARY KEY (agente_area_de_visita_id);


--
-- Name: agente agente_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.agente
    ADD CONSTRAINT agente_pkey PRIMARY KEY (agente_id);


--
-- Name: area_de_visita area_de_visita_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.area_de_visita
    ADD CONSTRAINT area_de_visita_pkey PRIMARY KEY (area_de_visita_id);


--
-- Name: arquivos_denuncia arquivos_denuncia_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.arquivos_denuncia
    ADD CONSTRAINT arquivos_denuncia_pkey PRIMARY KEY (arquivo_denuncia_id);


--
-- Name: artigo artigo_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.artigo
    ADD CONSTRAINT artigo_pkey PRIMARY KEY (artigo_id);


--
-- Name: ciclo_area_de_visita ciclo_area_de_visita_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ciclo_area_de_visita
    ADD CONSTRAINT ciclo_area_de_visita_pkey PRIMARY KEY (ciclo_area_de_visita_id);


--
-- Name: ciclos ciclos_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ciclos
    ADD CONSTRAINT ciclos_pkey PRIMARY KEY (ciclo_id);


--
-- Name: denuncia denuncia_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.denuncia
    ADD CONSTRAINT denuncia_pkey PRIMARY KEY (denuncia_id);


--
-- Name: depositos depositos_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.depositos
    ADD CONSTRAINT depositos_pkey PRIMARY KEY (deposito_id);


--
-- Name: larvicida larvicida_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.larvicida
    ADD CONSTRAINT larvicida_pkey PRIMARY KEY (larvicida_id);


--
-- Name: registro_de_campo_arquivos registro_de_campo_arquivos_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo_arquivos
    ADD CONSTRAINT registro_de_campo_arquivos_pkey PRIMARY KEY (registro_de_campo_arquivo_id);


--
-- Name: registro_de_campo registro_de_campo_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT registro_de_campo_pkey PRIMARY KEY (registro_de_campo_id);


--
-- Name: supervisor supervisor_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisor_pkey PRIMARY KEY (supervisor_id);


--
-- Name: usuario usuario_cpf_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_cpf_key UNIQUE (cpf);


--
-- Name: usuario usuario_email_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_email_key UNIQUE (email);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (usuario_id);


--
-- Name: agente_area_de_visita fk_agente; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.agente_area_de_visita
    ADD CONSTRAINT fk_agente FOREIGN KEY (agente_id) REFERENCES public.agente(agente_id) ON DELETE CASCADE;


--
-- Name: registro_de_campo fk_agente; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT fk_agente FOREIGN KEY (agente_id) REFERENCES public.agente(agente_id) ON DELETE SET NULL;


--
-- Name: denuncia fk_agente_responsavel_id; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.denuncia
    ADD CONSTRAINT fk_agente_responsavel_id FOREIGN KEY (agente_responsavel_id) REFERENCES public.agente(agente_id) ON DELETE SET NULL;


--
-- Name: agente_area_de_visita fk_area_de_visita; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.agente_area_de_visita
    ADD CONSTRAINT fk_area_de_visita FOREIGN KEY (area_de_visita_id) REFERENCES public.area_de_visita(area_de_visita_id) ON DELETE CASCADE;


--
-- Name: registro_de_campo fk_area_de_visita; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT fk_area_de_visita FOREIGN KEY (area_de_visita_id) REFERENCES public.area_de_visita(area_de_visita_id) ON DELETE SET NULL;


--
-- Name: registro_de_campo fk_ciclo; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT fk_ciclo FOREIGN KEY (ciclo_id) REFERENCES public.ciclos(ciclo_id) ON DELETE CASCADE;


--
-- Name: arquivos_denuncia fk_denuncia; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.arquivos_denuncia
    ADD CONSTRAINT fk_denuncia FOREIGN KEY (denuncia_id) REFERENCES public.denuncia(denuncia_id) ON DELETE CASCADE;


--
-- Name: denuncia fk_deposito; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.denuncia
    ADD CONSTRAINT fk_deposito FOREIGN KEY (deposito_id) REFERENCES public.depositos(deposito_id) ON DELETE CASCADE;


--
-- Name: registro_de_campo fk_deposito; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT fk_deposito FOREIGN KEY (deposito_id) REFERENCES public.depositos(deposito_id) ON DELETE SET NULL;


--
-- Name: larvicida fk_registro_de_campo; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.larvicida
    ADD CONSTRAINT fk_registro_de_campo FOREIGN KEY (registro_de_campo_id) REFERENCES public.registro_de_campo(registro_de_campo_id) ON DELETE SET NULL;


--
-- Name: adulticida fk_registro_de_campo; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.adulticida
    ADD CONSTRAINT fk_registro_de_campo FOREIGN KEY (registro_de_campo_id) REFERENCES public.registro_de_campo(registro_de_campo_id) ON DELETE SET NULL;


--
-- Name: registro_de_campo_arquivos fk_registro_de_campo; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo_arquivos
    ADD CONSTRAINT fk_registro_de_campo FOREIGN KEY (registro_de_campo_id) REFERENCES public.registro_de_campo(registro_de_campo_id) ON DELETE SET NULL;


--
-- Name: ciclos fk_supervisor; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ciclos
    ADD CONSTRAINT fk_supervisor FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(supervisor_id) ON DELETE SET NULL;


--
-- Name: area_de_visita fk_supervisor; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.area_de_visita
    ADD CONSTRAINT fk_supervisor FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(supervisor_id) ON DELETE SET NULL;


--
-- Name: artigo fk_supervisor; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.artigo
    ADD CONSTRAINT fk_supervisor FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(supervisor_id) ON DELETE SET NULL;


--
-- Name: denuncia fk_supervisor; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.denuncia
    ADD CONSTRAINT fk_supervisor FOREIGN KEY (supervisor_id) REFERENCES public.supervisor(supervisor_id) ON DELETE SET NULL;


--
-- Name: agente fk_usuario; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.agente
    ADD CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) REFERENCES public.usuario(usuario_id) ON DELETE CASCADE;


--
-- Name: supervisor fk_usuario; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT fk_usuario FOREIGN KEY (usuario_id) REFERENCES public.usuario(usuario_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 3qEAE0GpvPeZ3AliDPoHJn2PHJmacy9g8pVfhKK5bUgxXGh0vyhJt0ObrkIzHqJ

