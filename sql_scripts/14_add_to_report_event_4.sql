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
	FROM goev_stg_transactions_tests gdft
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
SELECT trans_date AS event_dt,
	   passport_num AS passport,
	   concat(last_name,' ', first_name, ' ', patronymic) AS fio,
	   phone,
	   4 AS event_type,
	   (SELECT max(trans_date::date) FROM goev_stg_transactions_tests) AS report_dt
FROM evnts
LEFT JOIN deaise.goev_dwh_dim_clients_hist cl ON evnts.client = cl.client_id
