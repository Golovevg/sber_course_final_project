import psycopg2

# Connection to database established
conn = psycopg2.connect(database="bank",
                        host="de-edu-db.chronosavant.ru",
                        user="bank_etl",
                        password="bank_etl_password",
                        port="5432")
# Autocommit switched off
conn.autocommit = False

# Cursor created
cursor = conn.cursor()
