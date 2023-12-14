
SELECT card_num, account
FROM info.cards c
WHERE (REPLACE(TRIM(card_num), ' ', ''), COALESCE(update_dt, '1900-01-01')) IN (SELECT REPLACE(TRIM(card_num), ' ', ''),
                                                                               max(COALESCE(update_dt, '1900-01-01'))
                                                                               FROM info.accounts
                                                                               GROUP BY account)

