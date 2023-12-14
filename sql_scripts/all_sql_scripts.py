# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 1 # # #
#
capture_account_from_info = """
                            SELECT account, 
                                   valid_to, 
                                   client 
                            FROM info.accounts a 
                            WHERE (REPLACE(TRIM(account), ' ', ''), COALESCE(update_dt, '1900-01-01')) IN (SELECT REPLACE(TRIM(account), ' ', ''), 
                                                                                                           max(COALESCE(update_dt, '1900-01-01'))
                                                                                                           FROM info.accounts 
                                                                                                           GROUP BY account)
							"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 2 # # #
#
capture_card_from_info = """
                            SELECT card_num, 
                                   account 
                            FROM info.cards c 
                            WHERE (REPLACE(TRIM(card_num), ' ', ''), COALESCE(update_dt, '1900-01-01')) IN (SELECT REPLACE(TRIM(card_num), ' ', ''), 
                                                                                                           max(COALESCE(update_dt, '1900-01-01'))
                                                                                                           FROM info.accounts 
                                                                                                           GROUP BY account)
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 3 # # #
#
capture_client_from_info = """
                            SELECT client_id, 
                                   last_name, 
                                   first_name, 
                                   patronymic, 
                                   date_of_birth, 
                                   passport_num, 
                                   passport_valid_to, 
                                   phone 
                            FROM info.clients c 
                            WHERE (client_id, COALESCE(update_dt, '1900-01-01')) IN (SELECT client_id, 
                                                                                     max(COALESCE(update_dt, '1900-01-01'))
                                                                                     FROM info.clients
                                                                                     GROUP BY client_id)
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 4 # # #
#
clear_stg_layer = """   
                            delete from deaise.goev_stg_accounts ;
                            delete from deaise.goev_stg_transactions ;
                            delete from deaise.goev_stg_clients ;
                            delete from deaise.goev_stg_cards ;
                            delete from deaise.goev_stg_passport_blacklist ;
                            delete from deaise.goev_stg_terminals ;
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 5 # # #
#
fill_goev_dwh_dim_accounts_hist = """
                            INSERT INTO deaise.goev_dwh_dim_accounts_hist(client, 
                                                                          valid_to, 
                                                                          account_num, 
                                                                          effective_from, 
                                                                          effective_to)
                            SELECT 
                                DISTINCT stg.client, 
                                stg.valid_to,
                                stg.account_num,
                                (SELECT max(trans_date::date) FROM deaise.goev_stg_transactions) AS effective_from, 
                                '9999-12-31'::date AS effective_to
                            FROM  deaise.goev_stg_accounts stg
                            LEFT JOIN deaise.goev_dwh_dim_accounts_hist tgt
                            ON stg.client = tgt.client
                            WHERE tgt.client IS NULL 
                                                  OR (concat(REPLACE(TRIM(stg.client), ' ', ''), 
                                                      REPLACE(TRIM(stg.account_num), ' ', ''),
                                                      stg.valid_to))
                                                       NOT IN  
                                                            (SELECT concat(REPLACE(TRIM(client), ' ', ''), 
                                                                  REPLACE(TRIM(account_num), ' ', ''),
                                                                  valid_to)
                                                             FROM deaise.goev_dwh_dim_accounts_hist
                                                             WHERE effective_to = '9999-12-31');
                            
                                                                             
                            UPDATE deaise.goev_dwh_dim_accounts_hist
                            SET deleted_flg = 1 
                                WHERE (concat(REPLACE(TRIM(client), ' ', ''), 
                                       REPLACE(TRIM(account_num), ' ', '')))  
                                       NOT IN 
                                            (SELECT concat(REPLACE(TRIM(client), ' ', ''), 
                                                    REPLACE(TRIM(account_num), ' ', ''))
                                             FROM deaise.goev_stg_accounts) 
                                       AND effective_to = '9999-12-31';
                            
                            UPDATE deaise.goev_dwh_dim_accounts_hist
                            SET deleted_flg = 0 
                                WHERE (concat(REPLACE(TRIM(client), ' ', ''), 
                                       REPLACE(TRIM(account_num), ' ', '')))  
                                       IN 
                                            (SELECT concat(REPLACE(TRIM(client), ' ', ''), 
                                                    REPLACE(TRIM(account_num), ' ', ''))
                                             FROM deaise.goev_stg_accounts) 
                                       AND effective_to = '9999-12-31';
                                
                            UPDATE deaise.goev_dwh_dim_accounts_hist
                            SET effective_to = (SELECT DISTINCT(max(effective_from))
                                                FROM deaise.goev_dwh_dim_accounts_hist
                                                WHERE effective_to = '9999-12-31'
                                                GROUP BY concat(REPLACE(TRIM(client), ' ', ''), 
                                                         REPLACE(TRIM(account_num), ' ', ''))
                                                HAVING count(concat(REPLACE(TRIM(client), ' ', ''), 
                                                                    REPLACE(TRIM(account_num), ' ', ''))) > 1) - INTERVAL '1 sec'
                            WHERE (concat(REPLACE(TRIM(client), ' ', ''), 
                                   REPLACE(TRIM(account_num), ' ', '')), 
                                   effective_from) IN (SELECT concat(REPLACE(TRIM(client), ' ', ''), 
                                                                     REPLACE(TRIM(account_num), ' ', '')), 
                                                                     min(effective_from)
                                                       FROM deaise.goev_dwh_dim_accounts_hist
                                                       WHERE effective_to = '9999-12-31'
                                                       GROUP BY client, account_num
                                                       HAVING count(*) > 1);
                            
                            INSERT INTO deaise.goev_meta_dwh (schema_name, table_name, update_dt, file_dt)
                            VALUES ('deaise', 'goev_dwh_dim_accounts_hist', now(), (SELECT max(trans_date::date) FROM deaise.goev_stg_transactions));
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 6 # # #
#
fill_goev_dwh_dim_cards = """
                            INSERT INTO deaise.goev_dwh_dim_cards(account_num, card_num)
                            SELECT 
                                DISTINCT REPLACE(TRIM(stg.account_num), ' ', ''), 
                                REPLACE(TRIM(stg.card_num), ' ', '')
                            FROM  deaise.goev_stg_cards stg
                            LEFT JOIN deaise.goev_dwh_dim_cards tgt
                            ON stg.account_num = tgt.account_num 
                            WHERE tgt.account_num IS NULL
                                                  OR concat(REPLACE(TRIM(stg.account_num), ' ', ''), REPLACE(TRIM(stg.card_num), ' ', '')) NOT IN  
                                                          (SELECT concat(REPLACE(TRIM(account_num), ' ', ''), REPLACE(TRIM(card_num), ' ', ''))
                                                          FROM deaise.goev_dwh_dim_cards);
                            
                            UPDATE deaise.goev_dwh_dim_cards
                            SET deleted_flg = 1 
                            WHERE (account_num, card_num) NOT IN (SELECT REPLACE(TRIM(account_num), ' ', '') AS account_num, 
                                                                         REPLACE(TRIM(card_num), ' ', '') AS card_num
                                                                  FROM deaise.goev_stg_cards);
                            
                            UPDATE deaise.goev_dwh_dim_cards  
                            SET deleted_flg = 0 
                                WHERE (account_num, card_num) IN (SELECT REPLACE(TRIM(account_num), ' ', '') AS account_num, 
                                                                         REPLACE(TRIM(card_num), ' ', '') AS card_num
                                                                  FROM deaise.goev_stg_cards) 
                                AND deleted_flg = 1;
                                
                            
                            INSERT INTO deaise.goev_meta_dwh (schema_name, table_name, update_dt, file_dt)
                            VALUES ('deaise', 'goev_dwh_dim_cards', now(), (SELECT max(trans_date::date) FROM deaise.goev_stg_transactions)); 
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 7 # # #
#
fill_goev_dwh_dim_clients_hist = """
                            INSERT INTO deaise.goev_dwh_dim_clients_hist (client_id, 
                                                                          last_name, 
                                                                          first_name, 
                                                                          patronymic, 
                                                                          date_of_birth, 
                                                                          passport_num, 
                                                                          passport_valid_to, 
                                                                          phone, 
                                                                          effective_from, 
                                                                          effective_to)
                            SELECT 
                                DISTINCT stg.client_id, 
                                stg.last_name,
                                stg.first_name,
                                stg.patronymic,
                                stg.date_of_birth,
                                stg.passport_num,
                                stg.passport_valid_to,
                                stg.phone,
                                (SELECT max(trans_date::date) FROM deaise.goev_stg_transactions) AS effective_from,
                                '9999-12-31'::date AS effective_to
                            FROM  deaise.goev_stg_clients stg
                            LEFT JOIN deaise.goev_dwh_dim_clients_hist tgt
                            ON stg.client_id = tgt.client_id 
                            WHERE tgt.client_id IS NULL 
                                                  OR (lower(
                                                            concat(
                                                              REPLACE(TRIM(stg.client_id), ' ', ''), 
                                                              REPLACE(TRIM(stg.last_name), ' ', ''),
                                                              REPLACE(TRIM(stg.first_name), ' ', ''),
                                                              REPLACE(TRIM(stg.patronymic), ' ', ''),
                                                              REPLACE(TRIM(stg.passport_num), ' ', ''),
                                                              REPLACE(TRIM(stg.phone), ' ', ''),
                                                              stg.passport_valid_to,
                                                              stg.date_of_birth
                                                                  ) 
                                                              ))
                                                       NOT IN  
                                                            (SELECT lower(
                                                                        concat(
                                                                          REPLACE(TRIM(client_id), ' ', ''), 
                                                                          REPLACE(TRIM(last_name), ' ', ''),
                                                                          REPLACE(TRIM(first_name), ' ', ''),
                                                                          REPLACE(TRIM(patronymic), ' ', ''),
                                                                          REPLACE(TRIM(passport_num), ' ', ''),
                                                                          REPLACE(TRIM(phone), ' ', ''),
                                                                          passport_valid_to,
                                                                          date_of_birth
                                                                              ) 
                                                                          )
                                                             FROM deaise.goev_dwh_dim_clients_hist
                                                             WHERE effective_to = '9999-12-31');
                            
                            
                                                                             
                            UPDATE deaise.goev_dwh_dim_clients_hist
                            SET deleted_flg = 1 
                                WHERE REPLACE(TRIM(client_id), ' ', '')
                                   NOT IN 
                                        (SELECT REPLACE(TRIM(client_id), ' ', '')
                                         FROM deaise.goev_stg_clients) 
                               AND effective_to = '9999-12-31';
                            
                            UPDATE deaise.goev_dwh_dim_clients_hist
                            SET deleted_flg = 0 
                                WHERE REPLACE(TRIM(client_id), ' ', '')
                                   IN 
                                        (SELECT REPLACE(TRIM(client_id), ' ', '')
                                         FROM deaise.goev_stg_clients) 
                               AND effective_to = '9999-12-31';
                                
                            UPDATE deaise.goev_dwh_dim_clients_hist
                            SET effective_to = (SELECT DISTINCT(max(effective_from))
                                                FROM deaise.goev_dwh_dim_clients_hist
                                                WHERE effective_to = '9999-12-31'
                                                GROUP BY REPLACE(TRIM(client_id), ' ', '')
                                                HAVING count(REPLACE(TRIM(client_id), ' ', '')) > 1) - INTERVAL '1 sec'
                            WHERE (REPLACE(TRIM(client_id), ' ', ''), 
                                   effective_from) IN (SELECT REPLACE(TRIM(client_id), ' ', ''), 
                                                                     min(effective_from)
                                                       FROM deaise.goev_dwh_dim_clients_hist
                                                       WHERE effective_to = '9999-12-31'
                                                       GROUP BY client_id
                                                       HAVING count(last_name) > 1);
                            
                            INSERT INTO deaise.goev_meta_dwh (schema_name, table_name, update_dt, file_dt)
                            VALUES ('deaise', 'goev_dwh_dim_clients_hist', now(), (SELECT max(trans_date::date) FROM deaise.goev_stg_transactions)); 
                            
                           """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 8 # # #
