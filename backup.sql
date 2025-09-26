--
-- PostgreSQL database dump
--

\restrict IkDj5uW3JrHJnwDjIuCtMCL8Tjm1SeJacholQn5NnxZsqGzzpjW0S90rHOGE7IF

-- Dumped from database version 17.6 (Debian 17.6-1.pgdg13+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-1.pgdg13+1)

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
-- Name: arquivo_artigo; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.arquivo_artigo (
    arquivo_artigo_id integer NOT NULL,
    artigo_id integer,
    arquivo_nome character varying(100) NOT NULL
);


ALTER TABLE public.arquivo_artigo OWNER TO "user";

--
-- Name: arquivo_artigo_arquivo_artigo_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.arquivo_artigo ALTER COLUMN arquivo_artigo_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.arquivo_artigo_arquivo_artigo_id_seq
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
    nome_artigo_documento character varying(100),
    conteudo_artigo_digitado character varying(1000),
    titulo character varying(100) NOT NULL,
    descricao character varying(300) NOT NULL
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
    ativo boolean NOT NULL
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
    rua_avenida character varying(100) NOT NULL,
    numero smallint NOT NULL,
    bairro character varying(50) NOT NULL,
    tipo_imovel character varying(100) NOT NULL,
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
    registro_de_campo integer NOT NULL,
    rua character varying(200) NOT NULL,
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
    larvicida_id integer,
    adulticida_id integer,
    registro_de_campo_arquivo_id integer
);


ALTER TABLE public.registro_de_campo OWNER TO "user";

