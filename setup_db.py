import sqlite3
import os


db_path = os.path.join(os.path.dirname(__file__), "data.db")
print("📦 作成されるDBのパス：", db_path)


# データベースに接続（なければ自動で作られる！）
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# テーブルを作成（もし存在しなければ）
cur.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    message TEXT NOT NULL,
    category TEXT NOT NULL,
    time TEXT NOT NULL
)
""")

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("📋 データベース内のテーブル一覧：", cur.fetchall())

# 保存して終了！
conn.commit()
conn.close()

print("✅ データベースとテーブルを作成しました！")