#
fill_goev_dwh_dim_terminals_hist = """
                            INSERT INTO deaise.goev_dwh_dim_terminals_hist(terminal_id, terminal_type, terminal_city, terminal_address, effective_from, effective_to)
                            SELECT
                                DISTINCT stg.terminal_id,
                                stg.terminal_type,
                                stg.terminal_city,
                                stg.terminal_address,
                                (SELECT max(trans_date::date) FROM deaise.goev_stg_transactions) AS effective_from,
                                '9999-12-31'::date AS effective_to
                            FROM  deaise.goev_stg_terminals stg
                            LEFT JOIN deaise.goev_dwh_dim_terminals_hist tgt
                            ON stg.terminal_id = tgt.terminal_id
                            WHERE tgt.terminal_id IS NULL
                                                  OR lower(concat(stg.terminal_id, stg.terminal_type, stg.terminal_address, stg.terminal_city)) NOT IN
                                                          (SELECT lower(concat(terminal_id, terminal_type, terminal_address, terminal_city))
                                                          FROM deaise.goev_dwh_dim_terminals_hist
                                                          WHERE effective_to = '9999-12-31');
                            
                            UPDATE deaise.goev_dwh_dim_terminals_hist
                            SET deleted_flg = 1
                                WHERE terminal_id NOT IN (SELECT DISTINCT terminal_id
                                                          FROM deaise.goev_stg_terminals)
                                                  AND effective_to = '9999-12-31';
                            
                            UPDATE deaise.goev_dwh_dim_terminals_hist
                            SET deleted_flg = 0
                                WHERE terminal_id IN (SELECT DISTINCT terminal_id
                                                      FROM deaise.goev_stg_terminals)
                                                  AND deleted_flg = 1;
                            
                            UPDATE deaise.goev_dwh_dim_terminals_hist
                            SET effective_to = (SELECT DISTINCT(max(effective_from))
                                                FROM deaise.goev_dwh_dim_terminals_hist
                                                WHERE effective_to = '9999-12-31'
                                                GROUP BY terminal_id
                                                HAVING count(terminal_id) > 1) - INTERVAL '1 day'
                            WHERE (terminal_id, effective_from) IN (SELECT terminal_id, min(effective_from)
                                                                    FROM deaise.goev_dwh_dim_terminals_hist
                                                                    WHERE effective_to = '9999-12-31'
                                                                    GROUP BY terminal_id
                                                                    HAVING count(terminal_id) > 1);
                                                                    
                            INSERT INTO deaise.goev_meta_dwh (schema_name, table_name, update_dt, file_dt)
                            VALUES ('deaise', 'goev_dwh_dim_terminals_hist', now(), (SELECT max(trans_date::date) FROM deaise.goev_stg_transactions));  
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 9 # # #
#
fill_goev_dwh_fact_passport_blacklist = """
                            delete from goev_dwh_fact_passport_blacklist;
                            insert into goev_dwh_fact_passport_blacklist 
                            select passport_num, entry_dt 
                            from goev_stg_passport_blacklist
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 10 # # #
#
fill_goev_dwh_fact_transaction = """
                            delete from goev_dwh_fact_transactions;
                            insert into goev_dwh_fact_transactions 
                            select * 
                            from goev_stg_transactions
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 11 # # #
#
add_to_report_event_1 = """
                            INSERT INTO goev_rep_fraud
                            WITH not_clnt AS (
                                SELECT client_id,
                                       concat(last_name, ' ', first_name,' ',patronymic) AS fio,
                                       passport_num,
                                       phone
                                FROM deaise.goev_dwh_dim_clients_hist
                                WHERE passport_num IN (SELECT passport_num FROM goev_dwh_fact_passport_blacklist)
                                      OR passport_valid_to < (SELECT max(trans_date::date) FROM deaise.goev_dwh_fact_transactions)
                                      AND effective_to = '9999-12-31'
                                            ),
                                 card_evnt AS ( 			
                                SELECT c.card_num, client_id 
                                FROM not_clnt cl
                                LEFT JOIN goev_dwh_dim_accounts_hist ac ON ac.client = cl.client_id
                                LEFT JOIN goev_dwh_dim_cards c ON (REPLACE(TRIM(c.account_num), ' ', '')) = (REPLACE(TRIM(ac.account_num), ' ', ''))
                                WHERE effective_to = '9999-12-31'
                                GROUP BY card_num, client_id
                                              ), 
                                events AS (
                                SELECT trans_date AS event_dt,
                                       passport_num AS passport,
                                       fio,
                                       phone,
                                       1 AS event_type,
                                       (SELECT max(trans_date::date) FROM deaise.goev_dwh_fact_transactions) AS report_dt
                                FROM card_evnt ce
                                LEFT JOIN deaise.goev_dwh_fact_transactions tr ON (REPLACE(TRIM(ce.card_num), ' ', '')) = (REPLACE(TRIM(tr.card_num), ' ', ''))
                                LEFT JOIN not_clnt nc ON nc.client_id  = ce.client_id 
                                         )
                            SELECT event_dt::time AS event_dt, passport, fio, phone, 1 AS event_type, report_dt
                            FROM events;
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 12 # # #
#
add_to_report_event_2 = """ 
                            INSERT INTO goev_rep_fraud
                            SELECT trans_date::time AS event_dt,
                                   passport_num AS passport,
                                   concat(last_name,' ', first_name, ' ', patronymic) AS fio,
                                   phone, 
                                   2 AS event_type,
                                   (SELECT max(trans_date::date) FROM deaise.goev_dwh_fact_transactions) AS report_dt
                            FROM deaise.goev_dwh_dim_accounts_hist ac
                            LEFT JOIN deaise.goev_dwh_dim_clients_hist cl ON ac.client = cl.client_id
                            LEFT JOIN goev_dwh_dim_cards c ON (REPLACE(TRIM(c.account_num), ' ', '')) = (REPLACE(TRIM(ac.account_num), ' ', ''))
                            LEFT JOIN deaise.goev_dwh_fact_transactions tr ON (REPLACE(TRIM(c.card_num), ' ', '')) = (REPLACE(TRIM(tr.card_num), ' ', ''))
                            WHERE valid_to < (SELECT max(trans_date::date) FROM deaise.goev_dwh_fact_transactions) 
                                 AND ac.effective_to = '9999-12-31';
	                        """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 13 # # #
