import os
from contextlib import contextmanager

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_env(cls):
        return cls(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
        )


class DatabaseManager:
    def __init__(self, config=None):
        self.config = config or DatabaseConfig.from_env()

    def connect(self):
        return psycopg2.connect(
            host=self.config.host,
            database=self.config.database,
            user=self.config.user,
            password=self.config.password,
            port=self.config.port,
        )

    @contextmanager
    def connection(self):
        conn = self.connect()
        try:
            yield conn
        finally:
            conn.close()

    def execute(self, query, params=None):
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
            conn.commit()

    def execute_many(self, query, rows):
        if not rows:
            return

        with self.connection() as conn:
            with conn.cursor() as cur:
                for row in rows:
                    cur.execute(query, row)
            conn.commit()

    def test_connection(self):
        with self.connection():
            return True


def get_connection():
    return DatabaseManager().connect()