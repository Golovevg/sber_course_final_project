# clear_stg_layer

clear_stg_layer = """ delete from goev_stg_accounts ;
                delete from goev_stg_transactions ;
                delete from goev_stg_clients ;
                delete from goev_stg_cards ;
                delete from goev_stg_passport_blacklist ;
                delete from goev_stg_terminals ;"""
