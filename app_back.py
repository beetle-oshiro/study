from flask import Flask, render_template, request, json, redirect
from datetime import datetime


app = Flask(__name__)


# =========================データ管理=========================
# データを保管する変数を用意
data_stock = {}


# =========================データをJSONファイルに保存=========================
def save_json():
    # 現在の data_stock を JSON ファイルに保存
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data_stock, f, ensure_ascii=False, indent=2)


# =========================JSONファイルを読み込んで復元=========================
def load_json():
    # JSON ファイルから data_stock を読み込む
    global data_stock
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data_stock = json.load(f)
    except FileNotFoundError:
        data_stock = {}


# =========================IDの生成=========================
def get_next_id():
    # 次に使うIDを文字列で取得
    if data_stock:
        return str(max(int(k) for k in data_stock.keys()) + 1)
    else:
        return "1"
    

# =========================登録処理（データがあるか？ある場合は登録）=========================
def register_data(req):
    name = req.form.get("name", "").strip()
    message = req.form.get("message", "").strip()
    category = req.form.get("category", "").strip()
    error = ""

    if not name or not message or not category:
        error = "すべての項目を入力してください！"
    else:
        new_id = get_next_id()
        data_stock[new_id] = {
            "name": name,
            "message": message,
            "category": category,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_json()

    return name, message, category, error


# =========================カテゴリーの絞り込み=========================
def filter_by_category(data_dict, category):
    if category == "all":
        return data_dict
    else:
        result = {}
        for k, v in data_dict.items():
            if v["category"] == category:
                result[k] = v
        return result
    

# =========================キーワードでの絞り込み=========================
def filter_by_keyword(data_dict, keyword):
    if keyword == "":
        return data_dict

    result = {}
    keyword_lower = keyword.lower()
    for k, v in data_dict.items():
        name_lower = v["name"].lower()
        message_lower = v["message"].lower()
        if keyword_lower in name_lower or keyword_lower in message_lower:
            result[k] = v

    return result


# =========================並び順の判断=========================
def sort_data(data_dict, sort_order):
    if sort_order == "name":        #名前順
        return dict(sorted(data_dict.items(), key=lambda x: x[1]["name"]))
    else:                           #新着順
        return dict(sorted(
            data_dict.items(),
            key=lambda x: datetime.strptime(x[1]["time"], "%Y-%m-%d %H:%M"),
            reverse=True
        ))


# =========================データの辞書からidを探す（無ければNone）=========================
def get_data_by_id(id):
    return data_stock.get(id)


# =========================更新処理=========================
def update_data(id, name, category, message):
    if id in data_stock:
        data_stock[id].update({
            "name": name,
            "category": category,
            "message": message,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        save_json()


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
    keyword = request.args.get("keyword", "").strip()
    # どの並び順にするか
    sort_order = request.args.get("sort", "time")

    #データが送られてきていたら
    if request.method == "POST":
        name, message, category, error = register_data(request)

    # 絞り込み処理（カテゴリフィルター）
    filtered_data = filter_by_category(data_stock, filter_category)
        

    # 検索キーワードがあれば絞り込み
    filtered_data = filter_by_keyword(filtered_data, keyword)


    #並び順を決める
    sorted_data = sort_data(filtered_data, sort_order)

    return render_template("index.html",
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
    item = get_data_by_id(id)
    if item:
        return render_template("edit.html", id=id, item=item)
    return redirect("/")


# =========================更新（UPDATE処理）=========================
@app.route("/update/<id>", methods=["POST"])
def update(id):
    name = request.form.get("name")
    category = request.form.get("category")
    message = request.form.get("message")

    update_data(id, name, category, message)
    return redirect("/")


# =========================削除=========================


@app.route("/delete/<id>", methods=["POST"])
def delete(id):
    if id in data_stock:
        del data_stock[id]
        save_json()
    return redirect("/")


# =========================実行=========================
load_json()


if __name__ == "__main__":
    app.run(debug=True)
