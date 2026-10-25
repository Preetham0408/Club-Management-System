import psycopg2

def get_connection():
    conn = psycopg2.connect(
        dbname="club_management",
        user="postgres",
        password="", # Update with your PostgreSQL password
        host="localhost",
        port="5432"
    )
    return conn