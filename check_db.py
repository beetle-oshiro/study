import sqlite3
import os


db_path = os.path.join(os.path.dirname(__file__), "data.db")
print("📦 作成されるDBのパス：", db_path)


# データベースに接続
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# データを全件取得！
cur.execute("SELECT * FROM records")
rows = cur.fetchall()

# 結果を表示
if rows:
    for row in rows:
        print(row)
else:
    print("📭 テーブルはまだ空っぽみたい！")

# 接続を閉じる
conn.close()
