# fill_goev_dwh_dim_clients_hist

goev_dwh_dim_clients_hist = """
INSERT INTO deaise.goev_dwh_dim_clients_hist_(client_id, 
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
	now()AS effective_from, --have to be reblaced by the date extraxted from the file name  
	'9999-12-31'::date AS effective_to
FROM  deaise.goev_stg_clients stg
LEFT JOIN deaise.goev_dwh_dim_clients_hist_ tgt
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
                                 FROM deaise.goev_dwh_dim_clients_hist_
                                 WHERE effective_to = '9999-12-31');


                                                 
UPDATE deaise.goev_dwh_dim_clients_hist_
SET deleted_flg = 1 
    WHERE REPLACE(TRIM(client_id), ' ', '')
	   NOT IN 
	   		(SELECT REPLACE(TRIM(client_id), ' ', '')
	         FROM deaise.goev_stg_clients) 
   AND effective_to = '9999-12-31';

UPDATE deaise.goev_dwh_dim_clients_hist_
SET deleted_flg = 0 
    WHERE REPLACE(TRIM(client_id), ' ', '')
	   IN 
	   		(SELECT REPLACE(TRIM(client_id), ' ', '')
	         FROM deaise.goev_stg_clients) 
   AND effective_to = '9999-12-31';
    
UPDATE deaise.goev_dwh_dim_clients_hist_
SET effective_to = (SELECT DISTINCT(max(effective_from))
                    FROM deaise.goev_dwh_dim_clients_hist_
                    WHERE effective_to = '9999-12-31'
                    GROUP BY REPLACE(TRIM(client_id), ' ', '')
                    HAVING count(REPLACE(TRIM(client_id), ' ', '')) > 1) - INTERVAL '1 sec'
WHERE (REPLACE(TRIM(client_id), ' ', ''), 
	   effective_from) IN (SELECT REPLACE(TRIM(client_id), ' ', ''), 
		  								 min(effective_from)
                           FROM deaise.goev_dwh_dim_clients_hist_
                           WHERE effective_to = '9999-12-31'
                           GROUP BY client_id
                           HAVING count(last_name) > 1);

INSERT INTO deaise.goev_meta_dwh (schema_name, table_name, update_dt, file_dt)
VALUES ('deaise', 'goev_dwh_dim_accounts_hist', now()::date, now());  -- have to be added date of file;

"""
