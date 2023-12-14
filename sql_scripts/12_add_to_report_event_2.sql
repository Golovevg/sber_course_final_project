INSERT INTO goev_rep_fraud
SELECT min(trans_date) AS event_dt,
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
	 AND ac.effective_to = '9999-12-31'
GROUP BY passport_num, concat(last_name,' ', first_name, ' ', patronymic), phone;
