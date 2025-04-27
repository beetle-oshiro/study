import json
import os
from datetime import datetime


# =========================共通のファイルパス設定=========================
current_dir = os.path.dirname(__file__)
json_path = os.path.join(current_dir, "data.json")


# =========================データを保管する変数=========================
data_stock = {}


# =========================データをJSONファイルに保存=========================
def save_json():
    # print("💾 保存される内容：", data_stock)
    with open(json_path, "w", encoding="utf-8") as f:               # ←共通のパス使用　書き込みモードで対象のファイルを開く（そのファイルへの書込みなどはfを用いる？）
        json.dump(data_stock, f, ensure_ascii=False, indent=2)      #辞書の中身をファイル（f）にJSON形式で書き込む


# =========================JSONファイルを読み込んで復元=========================
def load_json():

    global data_stock                                           #関数外の変数data_stockを使う

    if not os.path.exists(json_path):                           #json_pathが無かった場合は
        print("🚨 data.json が見つかりません！")                 #警告をターミナルに表示
        data_stock = {}                                         #data_stock（辞書）を空にする
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:       #json_pathというパスの先にあるファイルを読み込みモードで開く（そのファイルへの読み込みなどはfを用いる？）
            loaded_data = json.load(f)                          #その中身を JSON として読み込んで、loaded_data に入れる
            data_stock.clear()                                  # ←ここで元の辞書をクリア
            data_stock.update(loaded_data)                      # ←data_stock(辞書)の中身を中身をloaded_dataに更新！
            print("📦 読み込み成功！中身：", data_stock)
    except Exception as e:                                      #エラーが出たら、内容をeに入れる
        print("❌ 読み込みエラー：", e)                          #ターミナルにエラー内容を表示
        data_stock = {}                                         #data_stockを空にする


# =========================IDの生成=========================
def get_next_id():
    if data_stock:                                              #辞書に登録データがある場合
        return str(max(int(k) for k in data_stock.keys()) + 1)  #今あるデータの中で最大のIDを探して、それに1を足して、新しいIDとして返す（辞書で登録されているので、整数型にして取り出して1を足して、再度文字型にもどしている）
    else:                                                       #辞書に登録データがない場合
        return "1"                                              #最初のデータということで1を返す


# =========================データの辞書からidを探す（無ければNone）=========================
def     get_data_by_id(id):
    return data_stock.get(id)   #引数で渡されたidに対応するデータ（辞書の中身）を返す　ない場合はNoneを返す（.get(id, ありません)）としていたら、Noneではなく「ありません」を返す
