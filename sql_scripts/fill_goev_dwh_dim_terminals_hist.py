# fill_goev_dwh_dim_terminals_hist

fill_goev_dwh_dim_terminals_hist = """
INSERT INTO deaise.goev_dwh_dim_terminals_hist(terminal_id, terminal_type, terminal_city, terminal_address, effective_from, effective_to)
SELECT
	DISTINCT stg.terminal_id,
	stg.terminal_type,
	stg.terminal_city,
	stg.terminal_address,
	now()AS effective_from, --have to be reblaced by the date extraxted from the file name
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
                    HAVING count(terminal_id) > 1) - INTERVAL '1 sec'
WHERE (terminal_id, effective_from) IN (SELECT terminal_id, min(effective_from)
                                        FROM deaise.goev_dwh_dim_terminals_hist
                                        WHERE effective_to = '9999-12-31'
                                        GROUP BY terminal_id
                                        HAVING count(terminal_id) > 1);
                                        
INSERT INTO deaise.goev_meta_dwh (schema_name, table_name, update_dt, file_dt)
VALUES ('deaise', 'goev_dwh_dim_terminals_hist', now()::date, now());  -- have to be added date of file;
"""
