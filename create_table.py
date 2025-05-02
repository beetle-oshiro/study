# create_table.py
from db_connect import get_connection

def create_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        message TEXT NOT NULL,
        category TEXT NOT NULL,
        time TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    print("✅ テーブル作成成功！")

if __name__ == "__main__":
    create_table()
