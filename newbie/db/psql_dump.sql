--
-- PostgreSQL database dump
--

-- Dumped from database version 11.1
-- Dumped by pg_dump version 11.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: admin; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admin (
    id integer NOT NULL,
    emp_id character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    super_admin boolean,
    roles character varying(1000),
    created_date timestamp without time zone NOT NULL,
    team character varying(100)
);


ALTER TABLE public.admin OWNER TO postgres;

--
-- Name: admin_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.admin_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_id_seq OWNER TO postgres;

--
-- Name: admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.admin_id_seq OWNED BY public.admin.id;


--
-- Name: admin_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admin_roles (
    id integer NOT NULL,
    role_name character varying(20) NOT NULL,
    role_description character varying(100) NOT NULL,
    created_date timestamp without time zone NOT NULL
);


ALTER TABLE public.admin_roles OWNER TO postgres;

--
-- Name: admin_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.admin_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.admin_roles_id_seq OWNER TO postgres;

--
-- Name: admin_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.admin_roles_id_seq OWNED BY public.admin_roles.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: auth_groups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auth_groups (
    id integer NOT NULL,
    groups character varying(150) NOT NULL,
    created_date timestamp without time zone NOT NULL
);


ALTER TABLE public.auth_groups OWNER TO postgres;

--
-- Name: auth_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auth_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_groups_id_seq OWNER TO postgres;

--
-- Name: auth_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auth_groups_id_seq OWNED BY public.auth_groups.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    type character varying(32) NOT NULL,
    topic character varying(100) NOT NULL,
    title_link json,
    send_day integer,
    send_hour integer,
    repeatable boolean,
    repeat_number integer,
    repeat_type character varying(6),
    repeat_times integer,
    text character varying(999) NOT NULL,
    send_date timestamp without time zone NOT NULL,
    send_once boolean NOT NULL,
    created_date timestamp without time zone NOT NULL,
    country character varying(1000) NOT NULL,
    callback_id character varying(15),
    tags character varying[],
    team character varying(100),
    owner character varying(50),
    location character varying(1000),
    emp_type character varying(1000)
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: messages_to_send; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages_to_send (
    id integer NOT NULL,
    emp_id character varying(50) NOT NULL,
    message_id character varying NOT NULL,
    send_dttm timestamp with time zone NOT NULL,
    send_order integer NOT NULL,
    send_status boolean NOT NULL,
    cancel_status boolean NOT NULL,
    last_updated timestamp without time zone NOT NULL,
    created_date timestamp without time zone NOT NULL
);


ALTER TABLE public.messages_to_send OWNER TO postgres;

--
-- Name: messages_to_send_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.messages_to_send_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_to_send_id_seq OWNER TO postgres;

--
-- Name: messages_to_send_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.messages_to_send_id_seq OWNED BY public.messages_to_send.id;


--
-- Name: people; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.people (
    id integer NOT NULL,
    emp_id character varying(50) NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    email character varying(150) NOT NULL,
    slack_handle character varying(50),
    start_date timestamp without time zone NOT NULL,
    last_modified timestamp without time zone NOT NULL,
    timezone character varying(100),
    country character varying(4),
    manager_id character varying(120) NOT NULL,
    user_opt_out boolean NOT NULL,
    manager_opt_out boolean NOT NULL,
    admin_opt_out boolean NOT NULL,
    created_date timestamp without time zone NOT NULL,
    admin_requested boolean,
    admin_role_requested character varying[],
    admin_requested_date timestamp without time zone,
    admin_status character varying,
    admin_status_updated_date timestamp without time zone,
    admin_request_updated_by integer,
    admin_team character varying(100)
);


ALTER TABLE public.people OWNER TO postgres;

--
-- Name: people_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.people_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.people_id_seq OWNER TO postgres;

--
-- Name: people_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.people_id_seq OWNED BY public.people.id;


--
-- Name: user_feedback; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_feedback (
    id integer NOT NULL,
    action character varying(10) NOT NULL,
    emp_id character varying(50) NOT NULL,
    rating character varying(10) NOT NULL,
    comment character varying(300),
    created_date timestamp without time zone NOT NULL
);


ALTER TABLE public.user_feedback OWNER TO postgres;

--
-- Name: user_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_feedback_id_seq OWNER TO postgres;

--
-- Name: user_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_feedback_id_seq OWNED BY public.user_feedback.id;


--
-- Name: admin id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin ALTER COLUMN id SET DEFAULT nextval('public.admin_id_seq'::regclass);


