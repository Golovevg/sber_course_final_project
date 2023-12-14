import pandas as pd
import os
import re
from datetime import date
from credentials.edu_credentials import cursor as edu_cursor, conn as edu_conn


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # Functions # # #
#
# 1. Checking the entirety in data_files
def check_entirety():
    file_list = os.listdir('data_files')
    file_name = ['transactions', 'terminals', 'passport_blacklist']
    if len(file_list) == 0:
        print("Data hasn't been added from the sources")
    for i in file_name:
        if not re.findall(i, str(file_list)):
            print(f"File {i.upper()} hasn't been added from the data source")
    if len(file_list) % 3 != 0:
        print(f'{file_list % 3} files are absent in the data downloaded from the sources')


#
# 2. Creating the list of files names in data_files
def files_list():
    file_list = os.listdir('data_files')
    transactions = []
    terminals = []
    passport_blacklist = []
    unknown = []
    for i in file_list:
        if i.startswith('transactions'):
            transactions.append(i)
        elif i.startswith('terminals'):
            terminals.append(i)
        elif i.startswith('passport_blacklist'):
            passport_blacklist.append(i)
        else:
            unknown.append(i)
    return (sorted(transactions), sorted(passport_blacklist), sorted(terminals), sorted(unknown))


#
# 3. Deleting data from the data_files folder and storing it to an archive
def throw_data_to_backup():
    dt = date.today()
    folder = f'archive/{dt}'
    if not os.path.exists(folder):
        os.mkdir(folder)
    for i in os.listdir('data_files'):
        os.rename(f'data_files/{i}', f'{folder}/{i}.backup')
    print(f'Data has been moved to {folder}')


#
# 4. Execute sgl request
def execute_sgl(cursor, request, success_msg=None, error_msg=None):
    try:
        cursor.execute(request)
    except Exception as error:
        print(error_msg, error)
    else:
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
        print(success_msg)

#
# 7. Commit
def (success_msg=None, error_msg=None):
    try:
        edu_conn.commit()
    except Exception as error:
        print(error_msg, error)
    else:
        print(success_msg)
