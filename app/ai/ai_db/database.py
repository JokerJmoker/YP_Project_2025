import psycopg2
from .db_config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()