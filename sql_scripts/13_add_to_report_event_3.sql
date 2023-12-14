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

