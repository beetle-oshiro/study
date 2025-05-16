from datetime import datetime
from data import data_stock, save_json, get_next_id
import sqlite3
import os
from db_connect import get_connection


# =========================共通のファイルパス設定=========================
# current_dir = os.path.dirname(__file__)
# db_path = os.path.join(current_dir, "data.db")

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "data.db")


# =========================登録処理（データがあるか？ある場合は登録） JSON版=========================
#json方式でファイルに登録バージョン
def register_data(req):
    name = req.form.get("name", "").strip()             #ブラウザから送られてきたデータの中のnameの中身を空白を省いて変数nameに入れる
    message = req.form.get("message", "").strip()       #ブラウザから送られてきたデータの中のmessageの中身を空白を省いて変数messageに入れる
    category = req.form.get("category", "").strip()     #ブラウザから送られてきたデータの中のcategoryの中身を空白を省いて変数categoryに入れる
    error = ""                                          #errorには何もいれない（空白）

    if not name or not message or not category:         #ブラウザから送られてきたデータの中のname、message、categoryの内のどれか1つでも空欄があった場合
        error = "すべての項目を入力してください！"         #errorに警告文を入れる
    else:                                               #name、message、categoryの全てにデータが入っていた場合
        new_id = get_next_id()                          #新しいIDを作る
        data_stock[new_id] = {                          #そのIDを使って、辞書にデータを入れていく（ブラウザで入力したデータと、今の現在日時が登録される）
            "name": name,
            "message": message,
            "category": category,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_json()

    return name, message, category, error               #それぞれの変数の値を返す


# =========================登録処理（データがあるか？ある場合は登録）データベース版 =========================
def register_to_db(form):
    name = form.get("name", "").strip()
    message = form.get("message", "").strip()
    category = form.get("category", "").strip()
    error = ""

    if not name or not message or not category:
        error = "すべての項目を入力してください！"
    else:
        time = datetime.now().strftime("%Y-%m-%d %H:%M")
        insert_to_db(name, message, category, time)

    return name, message, category, error


#データベースに登録バージョン
def insert_to_db(name, message, category, time):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO records (name, message, category, time)
        VALUES (?, ?, ?, ?)
    """, (name, message, category, time))
    conn.commit()
    conn.close()




# =========================登録処理（データがあるか？ある場合は登録）PostgreSQL版 =========================
def register_record_to_postgres(form):
    word = form.get("word", "").strip()
    details = form.get("details", "").strip()
    status = form.get("status", "").strip()
    memo = form.get("memo", "").strip()
    error = ""
    tag_ids = form.getlist("tags")  # ← ここが複数受け取り！

    if not word:
        error = "ワードは必須項目です！"
        return word, details, tag_ids, status, memo, error

    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 学習内容の登録
        cur.execute("""
            INSERT INTO records (word, details, tags, status, memo, created_at)
            VALUES (%s, %s, NULL, %s, %s, %s)
            RETURNING id
        """, (word, details, status, memo, time_str))

        record_id = cur.fetchone()[0]  # ← 登録されたIDを取得

        # タグの関連付け（record_tags に保存）
        for tag_id in tag_ids:
            cur.execute("""
                INSERT INTO record_tags (record_id, tag_id)
                VALUES (%s, %s)
            """, (record_id, tag_id))

        conn.commit()
        conn.close()

    except Exception as e:
        error = f"登録中にエラーが発生しました：{e}"

    return word, details, tag_ids, status, memo, error



# =========================PostgreSQLから全データ取得=========================

def get_all_records_postgres():
    conn = get_connection()
    cur = conn.cursor()

     # レコードとタグをJOINで取得
    cur.execute("""
        SELECT r.id, r.word, r.details, r.status, r.memo, r.created_at,
               t.tag_name
        FROM records r
        LEFT JOIN record_tags rt ON r.id = rt.record_id
        LEFT JOIN tags t ON rt.tag_id = t.id
        ORDER BY r.created_at DESC
    """)    
    rows = cur.fetchall()
    conn.close()

    # データを辞書に整形
    result = {}
    for row in rows:
        record_id = str(row[0])
        if record_id not in result:
            result[record_id] = {
                "word": row[1],
                "details": row[2],
                "status": row[3],
                "memo": row[4],
                "time": row[5],
                "tags": []
            }

        # タグが存在する場合のみ追加（NULL対策）
        if row[6]:
            result[record_id]["tags"].append(row[6])

    return result


# =========================データの削除（データベース：MySQL）=========================
def delete_from_db(record_id):
    conn = sqlite3.connect(os.path.normpath(db_path))
    cur = conn.cursor()
    cur.execute("DELETE FROM records WHERE id = ?", (record_id,))               #プレースホルダを使って安全に削除のSQLを実行
    conn.commit()
    conn.close()


# =========================データの削除（データベース：PostgreSQL）=========================
def delete_record_from_postgres(record_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM records WHERE id = %s", (record_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ 削除中にエラーが発生しました：{e}")


# =========================データの検索（データベース）=========================
def get_all_records(db_path):
    # print("ここの下")
    # print(db_path)
    # print("👀 db_path は：", db_path)
    # print("📦 ファイルが存在する？：", os.path.exists(db_path))
    conn = sqlite3.connect(os.path.normpath(db_path))       #db_path の中にあるスラッシュ・バックスラッシュなどを、OSに合わせてキレイに整える
    conn.row_factory = sqlite3.Row      #row[〇]ここにデータベースの列名が使えるように
    cur = conn.cursor()
    cur.execute("SELECT * FROM records")
    rows = cur.fetchall()       #↑のSELECTで抜き取ったデータ（全件）をタプルのリストで返す
    conn.close()
    
    # 辞書形式に整える（Flaskで今までと同じように扱えるようにする）
    result = {}
    for row in rows:
        record_id = str(row[0])
        result[record_id] = {
            "name": row[1],
            "message": row[2],
            "category": row[3],
            "time": row[4]
        }
    return result


# =========================更新したいデータをデータベースから取ってくる（MySQL） =========================
def get_record_by_id(record_id):
    conn = sqlite3.connect(os.path.normpath(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM records WHERE id = ?", (record_id,))
    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "name": row["name"],
            "message": row["message"],
            "category": row["category"],
            "time": row["time"]
        }
    else:
        return None


# =========================更新処理（データベース：MySQL）=========================
def update_record_in_db(record_id, name, category, message, time):
    conn = sqlite3.connect(os.path.normpath(db_path))
    cur = conn.cursor()
    cur.execute("""
        UPDATE records
        SET name = ?, category = ?, message = ?, time = ?
        WHERE id = ?
    """, (name, category, message, time, record_id))
    conn.commit()
    conn.close()


# =========================更新したいデータをデータベースから取ってくる（PostgreSQL）=========================
def get_record_by_id_postgres(record_id):
    conn = get_connection()
    cur = conn.cursor()

    # メイン情報（word, detailsなど）
    cur.execute("""
        SELECT id, word, details, status, memo, created_at
        FROM records
        WHERE id = %s
    """, (record_id,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return None

    # タグ情報を取得（tag_name のリストを作る）
    cur.execute("""
        SELECT t.tag_name
        FROM tags t
        JOIN record_tags rt ON t.id = rt.tag_id
        WHERE rt.record_id = %s
    """, (record_id,))
    tag_rows = cur.fetchall()
    conn.close()

    tag_list = [tag_row[0] for tag_row in tag_rows]  # 例：['Python', 'PHP']

    return {
        "word": row[1],
        "details": row[2],
        "status": row[3],
        "memo": row[4],
        "time": row[5],
        "tags": tag_list  # ← リストで渡す！
    }



# =========================更新処理（データベース：PostgreSQL）=========================
def update_record_in_postgres(record_id, word, details, tags, status, memo, time_str):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # records テーブルの更新（tagsカラムは使わない）
        cur.execute("""
            UPDATE records
            SET word = %s,
                details = %s,
                status = %s,
                memo = %s,
                created_at = %s
            WHERE id = %s
        """, (word, details, status, memo, time_str, record_id))

        # 既存のタグを削除
        cur.execute("DELETE FROM record_tags WHERE record_id = %s", (record_id,))

        # 新しいタグを登録
        for tag_id in tags:
            cur.execute("""
                INSERT INTO record_tags (record_id, tag_id)
                VALUES (%s, %s)
            """, (record_id, tag_id))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ 更新中にエラーが発生しました：{e}")



# =========================カテゴリーの絞り込み=========================
def filter_by_category(data_dict, category):
    if category == "all":                   #指定されたカテゴリーがallなら
        return data_dict                    #全データをそのまま返す
    else:
        result = {}                         #空の辞書を準備
        for k, v in data_dict.items():      #登録されて全データのキーと中身を取り出していく
            if v["category"] == category:   #指定されたカテゴリーと合うものをキーごとに探す
                result[k] = v               #見つかったらその"category"の中身とその"category"のあったキーを準備していた辞書に入れる
        return result                       #辞書を返す


# =========================キーワードでの絞り込み=========================
def filter_by_keyword(data_dict, keyword):
    if keyword == "":                       #キーワードが空欄の場合は
        return data_dict                    #絞り込みせずそのままデータを返す

    result = {}                             #空の辞書を用意
    keyword_lower = keyword.lower()         #指定されたキーワードを小文字にする
    for k, v in data_dict.items():          #カテゴリーで絞られたデータ（もしくは全データ）のキーと中身を取り出していく
        # word, details, tags の3つを検索対象にする
        word = v.get("word", "").lower()
        details = v.get("details", "").lower()
        tag_list = v.get("tags", [])  # ←リストのまま取得
        tag_str = ",".join(tag_list).lower()  # ←リストを文字列にして小文字に
        if (keyword_lower in word or
            keyword_lower in details or
            keyword_lower in tag_str):
            result[k] = v

    return result                           #辞書を返す


# =========================並び順の判断=========================
def sort_data(data_dict, sort_order):
    if sort_order == "name":                                                #並び順でname（名前順）が選択されていた場合
        return dict(sorted(data_dict.items(), key=lambda x: x[1]["name"]))  #data_dict（全データ、もしくは絞り込まれたデータ）の中身を「名前の文字列順（昇順）」で並び替えて、新しい辞書として返してる
    else:                                                                   #並び順でname（名前順）が選択されていない場合（つまり時間順が選択されている）
        return dict(sorted(                                                 #data_dict（全データ、もしくは絞り込まれたデータ）の中身を「時間順（降順）」で並び替えて、新しい辞書として返してる
            data_dict.items(),
            key=lambda x: x[1]["time"],
            reverse=True
        ))


# =========================更新処理=========================
def update_data(id, name, category, message):
    if id in data_stock:                                        #data_stock（辞書）の中に更新したいIDに該当するキーがある場合
        data_stock[id].update({                                 #data_stockのそのキーのデータにname,category,message,timeのデータを上書きする
            "name": name,
            "category": category,
            "message": message,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_json()                                             #保存


# =========================全タグを取得（PostgreSQL）=========================
def get_all_tags():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, tag_name FROM tags ORDER BY tag_name")
    rows = cur.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({"id": row[0], "name": row[1]})
    return result

# =========================タグを登録（PostgreSQL）=========================
def register_tag(tag_name):
    try:
        conn = get_connection()
        cur = conn.cursor()
        # 重複チェック
        cur.execute("SELECT COUNT(*) FROM tags WHERE tag_name = %s", (tag_name,))
        count = cur.fetchone()[0]
        if count > 0:
            return "このタグはすでに登録されています。"

        # 登録処理
        cur.execute("INSERT INTO tags (tag_name) VALUES (%s)", (tag_name,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return f"データベースエラー：{e}"
