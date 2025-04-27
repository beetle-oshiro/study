import pymysql

# 接続情報
host = "mysql630.db.sakura.ne.jp"  # たーのびのホスト名
user = "beetle45046"                       # ユーザー名
password = "seiko5_porterswans"             # パスワード
db = "beetle45046_db"                       # データベース名

try:
    # データベースに接続
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db,
        charset="utf8mb4"
    )
    print("✅ MySQLに接続できました！")
    
    # 接続できたらカーソルを作って、テーブル一覧を取得してみる！
    with conn.cursor() as cur:
        cur.execute("SHOW TABLES;")
        tables = cur.fetchall()
        print("📋 テーブル一覧：", tables)

    conn.close()

except Exception as e:
    print("❌ 接続エラー：", e)
