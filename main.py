import pandas as pd
import os
import re
from credentials.bank_credentials import cursor as bank_cursor
from credentials.edu_credentials import cursor as edu_cursor, conn as edu_conn

# # # Functions # # #
#
# 1. Checking the entirety
def check_entirety():
    file_list = os.listdir('data_files')
    file_name = ['transactions', 'terminals', 'passport_blacklist']
    if len(file_list) == 0:
        print("Data hasn't been added from the sources")
    for i in file_name:
        if not re.findall(i, str(file_list)):
            print(f"File {i.upper()} hasn't been added from the data source")
    if len(file_list) % 3 != 0:
        print(f'{file_list %3 } files are absent in the data downloaded from the sources')
#
# 2. Data files list
def files_list():
    file_list = os.listdir('data_files')
    transactions = []
    terminals = []
    passport_blacklist = []
    unknown = []
    for i in file_list:
        if i.startswith('transactions'):
            transactions.append(i)
        if i.startswith('terminals'):
            terminals.append(i)
        if i.startswith('passport_blacklist'):
            passport_blacklist.append(i)
        else:
            unknown.append(i)
    return (sorted(transactions), sorted(passport_blacklist), sorted(terminals), sorted(unknown))
#
# 3. Deleting data from the data_files folder and storing it to an archive
def throw_data_to_backup():
    date = date.today()
    folder = f'archive/{date}'
    if not path.exists(folder):
        os.mkdir(folder)
    for i in os.listdir('data_files'):
        os.rename(f'data_files/{i}', f'{folder}/{i}.backup')
#
# 4. Execute sgl request
def execute_sgl(cursor, conn, request, success_msg=None, error_msg=None):
    try:
        cursor.execute(request)
    except Exception as error:
        print(error_msg, error)
    else:
        conn.commit()
        print(success_msg)
#
# 5. Add '%s' for insert in executemany() function
def s(columns):
    return ', '.join(['%s' for i in columns])
#
# 6. Insert function for the staging layer tables
def insert_stg(df, insert, error_msg=None, success_msg=None):
    df_s = s(df.columns)
    insert = f"{insert} VALUES({df_s})"
    try:
        edu_cursor.executemany(insert, df.values.tolist())
    except Exception as error:
        print(f"{error_msg} Error: ", error)
    else:
        edu_conn.commit()
        print(success_msg)

# # # Checking the data in the data_files # # #
check_entirety()
transactions, passport_blacklist, terminals, unknown = files_list()

# # # Clearing staging layer # # #
from sql_scripts.clear_stg_layer import clear_stg_layer

execute_sgl(edu_cursor, edu_conn, clear_stg_layer, 'Staging layer has been successfully cleaned\n'
                                                   '                                                       \n'
                                                   '_______________________________________________________')

# # # Downloading data from the sources to the staging tables and updating the dwh layer # # #
#
# terminals
for i in terminals:
    # # 1. goev_stg_terminals
    terminals = pd.read_excel(f'data_files/{i}', index_col=False)
    terminals_stg_insert = "INSERT INTO deaise.goev_stg_terminals(terminal_id, terminal_type, terminal_city, terminal_address)"
    insert_stg(terminals, terminals_stg_insert, "TERMINAL", "Data has been added to goev_stg_terminals")

    # # 1. Updating data in goev_dwh_dim_terminals_hist
    from sql_scripts.fill_goev_dwh_dim_terminals_hist import fill_goev_dwh_dim_terminals_hist
    execute_sgl(edu_cursor, edu_conn, fill_goev_dwh_dim_terminals_hist,
                'Data has been updated at the fill_goev_dwh_dim_terminals_hist')

