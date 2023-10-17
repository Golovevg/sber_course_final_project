# fill_goev_dwh_dim_cards

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
VALUES ('deaise', 'goev_dwh_dim_cards', now()::date, now());  -- have to be added date of file;
"""
