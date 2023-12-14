--######################################################################################

-- Making the stage layer

--######################################################################################

-- step 1 -- Creating tables


--1
CREATE TABLE IF NOT EXISTS goev_stg_terminals (
terminal_id varchar,
terminal_type varchar,
terminal_city varchar,
terminal_address varchar
);

--2
CREATE TABLE IF NOT EXISTS goev_stg_clients (
client_id varchar,
last_name varchar,
first_name varchar,
patronymic varchar,
date_of_birth date,
passport_num varchar,
passport_valid_to date,
phone varchar
);

--3
CREATE TABLE IF NOT EXISTS goev_stg_accounts (
account_num varchar,
valid_to date,
client varchar
);


--4
CREATE TABLE IF NOT EXISTS goev_stg_cards (
card_num varchar,
account_num varchar
);

--5
CREATE TABLE IF NOT EXISTS goev_stg_passport_blacklist (
passport_num varchar,
entry_dt date
);

--6
CREATE TABLE IF NOT EXISTS goev_stg_transactions(
trans_id varchar,
trans_date timestamp,
card_num varchar,
oper_type varchar,
amt decimal,
oper_result varchar,
terminal varchar
);


--######################################################################################

-- Making the DWH layer

--######################################################################################

-- step 1 -- creating fact's tables

--1
CREATE TABLE IF NOT EXISTS goev_dwh_fact_transactions (
trans_id varchar,
trans_date timestamp,
card_num varchar,
oper_type varchar,
amt decimal,
oper_result varchar,
terminal varchar
);

--2
CREATE TABLE IF NOT EXISTS goev_dwh_fact_passport_blacklist (
passport_num varchar,
entry_dt date
);

-- step 2 -- creating dim's tables

--3
CREATE TABLE IF NOT EXISTS goev_dwh_dim_terminals_hist (
terminal_id varchar,
terminal_type varchar,
terminal_city varchar,
terminal_address varchar,
effective_from date,
effective_to date,
deleted_flg int DEFAULT 0);

--4
CREATE TABLE IF NOT EXISTS goev_dwh_dim_cards (
card_num varchar,
account_num varchar,
deleted_flg int DEFAULT 0);

--5
CREATE TABLE IF NOT EXISTS goev_dwh_dim_accounts_hist (
account_num varchar,
valid_to date,
client varchar,
effective_from date,
effective_to date,
deleted_flg int DEFAULT 0
);

--6
CREATE TABLE IF NOT EXISTS goev_dwh_dim_clients_hist (
client_id varchar,
last_name varchar,
first_name varchar,
patronymic varchar,
date_of_birth date,
passport_num varchar,
passport_valid_to date,
phone varchar,
effective_from date,
effective_to date,
deleted_flg int DEFAULT 0
);

-- step 3 -- creating meta table

CREATE TABLE IF NOT EXISTS deaise.goev_meta_dwh(
schema_name varchar(30),
table_name varchar(30),
update_dt timestamp,
file_dt date
);

--######################################################################################

-- Creating the report

--######################################################################################

CREATE TABLE IF NOT EXISTS goev_rep_fraud (
event_dt timestamp,
passport varchar,
fio varchar,
phone varchar,
event_type int,
report_dt date
);


--######################################################################################

--in case of checking up

--######################################################################################

--DELETE from goev_stg_accounts;
--DELETE from goev_stg_transactions;
--DELETE from goev_stg_clients;
--DELETE from goev_stg_cards;
--DELETE from goev_stg_passport_blacklist;
--DELETE from goev_stg_terminals;
--
--DROP table goev_stg_accounts;
--DROP table goev_stg_transactions;
--DROP table goev_stg_clients;
--DROP table goev_stg_cards;
--DROP table goev_stg_passport_blacklist;
--DROP table goev_stg_terminals;
--
--
--DELETE FROM goev_dwh_dim_terminals_hist;
--DELETE FROM goev_dwh_dim_clients_hist;
--DELETE FROM goev_dwh_dim_accounts_hist;
--DELETE FROM goev_dwh_dim_cards;
--DELETE FROM goev_dwh_fact_passport_blacklist;
--DELETE FROM goev_dwh_fact_transactions;
--
--DROP table goev_dwh_dim_terminals_hist;
--DROP table goev_dwh_dim_clients_hist;
--DROP table goev_dwh_dim_accounts_hist;
--DROP table goev_dwh_dim_cards;
--DROP table goev_dwh_fact_passport_blacklist;
--DROP table goev_dwh_fact_transactions;
--DROP table goev_rep_fraud;
--DROP table deaise.goev_meta_dwh;
--
--SELECT * FROM goev_dwh_dim_terminals_hist;
--SELECT * FROM goev_dwh_dim_clients_hist;
--SELECT * FROM goev_dwh_dim_accounts_hist;
--SELECT * FROM goev_dwh_dim_cards;
--SELECT * FROM goev_dwh_fact_passport_blacklist;
--SELECT * FROM goev_dwh_fact_transactions;
--SELECT * FROM deaise.goev_meta_dwh;

