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
SELECT min(event_dt) AS event_dt, passport, fio, phone, 1 AS event_type, report_dt
FROM events
GROUP BY passport, fio, phone, report_dt;



