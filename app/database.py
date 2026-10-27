import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "club_management"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )

def fetch_all(sql, params=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()

def fetch_one(sql, params=None):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None

def execute(sql, params=None):
    conn = get_connection()
    try:
        with conn:                      # commit on success, rollback on error
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.rowcount
    finally:
        conn.close()

def run_transaction(statements):
    """statements = [(sql, params), ...]  all succeed or none do."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for sql, params in statements:
                    cur.execute(sql, params)
    finally:
        conn.close()