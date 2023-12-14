import psycopg2

# Connection to database established
conn = psycopg2.connect(database="***",
                        host="***",
                        user="***",
                        password="***",
                        port="5432")
# Autocommit switched off
conn.autocommit = False

# Cursor created
cursor = conn.cursor()
