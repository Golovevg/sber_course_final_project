
SELECT account,
       valid_to,
       client
FROM info.accounts a
WHERE (REPLACE(TRIM(account), ' ', ''), COALESCE(update_dt, '1900-01-01')) IN (SELECT REPLACE(TRIM(account), ' ', ''),
                                                                               max(COALESCE(update_dt, '1900-01-01'))
                                                                               FROM info.accounts
                                                                               GROUP BY account)

