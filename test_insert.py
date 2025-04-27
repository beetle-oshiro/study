# test_insert.py
from logic import insert_to_db
from datetime import datetime

# 現在時刻を文字列で取得（Flaskでも使ってた形式！）
now = datetime.now().strftime("%Y-%m-%d %H:%M")

# テスト用のデータを挿入！
insert_to_db("たーのび", "クラスとSQLiteを学んだよ", "学習", now)
print("✅ データを挿入しました！")
