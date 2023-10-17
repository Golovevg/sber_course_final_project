#fill_goev_dwh_dim_accounts_hist

goev_dwh_dim_accounts_hist = """
INSERT INTO deaise.goev_dwh_dim_accounts_hist_(client, valid_to, account_num, effective_from, effective_to)
SELECT 
	DISTINCT stg.client, 
	stg.valid_to,
	stg.account_num,
	now()AS effective_from, --have to be reblaced by the date extraxted from the file name  
	'9999-12-31'::date AS effective_to
FROM  deaise.goev_stg_accounts stg
LEFT JOIN deaise.goev_dwh_dim_accounts_hist_ tgt
ON stg.client = tgt.client
WHERE tgt.client IS NULL 
					  OR (concat(REPLACE(TRIM(stg.client), ' ', ''), 
					      REPLACE(TRIM(stg.account_num), ' ', ''),
					      stg.valid_to))
                           NOT IN  
                           		(SELECT concat(REPLACE(TRIM(client), ' ', ''), 
                                      REPLACE(TRIM(account_num), ' ', ''),
                                      valid_to)
                                 FROM deaise.goev_dwh_dim_accounts_hist_
                                 WHERE effective_to = '9999-12-31');

                                                 
UPDATE deaise.goev_dwh_dim_accounts_hist_
SET deleted_flg = 1 
    WHERE (concat(REPLACE(TRIM(client), ' ', ''), 
		   REPLACE(TRIM(account_num), ' ', '')))  
		   NOT IN 
		   		(SELECT concat(REPLACE(TRIM(client), ' ', ''), 
                        REPLACE(TRIM(account_num), ' ', ''))
                 FROM deaise.goev_stg_accounts) 
   		   AND effective_to = '9999-12-31';

UPDATE deaise.goev_dwh_dim_accounts_hist_
SET deleted_flg = 0 
    WHERE (concat(REPLACE(TRIM(client), ' ', ''), 
		   REPLACE(TRIM(account_num), ' ', '')))  
		   IN 
		   		(SELECT concat(REPLACE(TRIM(client), ' ', ''), 
                        REPLACE(TRIM(account_num), ' ', ''))
                 FROM deaise.goev_stg_accounts) 
   		   AND effective_to = '9999-12-31';
    
UPDATE deaise.goev_dwh_dim_accounts_hist_
SET effective_to = (SELECT DISTINCT(max(effective_from))
                    FROM deaise.goev_dwh_dim_accounts_hist_
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
                           FROM deaise.goev_dwh_dim_accounts_hist_
                           WHERE effective_to = '9999-12-31'
                           GROUP BY client, account_num
                           HAVING count(*) > 1);

INSERT INTO deaise.goev_meta_dwh (schema_name, table_name, update_dt, file_dt)
VALUES ('deaise', 'goev_dwh_dim_accounts_hist', now()::date, now());  -- have to be added date of file;
"""
