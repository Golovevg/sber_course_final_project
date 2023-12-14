-- This SQL statement inserts data from the staging table into the historical terminals dimension table.
-- It selects distinct records based on terminal_id, terminal_type, terminal_city, and terminal_address.
-- The effective_from date will be replaced by the date extracted from the file name.
-- The effective_to date is set to '9999-12-31'.

INSERT INTO deaise.goev_dwh_dim_terminals_hist(terminal_id, terminal_type, terminal_city, terminal_address, effective_from, effective_to)
SELECT
    DISTINCT stg.terminal_id,
    stg.terminal_type,
    stg.terminal_city,
    stg.terminal_address,
    (SELECT max(trans_date::date) FROM deaise.goev_dwh_fact_transactions) AS effective_from,
    '9999-12-31'::date AS effective_to
FROM  deaise.goev_stg_terminals stg
LEFT JOIN deaise.goev_dwh_dim_terminals_hist tgt
ON stg.terminal_id = tgt.terminal_id
WHERE tgt.terminal_id IS NULL
                      OR lower(concat(stg.terminal_id, stg.terminal_type, stg.terminal_address, stg.terminal_city)) NOT IN
                              (SELECT lower(concat(terminal_id, terminal_type, terminal_address, terminal_city))
                              FROM deaise.goev_dwh_dim_terminals_hist
                              WHERE effective_to = '9999-12-31');

-- Update records in the historical terminals dimension table with deleted_flg set to 1.
-- This is done for records in the dimension table that do not have a corresponding entry in the staging table.
UPDATE deaise.goev_dwh_dim_terminals_hist
SET deleted_flg = 1
    WHERE terminal_id NOT IN (SELECT DISTINCT terminal_id
                              FROM deaise.goev_stg_terminals)
                      AND effective_to = '9999-12-31';

-- Update records in the historical terminals dimension table with deleted_flg set to 0.
-- This is done for records in the dimension table that have a corresponding entry in the staging table and had deleted_flg set to 1.
UPDATE deaise.goev_dwh_dim_terminals_hist
SET deleted_flg = 0
    WHERE terminal_id IN (SELECT DISTINCT terminal_id
                          FROM deaise.goev_stg_terminals)
                      AND deleted_flg = 1;

-- Update effective_to dates in the historical terminals dimension table for records with multiple entries.
-- The effective_to date is set to the maximum effective_from date of the duplicate records minus 1 day.
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
VALUES ('deaise', 'goev_dwh_dim_terminals_hist', now()::date, (SELECT max(trans_date::date) FROM deaise.goev_dwh_fact_transactions));