#
add_to_report_event_3 = """
                            INSERT INTO goev_rep_fraud
                            WITH evnt AS (
                                SELECT  trans_id,
                                        client,
                                        trans_date,
                                        COALESCE (LAG(trans_date) OVER(PARTITION BY client ORDER BY trans_date), trans_date) AS prev_date,
                                        COALESCE (LEAD(trans_date) OVER(PARTITION BY client ORDER BY trans_date), trans_date) AS next_date,
                                        terminal_city,
                                        COALESCE (LAG(terminal_city) OVER(PARTITION BY client ORDER BY trans_date), terminal_city) AS prev_city,
                                        COALESCE (LEAD(terminal_city) OVER(PARTITION BY client ORDER BY trans_date), terminal_city) AS next_city
                                FROM goev_dwh_fact_transactions tt
                                LEFT JOIN deaise.goev_dwh_dim_terminals_hist tr ON tr.terminal_id = tt.terminal
                                LEFT JOIN goev_dwh_dim_cards gddc ON (REPLACE(TRIM(tt.card_num), ' ', '')) = (REPLACE(TRIM(gddc.card_num), ' ', ''))
                                LEFT JOIN goev_dwh_dim_accounts_hist gddah ON (REPLACE(TRIM(gddc.account_num), ' ', '')) = (REPLACE(TRIM(gddah.account_num), ' ', ''))
                                WHERE  oper_type IN ('WITHDRAW', 'PAYMENT')
                                ORDER BY client, trans_date
                                          )
                            SELECT trans_date::time AS event_dt,
                                   passport_num AS passport,
                                   concat(last_name,' ', first_name, ' ', patronymic) AS fio,
                                   phone,
                                   3 AS event_type,
                                   (SELECT max(trans_date::date) FROM goev_dwh_fact_transactions) AS report_dt
                            FROM evnt
                            LEFT JOIN deaise.goev_dwh_dim_clients_hist cl ON evnt.client = cl.client_id
                            WHERE (prev_city <> terminal_city AND (trans_date - prev_date) < INTERVAL '60 min') AND prev_city = next_city
                            """

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # 13 # # #
#
add_to_report_event_4 = """
                            INSERT INTO goev_rep_fraud
                            WITH trnsct_dtls AS (
                                SELECT 
                                    trans_date, 
                                    client,  
                                    oper_result,
                                    LAG(oper_result) OVER(PARTITION BY client ORDER BY trans_date) prev_result,
                                    LAG(oper_result, 2) OVER(PARTITION BY client ORDER BY trans_date) prev_result_2,
                                    LAG(oper_result, 3) OVER(PARTITION BY client ORDER BY trans_date) prev_result_3,
                                    amt,
                                    LAG(amt) OVER(PARTITION BY client ORDER BY trans_date) prev_amt,
                                    LAG(amt, 2) OVER(PARTITION BY client ORDER BY trans_date) prev_amt_2,
                                    LAG(amt, 3) OVER(PARTITION BY client ORDER BY trans_date) prev_amt_3,
                                    LAG(trans_date, 3) OVER(PARTITION BY client ORDER BY trans_date) prev_time
                                FROM goev_dwh_fact_transactions gdft
                                LEFT JOIN goev_dwh_dim_cards gddc ON (REPLACE(TRIM(gdft.card_num), ' ', '')) = (REPLACE(TRIM(gddc.card_num), ' ', ''))
                                LEFT JOIN goev_dwh_dim_accounts_hist gddah ON (REPLACE(TRIM(gddc.account_num), ' ', '')) = (REPLACE(TRIM(gddah.account_num), ' ', ''))
                                WHERE  oper_type IN ('WITHDRAW', 'PAYMENT')
                                ORDER BY client, trans_date
                                        ),
                            evnts AS (
                                SELECT * 
                                FROM trnsct_dtls
                                WHERE prev_result_3 = 'REJECT' 
                                AND prev_result_2 = 'REJECT' 
                                AND prev_result = 'REJECT' 
                                AND oper_result = 'SUCCESS'
                                AND prev_amt_3 > prev_amt_2
                                AND prev_amt_2 > prev_amt
                                AND prev_amt_2 > amt
                                AND (trans_date - prev_time) <= INTERVAL '20 min'
                                        )
                            SELECT trans_date::time AS event_dt,
                                   passport_num AS passport,
                                   concat(last_name,' ', first_name, ' ', patronymic) AS fio,
                                   phone,
                                   4 AS event_type,
                                   (SELECT max(trans_date::date) FROM goev_dwh_fact_transactions) AS report_dt
                            FROM evnts 
                            LEFT JOIN deaise.goev_dwh_dim_clients_hist cl ON evnts.client = cl.client_id 
                            """
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # _____________ # # #
#