--
-- Name: registro_de_campo_arquivos; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.registro_de_campo_arquivos (
    registro_de_campo_arquivo_id integer NOT NULL,
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
-- Name: registro_de_campo_registro_de_campo_seq; Type: SEQUENCE; Schema: public; Owner: user
--

ALTER TABLE public.registro_de_campo ALTER COLUMN registro_de_campo ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.registro_de_campo_registro_de_campo_seq
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
    supervisor_criador_id integer,
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
    setor_de_atuacao character varying(50) NOT NULL,
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

COPY public.adulticida (adulticida_id, tipo, quantidade) FROM stdin;
1	Adulticida de Borrifação Residual (Piretróide)	20
2	Adulticida de Borrifação Residual (Piretróide)	15
3	Adulticida de Borrifação Residual (Piretróide)	25
4	Adulticida de Borrifação Residual (Piretróide)	10
5	Adulticida de Borrifação Residual (Piretróide)	30
6	Adulticida de Borrifação Residual (Piretróide)	20
7	Adulticida de Borrifação Residual (Piretróide)	18
8	Adulticida de Borrifação Residual (Piretróide)	22
9	Adulticida de Borrifação Residual (Piretróide)	35
10	Adulticida de Borrifação Residual (Piretróide)	15
11	Adulticida de Borrifação Residual (Piretróide)	20
12	Adulticida de Borrifação Residual (Piretróide)	25
13	Adulticida de Borrifação Residual (Piretróide)	12
14	Adulticida de Borrifação Residual (Piretróide)	28
15	Adulticida de Borrifação Residual (Piretróide)	20
16	Adulticida de Borrifação Residual (Piretróide)	15
17	Adulticida de Borrifação Residual (Piretróide)	30
18	Adulticida de Borrifação Residual (Piretróide)	24
19	Adulticida de Borrifação Residual (Piretróide)	16
20	Adulticida de Borrifação Residual (Piretróide)	20
21	Adulticida de Borrifação Residual (Piretróide)	25
22	Adulticida de Borrifação Residual (Piretróide)	10
23	Adulticida de Borrifação Residual (Piretróide)	40
24	Adulticida de Borrifação Residual (Piretróide)	22
25	Adulticida de Borrifação Residual (Piretróide)	18
26	Adulticida de Borrifação Residual (Piretróide)	20
27	Adulticida de Borrifação Residual (Piretróide)	30
28	Adulticida de Borrifação Residual (Piretróide)	15
29	Adulticida de Borrifação Residual (Piretróide)	25
30	Adulticida de Borrifação Residual (Piretróide)	20
\.


--
-- Data for Name: agente; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.agente (agente_id, usuario_id) FROM stdin;
1	1
2	2
3	3
4	4
5	6
6	7
7	8
8	10
9	11
10	12
11	13
12	14
13	15
14	16
15	17
16	19
17	20
\.


--
-- Data for Name: agente_area_de_visita; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.agente_area_de_visita (agente_area_de_visita_id, agente_id, area_de_visita_id) FROM stdin;
1	1	1
2	2	2
3	3	3
4	4	4
5	5	5
6	6	6
7	7	7
8	8	8
9	9	9
10	10	10
11	11	1
12	12	2
13	13	4
14	14	6
15	15	7
16	16	8
17	17	7
18	1	3
19	2	5
\.


--
-- Data for Name: area_de_visita; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.area_de_visita (area_de_visita_id, supervisor_id, cep, setor, numero_quarteirao, estado, municipio, bairro, logadouro) FROM stdin;
1	1	57035-180	Setor Ponta Verde 01	15	AL	Maceió	Ponta Verde	Avenida Álvaro Otacílio
2	2	57036-000	Setor Jatiúca 03	42	AL	Maceió	Jatiúca	Avenida Doutor Antônio Gomes de Barros
3	3	57030-170	Setor Pajuçara 02	28	AL	Maceió	Pajuçara	Rua Jangadeiros Alagoanos
4	1	57051-500	Setor Farol 05	112	AL	Maceió	Farol	Avenida Fernandes Lima
5	2	57036-540	Setor Cruz das Almas 01	67	AL	Maceió	Cruz das Almas	Avenida Brigadeiro Eduardo Gomes de Brito
6	3	57040-000	Setor Jacintinho 11	153	AL	Maceió	Jacintinho	Rua Cleto Campelo
7	1	57085-000	Setor Benedito Bentes 24	201	AL	Maceió	Benedito Bentes	Avenida Cachoeira do Meirim
8	2	57046-140	Setor Serraria 08	95	AL	Maceió	Serraria	Avenida Menino Marcelo
9	3	57052-480	Setor Gruta 04	78	AL	Maceió	Gruta de Lourdes	Rua Artur Vital da Silva
10	1	57035-160	Setor Mangabeiras 02	33	AL	Maceió	Mangabeiras	Rua Professora Maria Esther da Costa Barros
\.


--
-- Data for Name: arquivo_artigo; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.arquivo_artigo (arquivo_artigo_id, artigo_id, arquivo_nome) FROM stdin;
1	1	fluxograma_inspecao.png
2	2	foto_prato_planta.jpg
3	2	imagem_calha_entupida.jpg
4	2	foto_garrafas_quintal.png
5	3	foto_agente_aplicando_larvicida.jpg
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

COPY public.artigo (artigo_id, supervisor_id, nome_artigo_documento, conteudo_artigo_digitado, titulo, descricao) FROM stdin;
1	1	protocolo_inspecao_focal_2025.pdf	\N	Protocolo de Inspeção Focal para Agentes de Campo	Documento PDF com o passo a passo detalhado para a realização de inspeções focais em residências, comércios e terrenos baldios.
2	2	\N	A correta eliminação de criadouros é a principal forma de combate ao Aedes aegypti. Deve-se verificar calhas, garrafas, pneus e pratos de planta semanalmente. O uso de areia nos pratos de planta é uma medida eficaz para evitar o acúmulo de água. Em caso de caixas d'água, a vedação deve ser completa para impedir o acesso do mosquito. A colaboração da comunidade é essencial para o sucesso das ações de controle.	Guia Rápido: Eliminação de Criadouros Comuns	Um guia com dicas práticas para identificar e eliminar os criadouros mais comuns do mosquito Aedes aegypti no ambiente doméstico.
3	1	\N	O uso de larvicidas deve ser realizado por profissionais capacitados, seguindo estritamente as orientações do Ministério da Saúde. O produto deve ser aplicado em depósitos que não podem ser eliminados mecanicamente, como ralos internos e caixas de inspeção. A dosagem correta é crucial para a eficácia e para evitar a resistência do vetor. O período de reaplicação varia conforme o produto utilizado.	Uso Correto de Larvicidas no Controle Vetorial	Instruções técnicas sobre a aplicação, dosagem e segurança no manuseio de larvicidas utilizados no combate ao Aedes aegypti.
4	2	material_educativo_dengue.docx	\N	Material de Apoio para Ações Educativas	Documento com orientações e materiais (panfletos, cartazes) para serem utilizados em palestras e ações de conscientização com a comunidade.
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

COPY public.ciclos (ciclo_id, supervisor_id, ano_de_criacao, encerramento, ativo) FROM stdin;
1	1	2024-11-10	2025-01-10	f
2	2	2025-01-15	2025-03-15	f
3	3	2025-03-16	2025-05-16	f
4	1	2025-05-17	2025-07-17	f
5	2	2025-07-18	2025-09-18	f
6	3	2025-09-19	\N	t
\.


--
-- Data for Name: denuncia; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.denuncia (denuncia_id, supervisor_id, deposito_id, rua_avenida, numero, bairro, tipo_imovel, endereco_complemento, data_denuncia, hora_denuncia, observacoes) FROM stdin;
1	1	1	Rua Engenheiro Mário de Gusmão	980	Ponta Verde	Condomínio	Bloco A, perto da área da piscina	2025-09-18	10:30:00	Vários vasos de planta com água parada na área comum.
2	2	2	Avenida Doutor Júlio Marques Luz	1210	Jatiúca	Terreno Baldio	Ao lado de uma oficina mecânica.	2025-09-18	14:00:00	Acúmulo de lixo e pneus velhos com água da chuva.
3	3	3	Rua Professor Guedes de Miranda	455	Farol	Residência	Casa de esquina com muro branco e portão azul.	2025-09-19	09:15:00	Caixa d'água destampada no quintal, visível da rua.
4	1	4	Rua Desportista Humberto Guimarães	789	Ponta Verde	Comércio	Restaurante	2025-09-19	16:45:00	Garrafas e baldes acumulados no pátio traseiro do estabelecimento.
5	2	5	Rua Buarque de Macedo	550	Centro	Imóvel abandonado	Prédio antigo com janelas quebradas.	2025-09-20	08:00:00	Calhas entupidas e muito lixo no interior do imóvel.
\.


--
-- Data for Name: depositos; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.depositos (deposito_id, a1, a2, b, c, d1, d2, e) FROM stdin;
1	0	0	1	0	0	0	0
2	1	0	0	0	0	0	0
3	0	0	0	0	0	1	0
4	0	1	0	0	0	0	0
5	0	0	0	0	1	0	0
6	0	0	1	0	0	0	0
7	0	0	0	0	0	0	1
8	0	0	0	1	0	0	0
9	0	0	1	0	0	0	0
10	0	0	0	0	0	1	0
11	1	0	0	0	0	0	0
12	0	0	0	0	1	0	0
13	0	1	0	0	0	0	0
14	0	0	0	0	0	1	0
15	0	0	0	0	0	0	1
16	0	0	1	0	0	0	0
17	0	0	0	1	0	0	0
18	0	1	0	0	0	0	0
19	0	0	0	0	1	0	0
20	1	0	0	0	0	0	0
21	0	0	1	0	0	0	0
22	0	0	0	0	0	1	0
23	0	0	0	0	1	0	0
24	0	0	0	0	0	1	0
25	0	1	0	0	0	0	0
26	0	0	0	0	0	0	1
27	0	0	1	0	0	0	0
28	1	0	0	0	0	0	0
29	0	0	0	1	0	0	0
30	0	0	0	0	1	0	0
31	0	0	1	0	0	0	0
32	0	1	0	0	0	0	0
33	1	0	0	0	0	0	0
34	0	0	0	0	0	1	0
35	0	0	0	0	1	0	0
36	0	0	0	1	0	0	0
37	0	0	1	0	0	0	0
38	0	0	0	0	0	0	1
39	0	0	0	0	0	1	0
40	0	1	0	0	0	0	0
41	0	0	1	0	0	0	0
42	0	0	0	0	1	0	0
43	1	0	0	0	0	0	0
44	0	0	0	0	0	1	0
45	0	0	1	0	0	0	0
46	0	0	0	1	0	0	0
47	0	0	0	0	0	0	1
48	0	1	0	0	0	0	0
49	0	0	1	0	0	0	0
\.


--
-- Data for Name: larvicida; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.larvicida (larvicida_id, tipo, forma, quantidade) FROM stdin;
1	Pyriproxyfen	Granulado	2
2	Bti (Bacillus thuringiensis israelensis)	Tablete	1
3	Spinosad	Tablete	1
4	Pyriproxyfen	Granulado	5
5	Bti (Bacillus thuringiensis israelensis)	Granulado	10
6	Bti (Bacillus thuringiensis israelensis)	Tablete	2
7	Pyriproxyfen	Granulado	3
8	Pyriproxyfen	Granulado	4
9	Bti (Bacillus thuringiensis israelensis)	Granulado	15
10	Methoprene	Líquido	20
11	Spinosad	Tablete	1
12	Pyriproxyfen	Granulado	2
13	Bti (Bacillus thuringiensis israelensis)	Tablete	1
14	Pyriproxyfen	Granulado	5
15	Pyriproxyfen	Granulado	3
16	Bti (Bacillus thuringiensis israelensis)	Granulado	8
17	Bti (Bacillus thuringiensis israelensis)	Tablete	1
18	Pyriproxyfen	Granulado	6
19	Methoprene	Líquido	30
20	Pyriproxyfen	Granulado	4
21	Bti (Bacillus thuringiensis israelensis)	Granulado	12
22	Spinosad	Tablete	2
23	Pyriproxyfen	Granulado	2
24	Bti (Bacillus thuringiensis israelensis)	Tablete	1
25	Pyriproxyfen	Granulado	7
26	Bti (Bacillus thuringiensis israelensis)	Granulado	5
27	Bti (Bacillus thuringiensis israelensis)	Tablete	2
28	Pyriproxyfen	Granulado	3
29	Pyriproxyfen	Granulado	5
30	Bti (Bacillus thuringiensis israelensis)	Granulado	10
31	Spinosad	Tablete	1
32	Pyriproxyfen	Granulado	4
33	Bti (Bacillus thuringiensis israelensis)	Tablete	1
34	Pyriproxyfen	Granulado	2
35	Bti (Bacillus thuringiensis israelensis)	Granulado	20
36	Pyriproxyfen	Granulado	3
37	Bti (Bacillus thuringiensis israelensis)	Tablete	1
38	Methoprene	Líquido	25
39	Pyriproxyfen	Granulado	5
40	Bti (Bacillus thuringiensis israelensis)	Granulado	10
\.


--
-- Data for Name: registro_de_campo; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.registro_de_campo (registro_de_campo, rua, imovel_numero, imovel_lado, imovel_categoria_da_localidade, imovel_tipo, imovel_status, imovel_complemento, formulario_tipo, li, pe, t, df, pve, numero_da_amostra, quantiade_tubitos, observacao, area_de_visita_id, agente_id, deposito_id, larvicida_id, adulticida_id, registro_de_campo_arquivo_id) FROM stdin;
1	Rua Engenheiro Mário de Gusmão	123	Ímpar	Urbana	Residência	Tratado	Casa A	Dengue	f	f	t	t	f	\N	\N	Foco encontrado em prato de planta.	1	1	1	1	1	1
2	Avenida João Davino	45	Ímpar	Urbana	Comércio	Visitado	Loja 02	Dengue	f	f	f	f	f	\N	\N	Nenhum foco encontrado.	2	2	2	2	2	2
3	Rua Epaminondas Gracindo	86	Par	Urbana	Residência	Fechado	\N	Chikungunya	f	f	f	f	f	\N	\N	Morador ausente no momento da visita.	3	3	3	3	3	3
4	Rua Íris Alagoense	789	Ímpar	Urbana	Terreno Baldio	Tratado	\N	Zica	f	t	t	t	f	\N	\N	Limpeza e tratamento de focos em pneus.	4	4	4	4	4	4
5	Rua Lauro Machado da Costa	1010	Par	Urbana	Residência	Recusado	\N	Dengue	f	f	f	f	f	\N	\N	Morador não permitiu a entrada.	5	5	5	5	5	5
6	Rua São José	250	Par	Urbana	Residência	Visitado	Apto 301	Zica	t	f	f	t	f	A001	2	Coleta de amostra em ralo.	6	6	6	6	6	6
7	Avenida Norma Pimentel da Costa	33	Ímpar	Urbana	Comércio	Tratado	Restaurante	Chikungunya	f	t	t	f	f	\N	\N	Tratamento em caixa de gordura.	7	7	7	7	7	7
8	Avenida Presidente Roosevelt	542	Par	Urbana	Residência	Visitado	\N	Dengue	f	f	f	f	f	\N	\N	Ambiente limpo e sem depósitos.	8	8	8	8	8	8
9	Rua Doutor José de Castro Azevedo	99	Ímpar	Urbana	Outros	Tratado	Escola	Dengue	f	t	t	t	f	\N	\N	Tratamento em calhas e ralos do pátio.	9	9	9	9	9	9
10	Rua Adolfo Monteiro	1500	Par	Urbana	Residência	Visitado	Bloco B Apto 1002	Zica	f	f	f	t	f	\N	\N	Foco em bromélia na varanda.	10	10	10	10	10	10
11	Rua General João Saleiro Pitão	135	Ímpar	Urbana	Residência	Tratado	\N	Dengue	f	f	t	t	f	\N	\N	Atendendo denúncia. Foco eliminado.	1	11	11	11	11	11
12	Rua Industrial Cícero Toledo	88	Par	Urbana	Comércio	Visitado	Oficina	Chikungunya	f	t	f	f	f	\N	\N	Local inspecionado, sem larvas.	2	12	12	12	12	12
13	Rua Quintino Bocaiúva	712	Par	Urbana	Residência	Fechado	\N	Dengue	f	f	f	f	f	\N	\N	Imóvel para alugar, sem acesso.	3	13	13	13	13	13
14	Avenida Moreira e Silva	40	Par	Urbana	Residência	Visitado	\N	Zica	t	f	f	t	f	A002	3	Amostra coletada de balde no quintal.	4	14	14	14	14	14
15	Rua Bacharel Benigno de Oliveira	651	Ímpar	Urbana	Terreno Baldio	Tratado	Murado	Dengue	f	f	t	f	f	\N	\N	Tratamento com larvicida granulado.	5	15	15	15	15	15
16	Rua do Sol	199	Ímpar	Urbana	Residência	Visitado	\N	Dengue	f	f	f	f	f	\N	\N	Nenhum problema encontrado.	6	16	16	16	\N	16
17	Rua Caxangá	2048	Par	Urbana	Residência	Tratado	Casa dos Fundos	Chikungunya	f	f	t	t	f	\N	\N	Caixa d'água destampada, tratada.	7	17	17	17	\N	17
18	Rua Adolfo Gustavo	321	Ímpar	Urbana	Comércio	Visitado	Padaria	Dengue	f	f	f	f	f	\N	\N	Sem anormalidades.	8	1	18	18	\N	18
19	Avenida Artagnan Martins	55	Ímpar	Urbana	Residência	Recusado	Portão alto	Zica	f	f	f	f	f	\N	\N	Proprietário se recusou a abrir.	9	2	19	19	\N	19
20	Rua Doutor Antônio Cansanção	876	Par	Urbana	Residência	Fechado	\N	Dengue	f	f	f	f	f	\N	\N	Ninguém atendeu.	10	3	20	20	\N	20
21	Rua Doutor Noel Nutels	901	Ímpar	Urbana	Residência	Tratado	\N	Chikungunya	f	f	t	t	f	\N	\N	Foco em piscina abandonada, tratada.	1	4	21	21	\N	\N
22	Rua Bancário Rady Gusmão do Nascimento	112	Par	Urbana	Outros	Visitado	Igreja	Dengue	f	t	f	f	f	\N	\N	Verificado bebedouros e calhas.	2	5	22	22	\N	\N
23	Rua Doutor Lessa de Azevedo	433	Ímpar	Urbana	Residência	Visitado	Apto 505	Dengue	f	f	f	f	f	\N	\N	Sem focos.	3	6	23	23	\N	\N
24	Rua Professor Guedes de Miranda	1800	Par	Urbana	Comércio	Tratado	Supermercado	Zica	f	t	t	t	f	\N	\N	Tratamento em área de carga/descarga.	4	7	24	24	\N	\N
25	Rua João Lins	21	Ímpar	Urbana	Residência	Visitado	\N	Chikungunya	t	f	f	f	f	A003	1	Coleta de amostra positiva.	5	8	25	25	\N	\N
26	Rua Santa Inês	777	Ímpar	Urbana	Residência	Tratado	Casa com piscina	Dengue	f	f	t	t	f	\N	\N	Piscina tratada com larvicida.	6	9	26	26	\N	\N
27	Avenida Garça Torta	1234	Par	Urbana	Comércio	Visitado	Clínica	Dengue	f	f	f	f	f	\N	\N	Ok.	7	10	27	27	\N	\N
28	Rua Emérito de Farias	56	Par	Urbana	Residência	Fechado	\N	Zica	f	f	f	f	f	\N	\N	Cachorro bravo, morador ausente.	8	11	28	28	\N	\N
29	Rua Elói de Lemos	821	Ímpar	Urbana	Terreno Baldio	Visitado	Aberto	Chikungunya	f	f	f	t	f	\N	\N	Encontrado lixo com água.	9	12	29	29	\N	\N
30	Rua Pompeu Sarmento	10	Par	Urbana	Residência	Recusado	Apto 101	Dengue	f	f	f	f	f	\N	\N	Recusa.	10	13	30	30	\N	\N
31	Avenida Álvaro Otacílio	222	Par	Urbana	Residência	Tratado	\N	Dengue	f	f	t	f	f	\N	\N	Tratamento focal realizado.	1	14	31	\N	\N	\N
32	Avenida Doutor Antônio Gomes de Barros	345	Ímpar	Urbana	Outros	Visitado	Cemitério	Zica	f	t	f	t	f	\N	\N	Verificação de vasos e jazigos.	2	15	32	\N	\N	\N
33	Rua Jangadeiros Alagoanos	981	Ímpar	Urbana	Comércio	Visitado	Borracharia	Dengue	f	t	f	t	f	\N	\N	Pneus armazenados corretamente.	3	16	33	\N	\N	\N
34	Avenida Fernandes Lima	1730	Par	Urbana	Residência	Visitado	\N	Chikungunya	f	f	f	f	f	\N	\N	Ok.	4	17	34	\N	\N	\N
35	Avenida Brigadeiro Eduardo Gomes de Brito	501	Ímpar	Urbana	Residência	Fechado	Apto 501	Dengue	f	f	f	f	f	\N	\N	Morador não atendeu.	5	1	35	\N	\N	\N
36	Rua Cleto Campelo	48	Par	Urbana	Comércio	Visitado	\N	Zica	f	f	f	f	f	\N	\N	Nenhum foco encontrado.	6	2	36	\N	\N	\N
37	Avenida Cachoeira do Meirim	679	Ímpar	Urbana	Residência	Tratado	\N	Dengue	f	f	t	t	f	\N	\N	Denúncia procedente. Local tratado.	7	3	37	\N	\N	\N
38	Avenida Menino Marcelo	1111	Ímpar	Urbana	Residência	Visitado	Cond. Fechado	Chikungunya	f	f	f	f	f	\N	\N	Área comum verificada.	8	4	38	\N	\N	\N
39	Rua Artur Vital da Silva	30	Par	Urbana	Residência	Recusado	\N	Dengue	f	f	f	f	f	\N	\N	Morador informou que não recebe visitas.	9	5	39	\N	\N	\N
40	Rua Professora Maria Esther da Costa Barros	499	Ímpar	Urbana	Terreno Baldio	Visitado	\N	Zica	f	f	f	f	f	\N	\N	Sem água parada no momento.	10	6	40	\N	\N	\N
41	Rua Engenheiro Mário de Gusmão	580	Par	Urbana	Residência	Tratado	\N	Dengue	t	f	t	t	f	A004	4	Amostra coletada e local tratado.	1	7	41	\N	\N	\N
42	Avenida João Davino	128	Par	Urbana	Comércio	Visitado	Galpão	Dengue	f	t	f	f	f	\N	\N	Inspecionado.	2	8	42	\N	\N	\N
43	Rua Epaminondas Gracindo	77	Ímpar	Urbana	Residência	Fechado	\N	Chikungunya	f	f	f	f	f	\N	\N	Tentativa de visita sem sucesso.	3	9	43	\N	\N	\N
44	Rua Íris Alagoense	300	Par	Urbana	Residência	Visitado	\N	Dengue	f	f	f	f	f	\N	\N	Orientações verbais fornecidas.	4	10	44	\N	\N	\N
45	Rua Lauro Machado da Costa	1420	Par	Urbana	Outros	Tratado	Posto de Saúde	Zica	f	t	t	t	f	\N	\N	Tratamento periódico de rotina.	5	11	45	\N	\N	\N
\.


--
-- Data for Name: registro_de_campo_arquivos; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.registro_de_campo_arquivos (registro_de_campo_arquivo_id, arquivo_nome) FROM stdin;
1	IMG_20250921_101532.jpg
2	IMG_20250921_101545_foco_caixa_dagua.jpg
3	IMG_20250921_110510_pneus_quintal.jpg
4	d3e4f5a6-b7c8-9012-d3e4-f5a6b7c89012.jpg
5	foto_terreno_antes_limpeza.png
6	foto_terreno_depois_limpeza.png
7	IMG_20250921_093301_prova_visita.jpg
8	IMG_20250921_093315_larvicida_aplicado.jpg
9	VID_20250921_093500_vistoria.mp4
10	e4f5a6b7-c8d9-0123-e4f5-a6b7c8d90123.jpg
11	IMG_20250921_104520_vasos_de_planta.jpg
12	IMG_20250921_104535_tratamento_focal.jpg
13	a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890.jpg
14	foto_calha_entupida_com_agua.jpg
15	foto_prova_tratamento.jpg
16	IMG_20250921_112005.jpg
17	IMG_20250921_112018_prova_visita_recusada.jpg
18	b2c3d4e5-f6a7-8901-b2c3-d4e5f6a78901.png
19	VID_20250921_141000_conversa_com_morador.mp4
20	IMG_20250921_141230_imovel_fechado.jpg
\.


--
-- Data for Name: supervisor; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.supervisor (supervisor_id, usuario_id) FROM stdin;
1	5
2	9
3	18
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.usuario (usuario_id, supervisor_criador_id, nome_completo, cpf, rg, data_nascimento, email, telefone_ddd, telefone_numero, estado, municipio, bairro, logradouro, numero, registro_do_servidor, cargo, situacao_atual, data_de_admissao, setor_de_atuacao, senha, nivel_de_acesso) FROM stdin;
1	1	João da Silva	12345678901	1234567	1985-06-15	joao.silva@example.com	11	987654321	SP	São Paulo	Centro	Rua das Flores	123	RS-2025-001	Analista	t	2025-01-10	TI	senhaSegura123	usuario
2	1	Pedro Cavalcante	admin	212324567	1983-06-15	pedro.silva@example.com	11	987354321	SP	São Paulo	Centro	Rua das Flores	123	RS-2025-001	Analista	t	2025-01-10	TI	123456	supervisor
3	1	Maria Oliveira Santos	23456789012	2345678	1990-03-22	maria.santos@example.com	21	912345678	RJ	Rio de Janeiro	Copacabana	Avenida Atlântica	1702	RS-2025-002	Gerente de Projetos	t	2024-05-20	Projetos	outrasenha456	usuario
4	2	Carlos Pereira Costa	34567890123	3456789	1988-11-01	carlos.costa@example.com	31	988776655	MG	Belo Horizonte	Savassi	Rua Fernandes Tourinho	500	RS-2025-003	Desenvolvedor Sênior	t	2023-08-15	TI	senhaDev321	usuario
5	5	Ana Clara Ferreira	45678901234	4567890	1995-09-10	ana.ferreira@example.com	41	977665544	PR	Curitiba	Batel	Avenida do Batel	1868	RS-2025-004	Analista de RH	f	2024-02-01	Recursos Humanos	senhaRH987	usuario
6	1	Pedro Rodrigues Alves	56789012345	5678901	1982-01-30	pedro.alves@example.com	51	966554433	RS	Porto Alegre	Moinhos de Vento	Rua Padre Chagas	415	RS-2025-005	Coordenador Financeiro	t	2022-11-25	Financeiro	senhaFin159	supervisor
7	2	Juliana Souza Lima	67890123456	6789012	1998-07-12	juliana.lima@example.com	61	955443322	DF	Brasília	Asa Sul	SCS Quadra 07	10	RS-2025-006	Estagiária	t	2025-07-01	Marketing	senhaEstagio753	usuario
8	5	Lucas Martins	78901234567	7890123	1992-04-25	lucas.martins@example.com	71	944332211	BA	Salvador	Barra	Avenida Oceânica	2400	RS-2025-007	Analista de Marketing	t	2023-03-18	Marketing	senhaMkt357	usuario
9	2	Fernanda Gonçalves	89012345678	8901234	1986-12-08	fernanda.g@example.com	81	933221100	PE	Recife	Boa Viagem	Avenida Boa Viagem	97	RS-2025-008	Designer Gráfico	t	2024-09-02	Criação	senhaDesign123	usuario
10	1	Ricardo Almeida	90123456789	9012345	1979-05-19	ricardo.a@example.com	11	922110099	SP	São Paulo	Pinheiros	Rua dos Pinheiros	1000	RS-2025-009	Diretor de TI	t	2020-01-15	TI	senhaDiretorTop	supervisor
11	4	Beatriz Rocha	01234567890	0123456	2000-02-28	beatriz.rocha@example.com	21	911009988	RJ	Niterói	Icaraí	Rua Gavião Peixoto	30	RS-2025-010	Assistente Administrativo	t	2025-06-11	Administrativo	senhaAdmin456	usuario
12	3	Guilherme Barbosa	11223344556	1122334	1993-10-03	guilherme.b@example.com	31	988887777	MG	Contagem	Eldorado	Avenida João César de Oliveira	1275	RS-2025-011	Técnico de Suporte	t	2024-04-10	Suporte	senhaSup555	usuario
13	3	Larissa Azevedo	22334455667	2233445	1991-08-14	larissa.azevedo@example.com	48	977776666	SC	Florianópolis	Centro	Rua Felipe Schmidt	515	RS-2025-012	Analista de Negócios	t	2023-10-09	Negócios	senhaNegocios333	usuario
14	3	Rafael Ribeiro	33445566778	3344556	1987-03-29	rafael.r@example.com	85	966665555	CE	Fortaleza	Meireles	Avenida Beira Mar	4260	RS-2025-013	Desenvolvedor Pleno	t	2025-02-20	TI	senhaPleno777	usuario
15	2	Camila Nogueira	44556677889	4455667	1999-01-05	camila.n@example.com	92	955554444	AM	Manaus	Adrianópolis	Rua Teresina	151	RS-2025-014	Desenvolvedor Júnior	t	2025-08-12	TI	senhaJunior888	usuario
16	4	Felipe Monteiro	55667788990	5566778	1984-06-07	felipe.m@example.com	62	944443333	GO	Goiânia	Setor Bueno	Avenida T-10	100	RS-2025-015	Contador	t	2021-07-22	Financeiro	senhaContador999	usuario
17	1	Vanessa Dias	66778899001	6677889	1996-09-21	vanessa.dias@example.com	27	933332222	ES	Vitória	Jardim da Penha	Rua da Lama	50	RS-2025-016	Assistente de Marketing	f	2024-01-30	Marketing	senhaAssistMkt111	usuario
18	2	Bruno Medeiros	77889900112	7788990	1990-11-18	bruno.m@example.com	11	922221111	SP	Guarulhos	Macedo	Avenida Paulo Faccini	1500	RS-2025-017	Analista de Logística	t	2023-05-16	Logística	senhaLog222	usuario
19	1	Helena Justino	88990011223	8899001	1980-02-13	helena.j@example.com	41	911110000	PR	São José dos Pinhais	Centro	Rua XV de Novembro	210	RS-2025-018	Gerente de RH	t	2019-12-05	Recursos Humanos	senhaGerenteRH321	supervisor
20	4	Igor Fernandes	99001122334	9900112	1997-07-07	igor.f@example.com	21	999998888	RJ	Duque de Caxias	Vila São Luís	Rua Genaro Lomba	15	RS-2025-019	Recrutador	t	2025-03-03	Recursos Humanos	senhaRecrutador444	usuario
21	5	Tiago Moreira	00112233445	0011223	1989-10-26	tiago.m@example.com	11	988887777	SP	Campinas	Cambuí	Rua Coronel Quirino	200	RS-2025-020	Arquiteto de Soluções	t	2022-09-01	TI	senhaArquiteto555	usuario
\.


--
-- Name: adulticida_adulticida_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.adulticida_adulticida_id_seq', 30, true);


--
-- Name: agente_agente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.agente_agente_id_seq', 17, true);


--
-- Name: agente_area_de_visita_agente_area_de_visita_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.agente_area_de_visita_agente_area_de_visita_id_seq', 19, true);


--
-- Name: area_de_visita_area_de_visita_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.area_de_visita_area_de_visita_id_seq', 10, true);


--
-- Name: arquivo_artigo_arquivo_artigo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.arquivo_artigo_arquivo_artigo_id_seq', 5, true);


--
-- Name: arquivos_denuncia_arquivo_denuncia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.arquivos_denuncia_arquivo_denuncia_id_seq', 8, true);


--
-- Name: artigo_artigo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.artigo_artigo_id_seq', 4, true);


--
-- Name: ciclo_area_de_visita_ciclo_area_de_visita_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.ciclo_area_de_visita_ciclo_area_de_visita_id_seq', 60, true);


--
-- Name: ciclos_ciclo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.ciclos_ciclo_id_seq', 6, true);


--
-- Name: denuncia_denuncia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.denuncia_denuncia_id_seq', 5, true);


--
-- Name: depositos_deposito_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.depositos_deposito_id_seq', 49, true);


--
-- Name: larvicida_larvicida_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.larvicida_larvicida_id_seq', 40, true);


--
-- Name: registro_de_campo_arquivos_registro_de_campo_arquivo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.registro_de_campo_arquivos_registro_de_campo_arquivo_id_seq', 20, true);


--
-- Name: registro_de_campo_registro_de_campo_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.registro_de_campo_registro_de_campo_seq', 45, true);


--
-- Name: supervisor_supervisor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.supervisor_supervisor_id_seq', 3, true);


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
-- Name: arquivo_artigo arquivo_artigo_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.arquivo_artigo
    ADD CONSTRAINT arquivo_artigo_pkey PRIMARY KEY (arquivo_artigo_id);


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
    ADD CONSTRAINT registro_de_campo_pkey PRIMARY KEY (registro_de_campo);


--
-- Name: supervisor supervisor_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.supervisor
    ADD CONSTRAINT supervisor_pkey PRIMARY KEY (supervisor_id);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (usuario_id);


--
-- Name: registro_de_campo fk_adulticida; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT fk_adulticida FOREIGN KEY (adulticida_id) REFERENCES public.adulticida(adulticida_id) ON DELETE SET NULL;


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
-- Name: agente_area_de_visita fk_area_de_visita; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.agente_area_de_visita
    ADD CONSTRAINT fk_area_de_visita FOREIGN KEY (area_de_visita_id) REFERENCES public.area_de_visita(area_de_visita_id) ON DELETE CASCADE;


--
-- Name: ciclo_area_de_visita fk_area_de_visita; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ciclo_area_de_visita
    ADD CONSTRAINT fk_area_de_visita FOREIGN KEY (area_de_visita_id) REFERENCES public.area_de_visita(area_de_visita_id) ON DELETE CASCADE;


--
-- Name: registro_de_campo fk_area_de_visita; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT fk_area_de_visita FOREIGN KEY (area_de_visita_id) REFERENCES public.area_de_visita(area_de_visita_id) ON DELETE SET NULL;


--
-- Name: arquivo_artigo fk_artigo; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.arquivo_artigo
    ADD CONSTRAINT fk_artigo FOREIGN KEY (artigo_id) REFERENCES public.artigo(artigo_id) ON DELETE CASCADE;


--
-- Name: ciclo_area_de_visita fk_ciclos; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.ciclo_area_de_visita
    ADD CONSTRAINT fk_ciclos FOREIGN KEY (ciclo_id) REFERENCES public.ciclos(ciclo_id) ON DELETE CASCADE;


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
-- Name: registro_de_campo fk_larvicida; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT fk_larvicida FOREIGN KEY (larvicida_id) REFERENCES public.larvicida(larvicida_id) ON DELETE SET NULL;


--
-- Name: registro_de_campo fk_registro_de_campo_arquivos; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.registro_de_campo
    ADD CONSTRAINT fk_registro_de_campo_arquivos FOREIGN KEY (registro_de_campo_arquivo_id) REFERENCES public.registro_de_campo_arquivos(registro_de_campo_arquivo_id) ON DELETE SET NULL;


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

\unrestrict IkDj5uW3JrHJnwDjIuCtMCL8Tjm1SeJacholQn5NnxZsqGzzpjW0S90rHOGE7IF

