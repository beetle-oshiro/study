#!/usr/local/bin/python3

from flask import Flask, render_template, request, redirect
from datetime import datetime
from logic import (
    register_record_to_postgres,
    get_all_records_postgres,
    get_record_by_id_postgres,
    update_record_in_postgres,
    delete_record_from_postgres,
    filter_by_category,
    filter_by_keyword,
    sort_data,
    get_all_tags
)
import os



# Flaskアプリを作る準備
app = Flask(__name__)


# =========================ベースディレクトリとDBパス=========================
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "data.db")


# =========================ルーティング=========================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/assist", methods=["GET"])
def assist():
    keyword = request.args.get("keyword", "").strip()
    selected_tag = request.args.get("tag", "").strip()

    all_data = get_all_records_postgres()

    # 検索＋タグ絞り込み
    filtered = filter_by_keyword(all_data, keyword)

    if selected_tag:
        filtered = {
            k: v for k, v in filtered.items() if selected_tag in v.get("tags", "")
        }

    from logic import get_all_tags
    tags = get_all_tags()


    return render_template(
            "assist.html",
            results=filtered,
            keyword=keyword,
            tags=tags,
            selected_tag=selected_tag
        )


@app.route("/register", methods=["GET", "POST"])
def register():

    #入力欄の初期値
    word = ""
    details = ""
    tags = []
    status = ""
    memo = ""
    error = ""
    success = ""

    tags_input = get_all_tags()

    # どのカテゴリで表示するか
    filter_category = request.args.get("filter", "all")
    # 何のキーワードで絞り込みするか
    keyword = request.args.get("keyword", "").strip()       #.strip()は文字列の前後にある「空白（スペース・タブ・改行）」を削除する
    # どの並び順にするか
    sort_order = request.args.get("sort", "time")

    #データが送られてきていたら
    if request.method == "POST":
        #登録処理へ
        word, details, tags, status, memo, error = register_record_to_postgres(request.form) #requestにはブラウザから送られてきたリクエスト情報が全部詰まっている
        if not error:
            return redirect("/register?success=1")  # 成功時はリダイレクト（クエリ付き）
        
    # 登録後のリダイレクト先でメッセージ表示するためにクエリを取得
    if request.args.get("success") == "1":
        success = "✅ 登録が完了しました！"
        
    # データを PostgreSQLから取得する場合
    all_data = get_all_records_postgres()
    # 絞り込み処理（カテゴリフィルター）
    filtered_data = filter_by_category(all_data, filter_category)
    # 検索キーワードがあれば絞り込み
    filtered_data = filter_by_keyword(filtered_data, keyword)
    #並び順を決める
    sorted_data = sort_data(filtered_data, sort_order)

    tag_options = get_all_tags()  # ← タグを取得して追加

    return render_template("register.html",                    #それぞれのデータをそれぞれの変数に入れて、index.htmlに返している
                           word=word,
                           details=details,
                           tags_input=tags_input,  # ← 渡す変数名とhtml側で一致させる
                           status=status,
                           memo=memo,
                           data=sorted_data,
                           error=error,
                           success=success,
                        #    tag_options=tag_options,
                           timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# =========================編集画面に情報を渡す=========================
@app.route("/edit/<id>", methods=["GET"])
def edit(id):
    item = get_record_by_id_postgres(id)                        #index.htmlから編集（edit）で送られてきたidに該当するデータをitemに入れる（ない場合はNone）
    tags = get_all_tags()                                       #タグ一覧を取得
    if item:                                                    #itemにデータが入っている場合（編集したいデータを見つけた）
        return render_template("edit.html", id=id, item=item, tags=tags)   #edit.htmlに編集したいデータとそのＩＤを送る
    return redirect("/register")                                        #現在のページ（トップページ）へリダイレクトする


# =========================更新（UPDATE処理）=========================
@app.route("/update/<id>", methods=["POST"])
def update(id):
    word = request.form.get("word", "").strip()
    details = request.form.get("details", "").strip()
    tags = request.form.getlist("tags")  # ← 複数タグ対応！
    status = request.form.get("status", "").strip()
    memo = request.form.get("memo", "").strip()
    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    update_record_in_postgres(id, word, details, tags, status, memo, time)
    return redirect("/assist")


# =========================削除=========================
@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    delete_record_from_postgres(id)                             #URLにつけて送られてきたIDを引数にして送る
    return redirect("/register")                                        #現在のページ（トップページ）へリダイレクトする


# =========================タグ管理ページの表示=========================
@app.route("/settings", methods=["GET", "POST"])
def settings():
    from logic import get_all_tags, register_tag  # 必要な関数をインポート

    error = ""
    success = ""

    if request.method == "POST":
        tag_name = request.form.get("tag_name", "").strip()
        if tag_name:
            result = register_tag(tag_name)
            if result is True:
                success = f"「{tag_name}」を登録しました。"
            else:
                error = f"⚠️ {result}"  # 重複やエラーが返る想定
        else:
            error = "⚠️ タグ名を入力してください。"

    tags = get_all_tags()
    return render_template("settings.html", tags=tags, error=error, success=success)



# =========================クラスのお試しゾーン=========================
class Person:
    def __init__(self, name, hobby):
        self.name = name
        self.hobby = hobby

    def introduce(self):
        return f"こんにちは！私は {self.name} です。趣味は {self.hobby} です！"
    

# =========================実行（WEBアプリ）=========================
# Flaskサーバーを起動するかチェック（ファイルを直接実行したときだけ）
if __name__ == "__main__":          #このファイルが直接実行されているか（"__main__"ならされている）

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)