--
-- Name: admin_roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_roles ALTER COLUMN id SET DEFAULT nextval('public.admin_roles_id_seq'::regclass);


--
-- Name: auth_groups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_groups_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: messages_to_send id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages_to_send ALTER COLUMN id SET DEFAULT nextval('public.messages_to_send_id_seq'::regclass);


--
-- Name: people id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people ALTER COLUMN id SET DEFAULT nextval('public.people_id_seq'::regclass);


--
-- Name: user_feedback id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_feedback ALTER COLUMN id SET DEFAULT nextval('public.user_feedback_id_seq'::regclass);


--
-- Data for Name: admin; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admin (id, emp_id, name, super_admin, roles, created_date, team) FROM stdin;
1	ad|Mozilla-LDAP|mballard	Marty Ballard	t	[,Admin,Managers,Super Admin}	2019-01-01 12:00:00	IT: InfoSec
\.


--
-- Data for Name: admin_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admin_roles (id, role_name, role_description, created_date) FROM stdin;
1	Admin	Admin	2019-02-06 16:15:12.530106
2	Managers	Managers	2019-02-06 16:15:22.253522
3	Super Admin	Super Admin	2019-02-06 16:15:29.850107
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
dcd90c44806f
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages (id, type, topic, title_link, send_day, send_hour, repeatable, repeat_number, repeat_type, repeat_times, text, send_date, send_once, created_date, country, callback_id, tags, team, owner, location, emp_type) FROM stdin;
1	best_practices	New Hire IT Information	[{"name": "IT Info", "url": "https://mana.mozilla.org/wiki/x/RwQXAg"}]	1	9	f	\N	\N	\N	This New Hire IT Information page and Checklist will get you set up on our apps and tools.	2019-01-14 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{ldap,printers,gmail,slack,irc,encryption,data,privacy,gsuite}	IT	Josephine Leung	All	All
71	informational	Virtual Private Network (VPN)	[{"name": "VPN", "url": "https://mana.mozilla.org/wiki/x/BgQXAg"}]	29	9	f	\N	\N	\N	Do you need to access servers in the data centers? 	2019-01-14 00:00:00	f	2019-01-15 00:47:50.677662	ALL	\N	{VPN,remote_working,access}	IT: Service Desk	Mike Poessy	All	All
20	best_practices	Travel Visas	[{"name": "Travel Visas", "url": "https://mana.mozilla.org/wiki/display/PR/Travel+Visas"}]	18	9	f	\N	\N	\N	Need to travel outside the U.S. for business? Read our Travel Visa page for guidelines and tips.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{travel,visa,visas}	People	Josephine Leung	\N	\N
21	best_practices	Expensify - Employee Expenses	[{"name": "Expensify", "url": "https://mana.mozilla.org/wiki/display/FIN/Expensify+-+Employee+Expense+Reporting+System"}]	19	9	f	\N	\N	\N	We use Expensify to report expenses.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{expenses,expensify}	People	Josephine Leung	\N	\N
22	best_practices	Egencia (Mana page)	[{"name": "Egencia", "url": "https://mana.mozilla.org/wiki/display/WPR/Egencia"}]	20	9	f	\N	\N	\N	We use Egencia to manage and book Mozilla-related travel.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{travel,egencia,flight,hotel,rental,car}	People	Josephine Leung	\N	\N
23	best_practices	Policies	[{"name": "Policies", "url": "https://mana.mozilla.org/wiki/display/PR/Policy"}]	22	9	f	\N	\N	\N	Learn about Mozilla's policies	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{policies,procedures}	Legal	Josephine Leung	\N	\N
5	best_practices	Gmail 101	[{"name": "Gmail 101", "url": "https://mana.mozilla.org/wiki/display/SD/Gmail+101"}]	3	9	f	\N	\N	\N	Read our Gmail 101 page for tips on how to manage your inbox and more.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{gmail,email,inbox}	IT	Josephine Leung	\N	\N
6	best_practices	Mozilla Phonebook	[{"name": "Phonebook", "url": "https://phonebook.mozilla.org/"}]	5	9	f	\N	\N	\N	Find your fellow Mozillians on Phonebook.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{phone,phonebook,directory}	IT	Josephine Leung	\N	\N
72	informational	Beta Testing	[{"name": "Foxfooding", "url": "https://mana.mozilla.org/wiki/x/6oveB"}]	30	9	f	\N	\N	\N	Want to help beta test Mozilla products? Help dogfood or foxfood. 	2019-01-14 00:00:00	f	2019-01-15 02:20:22.123147	ALL	\N	{Beta,testing,dogfood,foxfood,nightly,pocket,scout,focus}	IT: Service Desk	Mike Poessy	All	All
8	best_practices	Service Desk	""	6	12	f	\N	\N	\N	Need to contact the Service Desk? Email servicedesk@mozilla.com or message #servicedesk on Slack	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{service}	IT	Josephine Leung	\N	\N
14	best_practices	All Hands (general info)	[{"name": "All Hands", "url": "https://mana.mozilla.org/wiki/display/IC/All+Hands+Content+Hub"}]	11	9	f	\N	\N	\N	It's never to early to start thinking about the next All Hands. Watch out for emails from @brianna for details.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{"all hands",meeting}	IT	Josephine Leung	\N	\N
24	best_practices	Monthly Internal Meeting	[{"name": "View Meetings", "url": "https://mana.mozilla.org/wiki/display/IC/Monthly+Internal+Meetings"}]	21	9	f	\N	\N	\N	Mark your calendar for Mozilla's Monthly Internal meetings for 2019	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{internal,meeting}	IT	Josephine Leung	\N	\N
25	best_practices	Open Door Policy	[{"name": "Policy", "url": "https://mana.mozilla.org/wiki/display/PR/Open+Door+Policy"}]	23	9	f	\N	\N	\N	Read about Mozilla's Open Door Policy	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{open,door,policy}	People	Tara Robertson	\N	\N
85	best_practices	Data Classification	[{"name": "Data", "url": "Classification"}]	38	9	f	\N	\N	\N	We love working in the open, but not everything is meant for everyone. Mark your documents and emails with Mozilla data classification markings, so recipients know who they should share with.	2019-01-17 00:00:00	f	2019-01-17 20:54:24.661929	All	\N	{"data classification","marking documents"}	IT: InfoSec	Tristan Weir	All	All
26	best_practices	PTO tool	[{"name": "PTO", "url": "https://pto.mozilla.org/"}]	24	9	f	\N	\N	\N	Submit your PTO requests using our PTO tool.	2018-12-07 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{PTO,vacation,sick}	IT	Josephine Leung	\N	\N
27	best_practices	Compensation	[{"name": "Comp", "url": "https://mana.mozilla.org/wiki/display/PR/Compensation"}]	25	9	f	\N	\N	\N	Our Compensation section has info on merit increases, bonuses, and salary structures.	2018-12-07 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{compensation,raise,pay,bonuses,salary}	People	Josephine Leung	\N	\N
2	informational	Welcome	[]	1	9	f	\N	\N	\N	Hi! I'm Newbie Bot, a chatbot designed to help ease you into life as a Mozillian. Over the next few weeks, I'll send you links to important information that should answer questions that all new Mozillians have.\r\n\r\nRight now, our interaction is one-sided, i.e., you won't be able to ask me anything. But you can search for topics such as holidays by sending me "/newbie search PTO" and I'll point you in the right direction. \r\n\r\nCurious about how I work? Type "/newbie help" to be directed to my Help page.	2019-01-17 00:00:00	f	2018-12-19 20:40:33.793591	All		{welcome}	IT	Josephine Leung	All	All
68	best_practices	Password Managers	[{"name": "Password Managers", "url": "https://mana.mozilla.org/wiki/x/Fo9WB"}]	26	9	f	\N	\N	\N	Are you using secure passwords? Need some help?	2019-01-14 00:00:00	f	2019-01-15 00:26:26.98761	ALL	\N	{Security,password,Safety,password_manager}	IT: Service Desk	Mike Poessy	All	All
9	best_practices	Medical Insurance (U.S.)	[{"name": "Insurance", "url": "https://mana.mozilla.org/wiki/display/PR/Medical+insurance"}]	7	9	f	\N	\N	\N	Reminder: you must enroll in your medical plan within 30 days after your start date.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	US		{medical,US,insurance}	People	Josephine Leung	\N	\N
73	instruction	Out of Office/Vacation Reply	[{"name": "OOO", "url": "https://mana.mozilla.org/wiki/x/4YBoBQ"}]	31	9	f	\N	\N	\N	Going on vacation? Going to be out of the office? Set up an out of office reply. 	2019-02-01 00:00:00	f	2019-01-15 04:06:22.643715	All	\N	{holiday,ooo,pto,Vacation,"out of office",Email,Gmail}	IT: Service Desk	Mike Poessy	All	All
3	best_practices	Slack	[{"name": "Slack", "url": "https://mana.mozilla.org/wiki/display/CCT/Slack"}]	2	9	f	\N	\N	\N	Slack is our main messaging tool. NOTE: never discuss confidential information or share passwords on Slack.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{slack,messaging}	IT	Josephine Leung	\N	\N
4	best_practices	The Hub	[{"name": "The Hub", "url": "https://mozilla.service-now.com/sp"}]	4	9	f	\N	\N	\N	Need computer or facilities help? Want to set up an event? Ship something? Check out The Hub.	2018-12-07 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{hub,service-now,service,computer,facilities,vpn}	IT	Josephine Leung	\N	\N
75	instruction	PGP Fingerprint	[{"name": "GPG", "url": "https://mana.mozilla.org/wiki/x/VSOxAw"}]	32	9	f	\N	\N	\N	Have you shared your public PGP Fingerprint?	2019-01-15 00:00:00	f	2019-01-15 18:51:53.217242	ALL	\N	{fingerprint,PGP,GPG}	IT: Service Desk	Mike Poessy	All	All
13	best_practices	WPR	""	15	12	f	\N	\N	\N	WPR (Workspace Resources) makes sure our facilities – from office supplies and shipping to event organisation and security – run smoothly! Need support? Email wpr@mozilla.com or message #wpr on Slack.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{WPR,HR,resources}	WPR	Josephine Leung	\N	\N
11	best_practices	People	""	8	9	f	\N	\N	\N	Need to contact the People team (HR)? Email peopleops@mozilla.com	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{people,HR}	People	Josephine Leung	\N	\N
12	best_practices	Enter Federal Withholding	[{"name": "Withholding", "url": "https://mana.mozilla.org/wiki/pages/viewpage.action?pageId=55935392"}]	9	9	f	\N	\N	\N	You can change your W4 withholdings via Workday.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{withholding,tax,W4}	People	Josephine Leung	\N	\N
69	informational	Making Audio Calls	[{"name": "Jive", "url": "https://mana.mozilla.org/wiki/x/zSqxAw"}]	27	9	f	\N	\N	\N	Need to make business calls? Mozilla has a tool for you. 	2019-01-14 00:00:00	f	2019-01-15 00:38:17.758283	ALL	\N	{Calling,Telephone,audio}	IT: Service Desk	Mike Poessy	All	All
76	informational	Templates	[{"name": "Templates", "url": "https://docs.google.com/presentation/u/0/?ftv=1&tgif=d"}]	33	9	f	\N	\N	\N	Creating a presentation? Check out Mozilla templates. 	2019-01-15 00:00:00	f	2019-01-16 00:14:17.782452	ALL	\N	{templates,presentation,sheets,Google}	IT: Service Desk	Mike Poessy	All	All
16	best_practices	Getting Paid in Canada	[{"name": "Pay", "url": "https://mana.mozilla.org/wiki/display/PR/Getting+Paid+in+Canada"}]	12	9	f	\N	\N	\N	Where's my cash? Check out our payroll resources for Canada.	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	CA		{pay,payroll,CA,Canada}	People	Josephine Leung	\N	\N
17	best_practices	Benefits	""	13	9	f	\N	\N	\N	Have benefits questions? Email benefits@mozilla.com	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{benefits,insurance}	People	Josephine Leung	\N	\N
18	best_practices	How do I Change My Personal Information	[{"name": "Info", "url": "https://mana.mozilla.org/wiki/pages/viewpage.action?pageId=83788975"}]	16	9	f	\N	\N	\N	Workday is the place to change your personal information	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{personal,information}	People	Josephine Leung	\N	\N
19	best_practices	Mozilla Benefits	[{"name": "Benefits", "url": "https://mana.mozilla.org/wiki/display/PR/Mozilla+Benefits"}]	17	9	f	\N	\N	\N	We got benefits - check 'em out	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL		{benefits}	People	Josephine Leung	\N	\N
83	informational	Ask a security question	[]	36	9	f	\N	\N	\N	If you have a general question on security at Mozilla, email infosec@mozilla.com or join us in #infosec. (For possible security incidents, always report to foxsignal@mozilla.com)	2019-01-17 00:00:00	f	2019-01-17 20:48:42.963696	All	\N	{"security, question, infosec"}	IT: InfoSec	Tristan Weir	All	All
10	best_practices	Rating	[{"name": ":thumbsup:", "url": ":thumbsup:"}, {"name": ":thumbsdown:", "url": ":thumbsdown:"}]	7	12	t	2	week	5	How are we doing? Are we helping you adjust to Mozilla? \r\n button: :thumbsdown: \r\n\r\n button: :thumbsup:	2018-12-04 00:00:00	f	2018-12-19 20:40:33.793591	ALL	rating	{rating}	IT	Josephine Leung	\N	\N
84	deadline	Use MFA everywhere	[{"name": "Why use MFA?", "url": "https://infosec.mozilla.org/fundamentals/rationales.html#mfa"}]	37	9	f	\N	\N	\N	Multi-factor authentication (MFA) is one of the best ways to prevent account compromise. We require you to use Duo MFA on Mozilla Single Sign-On (SSO). Make sure to enable it on your Bugzilla, GitHub, and other important accounts, as well!	2019-01-17 00:00:00	f	2019-01-17 20:49:39.633826	All	\N	{"duo, mfa, security, account"}	IT: InfoSec	Tristan Weir	All	All
100	best_practices	US holidays	[{"name": "US holidays", "url": "https://mana.mozilla.org/wiki/display/PR/Holidays%3A+US"}]	38	9	f	\N	\N	\N	If you're in the United States, mark these holidays in your 2019 calendar!	2019-02-01 00:00:00	f	2019-02-01 22:25:38.572634	US	\N	{" paid_time_off"," vacation"," holiday"," holidays",pto}	IT: InfoSec	Jojo	All	All
70	best_practices	Data backup	[{"name": "Crashplan", "url": "https://mana.mozilla.org/wiki/x/GAQXAg"}]	28	9	f	\N	\N	\N	Is your data being backed up? Worried about data loss?	2019-02-01 00:00:00	f	2019-01-15 00:44:42.681759	All	\N	{restore,backup,back_up,security}	IT: Service Desk	Mike Poessy	All	All
82	informational	Report possible security incidents	[]	34	9	f	\N	\N	\N	Notice strange account activity? Get a suspicious email? Suspect a security incident? Email foxsignal@mozilla.com and someone from the Enterprise Information Security team will be paged, 24/7. 	2019-01-17 00:00:00	f	2019-01-17 17:49:26.015418	All	\N	{"security, report, security incident, suspicious"}	IT: InfoSec	Tristan Weir	All	All
15	best_practices	Getting Paid in the US	[{"name": "Pay", "url": "https://mana.mozilla.org/wiki/pages/viewpage.action?pageId=33099487"}]	12	9	f	\N	\N	\N	Where's my cash? Check out our payroll resources for the U.S.	2019-01-17 00:00:00	f	2018-12-19 20:40:33.793591	US		{pay,US,payroll}	People	Josephine Leung	All	All
\.


