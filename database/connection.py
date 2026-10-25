
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3307")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "autonorm_db"),
        cursorclass=pymysql.cursors.DictCursor
    )


def test_connection():
    conn = None

    try:
        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

        return {
            "ok": True,
            "database": os.getenv("DB_NAME", "autonorm_db"),
            "port": int(os.getenv("DB_PORT", "3307"))
        }

    except Exception as e:
        print("DB ERROR:", e, flush=True)

        return {
            "ok": False,
            "database": os.getenv("DB_NAME", "autonorm_db"),
            "port": int(os.getenv("DB_PORT", "3307")),
            "error": str(e)
        }

    finally:
        if conn:
            conn.close()
