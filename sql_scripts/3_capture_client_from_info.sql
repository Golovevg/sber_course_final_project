
SELECT client_id,
       last_name,
       first_name,
       patronymic,
       date_of_birth,
       passport_num,
       passport_valid_to,
       phone
FROM info.clients c
WHERE (client_id, COALESCE(update_dt, '1900-01-01')) IN (SELECT client_id,
                                                         max(COALESCE(update_dt, '1900-01-01'))
                                                         FROM info.clients
                                                         GROUP BY client_id)