--
-- Data for Name: messages_to_send; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages_to_send (id, emp_id, message_id, send_dttm, send_order, send_status, cancel_status, last_updated, created_date) FROM stdin;
\.



--
-- Data for Name: user_feedback; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_feedback (id, action, emp_id, rating, comment, created_date) FROM stdin;
\.


--
-- Name: admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admin_id_seq', 199, true);


--
-- Name: admin_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.admin_roles_id_seq', 3, true);


--
-- Name: auth_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auth_groups_id_seq', 2082, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.messages_id_seq', 101, false);


--
-- Name: messages_to_send_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.messages_to_send_id_seq', 1, false);


--
-- Name: people_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.people_id_seq', 5295, true);


--
-- Name: user_feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_feedback_id_seq', 1, false);


--
-- Name: admin admin_emp_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_emp_id_key UNIQUE (emp_id);


--
-- Name: admin admin_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_pkey PRIMARY KEY (id);


--
-- Name: admin_roles admin_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_roles
    ADD CONSTRAINT admin_roles_pkey PRIMARY KEY (id);


--
-- Name: admin_roles admin_roles_role_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admin_roles
    ADD CONSTRAINT admin_roles_role_name_key UNIQUE (role_name);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: auth_groups auth_groups_groups_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_groups
    ADD CONSTRAINT auth_groups_groups_key UNIQUE (groups);


--
-- Name: auth_groups auth_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auth_groups
    ADD CONSTRAINT auth_groups_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: messages_to_send messages_to_send_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages_to_send
    ADD CONSTRAINT messages_to_send_pkey PRIMARY KEY (id);


--
-- Name: messages messages_topic_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_topic_key UNIQUE (topic);


--
-- Name: people people_emp_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_emp_id_key UNIQUE (emp_id);


--
-- Name: people people_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.people
    ADD CONSTRAINT people_pkey PRIMARY KEY (id);


--
-- Name: user_feedback user_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_feedback
    ADD CONSTRAINT user_feedback_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--
