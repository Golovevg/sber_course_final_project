from datetime import date
import os
import re
from os import path



# # # Functions # # #
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

def throw_data_to_backup()
    date = date.today()
    folder = f'archive/{date}'
    if not path.exists(folder):
        os.mkdir(folder)
    for i in os.listdir('data_files'):
        os.rename(f'data_files/{i}', f'{folder}/{i}.backup')

check_entirety()
transactions, passport_blacklist, terminals, unknown = files_list()




