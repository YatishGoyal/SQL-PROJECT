import psycopg2 as psql

def connection():
    conn = psql.connect(host="localhost",database = "Bill",user = "postgres",password = "010826",port = "5432")
    return conn
    
connection()
conn = connection()