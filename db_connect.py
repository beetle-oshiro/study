import psycopg2
import os

# 接続情報（ここは後でたーのびの本物の情報に置き換える！）
DB_HOST = "dpg-d08bkg9r0fns73brpmjg-a.oregon-postgres.render.com"
DB_NAME = "study_sys_db"
DB_USER = "study_user"
DB_PASS = "6vQNae5v64GRxT6bvNP7uSyDu1mgrFqJ"

# 接続を作る関数
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        sslmode="require"  # ←セキュリティ強化のため必ずつけよう！
    )


if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ PostgreSQLへの接続に成功しました！")
        conn.close()
    except Exception as e:
        print("❌ 接続に失敗しました:", e)