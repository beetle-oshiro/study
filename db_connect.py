import os
from dotenv import load_dotenv
import psycopg2


# .envファイルの読み込み
load_dotenv()


# .envから取得
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# 接続を作る関数
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode="require"
    )


if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ PostgreSQLへの接続に成功しました！")
        conn.close()
    except Exception as e:
        print("❌ 接続に失敗しました:", e)