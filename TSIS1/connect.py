import psycopg2
from config import DB_CONFIG


def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Could not connect to PostgreSQL: {e}")
        raise


def create_database_if_not_exists():
    tmp_cfg = {**DB_CONFIG, "database": "postgres"}
    conn = psycopg2.connect(**tmp_cfg)
    conn.autocommit = True
    cur = conn.cursor()

    db_name = DB_CONFIG["database"]
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{db_name}"')
        print(f"Database '{db_name}' created.")
    else:
        print(f"Database '{db_name}' already exists.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    create_database_if_not_exists()
    conn = get_connection()
    print("Connection successful!")
    conn.close()