# clients
# # # 2. goev_stg_clients
clients_sql = "select client_id, last_name, first_name, patronymic, date_of_birth, passport_num, passport_valid_to, phone, create_dt, update_dt from info.clients"
bank_cursor.execute(clients_sql)
clients = pd.DataFrame(bank_cursor.fetchall(), columns=[i[0] for i in bank_cursor.description])
clients_stg_insert = "INSERT INTO deaise.goev_stg_clients(client_id, last_name, first_name, patronymic, date_of_birth, passport_num, passport_valid_to, phone, create_dt, update_dt)"
insert_stg(clients, clients_stg_insert, "CLIENTS", "Data has been added to goev_stg_clients")
#
# # # 2. Updating data in goev_dwh_dim_clients_hist
from sql_scripts.fill_goev_dwh_dim_clients_hist_ import goev_dwh_dim_clients_hist

execute_sgl(edu_cursor, edu_conn, goev_dwh_dim_clients_hist,
            'Data has been updated at the goev_dwh_dim_clients_hist')
#
# accounts
# # # 3. goev_stg_accounts
accounts_sql = "select * from info.accounts"
bank_cursor.execute(accounts_sql)
accounts = pd.DataFrame(bank_cursor.fetchall(), columns=[i[0] for i in bank_cursor.description])
accounts_stg_insert = "INSERT INTO deaise.goev_stg_accounts(account_num, valid_to, client, create_dt, update_dt)"
insert_stg(accounts, accounts_stg_insert, "ACCOUNTS", "Data has been added to goev_stg_accounts")
#
# # # 3. Updating data in goev_dwh_dim_accounts_hist
from sql_scripts.fill_goev_dwh_dim_accounts_hist_ import goev_dwh_dim_accounts_hist

execute_sgl(edu_cursor, edu_conn, goev_dwh_dim_accounts_hist,
            'Data has been updated at the goev_dwh_dim_accounts_hist')
#
# cards
# # # 4. goev_stg_cards
cards_sql = "select card_num, account from info.cards"
bank_cursor.execute(cards_sql)
cards = pd.DataFrame(bank_cursor.fetchall(), columns=[i[0] for i in bank_cursor.description])
cards_stg_insert = "INSERT INTO deaise.goev_stg_cards(card_num, account_num)"
insert_stg(cards, cards_stg_insert, "CARDS", "Data has been added to goev_stg_cards")
#
# # # 4. Updating data in goev_dwh_dim_cards
from sql_scripts.fill_goev_dwh_dim_cards import fill_goev_dwh_dim_cards

execute_sgl(edu_cursor, edu_conn, fill_goev_dwh_dim_cards,
            'Data has been updated at the goev_dwh_dim_cards')
#
# passport_blacklist
# # # 5 goev_stg_passport_blacklist
for i in passport_blacklist:
    # # # 5. goev_stg_passport_blacklist
    passport_blacklist = pd.read_excel('data_files/passport_blacklist_01032021.xlsx', index_col=False)
    passport_blacklist_stg_insert = "INSERT INTO deaise.goev_stg_passport_blacklist(entry_dt, passport_num)"
    insert_stg(passport_blacklist, passport_blacklist_stg_insert, "PASSPORT BLACKLIST", "Data has been added to goev_stg_passport_blacklist")
    #
    # # # 5. Updating data in goev_dwh_fact_passport_blacklist
    execute_sgl(edu_cursor, edu_conn, """insert into goev_dwh_fact_passport_blacklist select passport_num, now() from goev_stg_passport_blacklist""",
                'Data has been updated at the goev_dwh_fact_passport_blacklist')

#
# transactions
# # # 6. goev_stg_transactions
transactions = pd.read_csv('data_files/transactions_01032021.txt', engine='python', delimiter=';', decimal=',')
transactions_stg_insert = "INSERT INTO deaise.goev_stg_transactions(trans_id, trans_date, amt, card_num, oper_type, oper_result, terminal)"
insert_stg(transactions, transactions_stg_insert, "TRANSACTIONS", "Data has been added to goev_stg_transactions\n"
                                                                  "                                                       \n"
                                                                  "_______________________________________________________")
#
# # # 6. Updating data in goev_dwh_fact_transactions
execute_sgl(edu_cursor, edu_conn, """insert into goev_dwh_fact_transactions select * from goev_stg_transactions""",
            'Data has been updated at the goev_dwh_fact_transactions')

