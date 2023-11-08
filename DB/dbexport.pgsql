--
-- PostgreSQL database dump
--

-- Dumped from database version 13.11
-- Dumped by pg_dump version 13.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: caregivers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.caregivers (
    patient_id integer NOT NULL,
    caregivers json
);


ALTER TABLE public.caregivers OWNER TO postgres;

--
-- Name: patient_medic_relation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.patient_medic_relation (
    patient integer NOT NULL,
    medic integer
);


ALTER TABLE public.patient_medic_relation OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name character varying,
    surname character varying,
    role integer NOT NULL,
    thingspeak_channel character varying,
    cf character varying NOT NULL,
    passkey character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: caregivers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.caregivers (patient_id, caregivers) FROM stdin;
3	{"phone": ["+393458983300"]}
2	{"phone": ["+393317667951"]}
\.


--
-- Data for Name: patient_medic_relation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.patient_medic_relation (patient, medic) FROM stdin;
2	1
3	1
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name) FROM stdin;
1	medic
2	patient
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, name, surname, role, thingspeak_channel, cf, passkey) FROM stdin;
1	Medic	Nice	1		nicemedic	
2	Andrea	Cencio	2	2205223	CNCNDR	6G77I4QGB1IBELF7
3	Federica	Minervino	2	2322486	MNRFRC	KFZEYM0JRVUEEXUX
\.


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 2, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 17, true);


--
-- Name: caregivers caregivers_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.caregivers
    ADD CONSTRAINT caregivers_pk PRIMARY KEY (patient_id);


--
-- Name: patient_medic_relation patient_medic_relation_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient_medic_relation
    ADD CONSTRAINT patient_medic_relation_pk PRIMARY KEY (patient);


--
-- Name: roles roles_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pk PRIMARY KEY (id);


--
-- Name: roles roles_un; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_un UNIQUE (name);


--
-- Name: users users_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pk PRIMARY KEY (id);


--
-- Name: users users_un; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_un UNIQUE (role, cf);


--
-- Name: caregivers caregivers_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.caregivers
    ADD CONSTRAINT caregivers_fk FOREIGN KEY (patient_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: patient_medic_relation patient_medic_relation_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient_medic_relation
    ADD CONSTRAINT patient_medic_relation_fk FOREIGN KEY (patient) REFERENCES public.users(id) ON UPDATE CASCADE;


--
-- Name: patient_medic_relation patient_medic_relation_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.patient_medic_relation
    ADD CONSTRAINT patient_medic_relation_fk_1 FOREIGN KEY (medic) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE SET NULL;


--
-- Name: users users_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_fk FOREIGN KEY (role) REFERENCES public.roles(id) ON UPDATE CASCADE ON DELETE SET DEFAULT;


--
-- PostgreSQL database dump complete
--

