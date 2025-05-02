# check_postgres.py
from db_connect import get_connection

def check_records():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM records;")
    rows = cur.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("📭 テーブルにデータがありません！")

    conn.close()

if __name__ == "__main__":
    check_records()
