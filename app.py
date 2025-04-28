#!/usr/local/bin/python3

from flask import Flask, render_template, request, json, redirect
from datetime import datetime
from data import load_json, save_json, data_stock, get_data_by_id
from logic import register_data, filter_by_category, filter_by_keyword, sort_data, update_data, get_all_records, register_to_db, delete_from_db, update_record_in_db, get_record_by_id
import os


# Flaskアプリを作る準備
app = Flask(__name__)


# =========================ベースディレクトリとDBパス=========================
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "data.db")


# =========================ルーティング=========================

@app.route("/", methods=["GET", "POST"])
def index():

    name = ""
    message = ""
    category = ""
    error = ""

    # どのカテゴリで表示するか
    filter_category = request.args.get("filter", "all")
    # 何のキーワードで絞り込みするか
    keyword = request.args.get("keyword", "").strip()       #.strip()は文字列の前後にある「空白（スペース・タブ・改行）」を削除する
    # どの並び順にするか
    sort_order = request.args.get("sort", "time")

    #データが送られてきていたら
    if request.method == "POST":
        name, message, category, error = register_to_db(request.form) #requestにはブラウザから送られてきたリクエスト情報が全部詰まっている
        if not error:
            return redirect("/")  # ←ここでリダイレクト！

    # データを JSONじゃなく DBから取得する場合
    all_data = get_all_records(db_path)

    # 絞り込み処理（カテゴリフィルター）
    filtered_data = filter_by_category(all_data, filter_category)

    # 検索キーワードがあれば絞り込み
    filtered_data = filter_by_keyword(filtered_data, keyword)

    #並び順を決める
    sorted_data = sort_data(filtered_data, sort_order)

    return render_template("index.html",                    #それぞれのデータをそれぞれの変数に入れて、index.htmlに返している
                           name=name,
                           message=message,
                           category=category,
                           data=sorted_data,
                           sort=sort_order,
                           error=error,
                           filter=filter_category,
                           keyword=keyword,
                           timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# =========================編集画面に情報を渡す=========================
@app.route("/edit/<id>", methods=["GET"])
def edit(id):
    item = get_record_by_id(id)                                 #index.htmlから編集（edit）で送られてきたidに該当するデータをitemに入れる（ない場合はNone）
    if item:                                                    #itemにデータが入っている場合（編集したいデータを見つけた）
        return render_template("edit.html", id=id, item=item)   #edit.htmlに編集したいデータとそのＩＤを送る
    return redirect("/")                                        #現在のページ（トップページ）へリダイレクトする


# =========================更新（UPDATE処理）=========================
@app.route("/update/<id>", methods=["POST"])
def update(id):
    name = request.form.get("name").strip()                     #edit.htmlから更新（update）で送られてきたnameに該当するデータを空白を抜いてnameに入れる
    category = request.form.get("category").strip()             #edit.htmlから更新（update）で送られてきたcategoryに該当するデータを空白を抜いてcategoryに入れる
    message = request.form.get("message").strip()               #edit.htmlから更新（update）で送られてきたmessageに該当するデータを空白を抜いてmessageに入れる
    time = datetime.now().strftime("%Y-%m-%d %H:%M")            #現在の日時をtimeに入れる

    update_record_in_db(id, name, category, message, time)      #更新したいデータのIDと名前、カテゴリー、メッセージを更新処理に送る
    return redirect("/")                                        #現在のページ（トップページ）へリダイレクトする


# =========================削除=========================
@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    delete_from_db(id)                                          #URLにつけて送られてきたIDを引数にして送る
    return redirect("/")                                        #現在のページ（トップページ）へリダイレクトする

    # if id in data_stock:                                        #data_stock（辞書）の中に削除したいIDに該当するキーがある場合
    #     del data_stock[id]                                      #該当のデータを辞書から削除
    #     save_json()                                             #保存

# =========================実行=========================
# print("💡 load_json() を呼び出します")
# load_json()
# print("📦 読み込まれたデータ：", data_stock)



# =========================クラスのお試しゾーン=========================
class Person:
    def __init__(self, name, hobby):
        self.name = name
        self.hobby = hobby

    def introduce(self):
        return f"こんにちは！私は {self.name} です。趣味は {self.hobby} です！"
    

# =========================テスト=========================
db_path = os.path.join(os.path.dirname(__file__), "data.db")
records = get_all_records(db_path)

print("📋 取得されたレコード：", records)
    

# # =========================実行=========================
# # Flaskサーバーを起動するかチェック（ファイルを直接実行したときだけ）
# if __name__ == "__main__":          #このファイルが直接実行されているか（"__main__"ならされている）
#     test_person = Person("たーのび", "日向坂46を応援すること")
#     print(test_person.introduce())

#     # Flaskアプリを起動
#     load_json()                     #JSONファイル（data.json）を読み込んで、その中身（辞書の形のデータ）を data_stock に入れ直す関数
#     app.run(debug=True)             #Flaskアプリを起動
                                    #（開発しやすくするために「デバッグモード」で実行）


# =========================実行（WEBアプリ）=========================
# Flaskサーバーを起動するかチェック（ファイルを直接実行したときだけ）
if __name__ == "__main__":          #このファイルが直接実行されているか（"__main__"ならされている）

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)





# if __name__ == "__main__":
#     app.run(debug=True)
