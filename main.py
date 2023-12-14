from credentials.bank_credentials import cursor as bank_cursor
import time
from sql_scripts.all_sql_scripts import *
from py_scripts.functions import *

start_time = time.time()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # Checking the data in the data_files # # #
check_entirety()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # Creating a list of files in the data_files # # #
transactions_list, passport_blacklist_list, terminals_list, unknown_list = files_list()
print('We have files for download:\n', ' ')
for i in files_list():
    for j in i:
        print(j)

# # # In case when we have more than 1 file in data_files for each entity

for i in range(len(terminals_list)):
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # Clearing staging layer # # #
    execute_sgl(edu_cursor, clear_stg_layer, '\n''Staging layer has been successfully cleaned \n''')

    edu_conn_commit(success_msg='Transaction Committed\n''_______________________________________________________')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # Downloading data from the sources to the staging tables and updating the dwh layer # # #
    #
    # transactions
    # # # 1. goev_stg_transactions
    transactions = pd.read_csv(f'data_files/{transactions_list[i]}', engine='python', delimiter=';', decimal=',')
    transactions_stg_insert = "INSERT INTO deaise.goev_stg_transactions(trans_id, trans_date, amt, card_num, oper_type, oper_result, terminal)"
    insert_stg(transactions, transactions_stg_insert, "TRANSACTIONS", "1. Data has been added to goev_stg_transactions")
    #
    # clients
    # # # 2. goev_stg_clients
    bank_cursor.execute(capture_client_from_info)
    clients = pd.DataFrame(bank_cursor.fetchall(), columns=[i[0] for i in bank_cursor.description])
    clients_stg_insert = "INSERT INTO deaise.goev_stg_clients(client_id, last_name, first_name, patronymic, date_of_birth, passport_num, passport_valid_to, phone)"
    insert_stg(clients, clients_stg_insert, "CLIENTS", "2. Data has been added to goev_stg_clients")
    #
    # accounts
    # # # 3. goev_stg_accounts
    bank_cursor.execute(capture_account_from_info)
    accounts = pd.DataFrame(bank_cursor.fetchall(), columns=[i[0] for i in bank_cursor.description])
    accounts_stg_insert = "INSERT INTO deaise.goev_stg_accounts(account_num, valid_to, client)"
    insert_stg(accounts, accounts_stg_insert, "ACCOUNTS", "3. Data has been added to goev_stg_accounts")
    #
    # cards
    # # # 4. goev_stg_cards
    bank_cursor.execute(capture_card_from_info)
    cards = pd.DataFrame(bank_cursor.fetchall(), columns=[i[0] for i in bank_cursor.description])
    cards_stg_insert = "INSERT INTO deaise.goev_stg_cards(card_num, account_num)"
    insert_stg(cards, cards_stg_insert, "CARDS", "4. Data has been added to goev_stg_cards")
    #
    # passport_blacklist
    # # # 5 goev_stg_passport_blacklist
    passport_blacklist = pd.read_excel(f'data_files/{passport_blacklist_list[i]}', index_col=False)
    passport_blacklist_stg_insert = "INSERT INTO deaise.goev_stg_passport_blacklist(entry_dt, passport_num)"
    insert_stg(passport_blacklist, passport_blacklist_stg_insert, "PASSPORT BLACKLIST",
               "5. Data has been added to goev_stg_passport_blacklist")
    #
    # terminals
    # # # 6. goev_stg_terminals
    terminals = pd.read_excel(f'data_files/{terminals_list[i]}', index_col=False)
    terminals_stg_insert = "INSERT INTO deaise.goev_stg_terminals(terminal_id, terminal_type, terminal_city, terminal_address)"
    insert_stg(terminals, terminals_stg_insert, "TERMINAL", "6. Data has been added to goev_stg_terminals\n"'')

    edu_conn_commit(success_msg='Transaction Committed\n''_______________________________________________________')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # Updating the dwh layer # # #
    #
    # terminals
    # # 1. Updating data in goev_dwh_dim_terminals_hist
    execute_sgl(edu_cursor, fill_goev_dwh_dim_terminals_hist,
                '1. Data has been updated at the goev_dwh_dim_terminals_hist')
    #
    # clients
    # # # 2. Updating data in goev_dwh_dim_clients_hist
    execute_sgl(edu_cursor, fill_goev_dwh_dim_clients_hist,
                '2. Data has been updated at the goev_dwh_dim_clients_hist')
    #
    # accounts
    # # # 3. Updating data in goev_dwh_dim_accounts_hist
    execute_sgl(edu_cursor, fill_goev_dwh_dim_accounts_hist,
                '3. Data has been updated at the goev_dwh_dim_accounts_hist')
    #
    # cards
    # # # 4. Updating data in goev_dwh_dim_cards
    execute_sgl(edu_cursor, fill_goev_dwh_dim_cards,
                '4. Data has been updated at the goev_dwh_dim_cards')
    #
    # passport_blacklist
    # # # 5. Updating data in goev_dwh_fact_passport_blacklist
    execute_sgl(edu_cursor, fill_goev_dwh_fact_passport_blacklist,
                '5. Data has been updated at the goev_dwh_fact_passport_blacklist')
    #
    # transactions
    # # # 6. Updating data in goev_dwh_fact_transactions
    execute_sgl(edu_cursor, fill_goev_dwh_fact_transaction,
                '6. Data has been updated at the goev_dwh_fact_transactions\n''                                                       ')

    edu_conn_commit(success_msg='Transaction Committed\n''_______________________________________________________')

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # Preparing the report. Load data to the goev_rep_fraud # # #
    #
    # Event 1
    execute_sgl(edu_cursor, add_to_report_event_1,
                'Events 1 have been downloaded to goev_rep_fraud')
    # Event 2
    execute_sgl(edu_cursor, add_to_report_event_2,
                'Events 2 have been downloaded to goev_rep_fraud')
    # Event 3
    execute_sgl(edu_cursor, add_to_report_event_3,
                'Events 3 have been downloaded to goev_rep_fraud')
    # Event 4
    execute_sgl(edu_cursor, add_to_report_event_4,
                'Events 4 have been downloaded to goev_rep_fraud')
    print('')
    edu_conn_commit(success_msg='Transaction Committed\n''_______________________________________________________')

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # Ending # # #
#

print('\n'f' Script took {(time.time() - start_time)} seconds''\n')

#
throw_data_to_backup()
