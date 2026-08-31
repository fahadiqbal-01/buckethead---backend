import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Add it to your .env file before starting the backend.")

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=4,
    max_size=20,
    timeout=10,
    max_lifetime=1800,
    max_idle=300,
)


def check_db_connection():
    try:
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
    except Exception as exc:
        raise RuntimeError(f"Database connection failed: {exc}") from exc