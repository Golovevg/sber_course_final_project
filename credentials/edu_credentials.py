import psycopg2

# Connection to database established
conn = psycopg2.connect(database="edu",
                        host="de-edu-db.chronosavant.ru",
                        user="deaise",
                        password="meriadocbrandybuck",
                        port="5432")
# Autocommit switched off
conn.autocommit = False

# Cursor created
cursor = conn.cursor()
