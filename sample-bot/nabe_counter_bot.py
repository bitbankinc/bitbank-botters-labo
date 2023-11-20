import time
import logging
import python_bitbankcc  # Bitbank APIのPythonライブラリをインポート
import datetime

# ログレベルをINFOに設定
logging.basicConfig(level=logging.INFO)

# 初期設定
print("初期設定を行います。")
API_KEY = ''  # APIキーを設定
API_SECRET = ''  # APIシークレットを設定
pub = python_bitbankcc.public()  # パブリックAPIインスタンスを作成
prv = python_bitbankcc.private(API_KEY, API_SECRET)  # プライベートAPIインスタンスを作成

# 各種パラメータ
print("各種パラメータを設定します。")
order_lot = 50  # 注文量を設定
time_frame = 11  # 時間枠を設定
price_diff_percent = 1  # 価格差のパーセンテージを設定
exit_profit_percent = 2.5  # 利益確定のパーセンテージを設定
exit_loss_percent = 2  # 損切りのパーセンテージを設定

# ポジション情報
current_position = 0  # 現在のポジション（注文量）を設定
entry_price = 0  # エントリー価格を設定

while True:  # 無限ループ開始
    # 現在の日付を取得して、YYYYMMDD形式に変換
    current_date = datetime.datetime.now().strftime('%Y%m%d')

    # 高値・安値を計算
    print("高値・安値を計算します。")
    value = pub.get_candlestick('xrp_jpy', '1hour', current_date)  # 1時間足のローソク足データを取得
    ohlcv = value['candlestick'][0]['ohlcv'][-(time_frame + 1):-1]  # 最新（当日）のデータを除いて、指定した時間枠でのOHLCVデータを取得
    high_prices = [float(x[1]) for x in ohlcv]  # 高値をリストとして取得（当日のデータは除外）
    low_prices = [float(x[2]) for x in ohlcv]  # 安値をリストとして取得（当日のデータは除外）
    high_max = max(high_prices)  # 高値の最大値を取得
    low_min = min(low_prices)  # 安値の最���値を取得
    # 計算結果を��力
    print(f"計算された高値: {high_max}, 計算された安値: {low_min}")

    # 現在価格を取得
    print("現在価格を取得します。")
    ticker = pub.get_ticker('xrp_jpy')  # Tickerデータを取得
    current_price = float(ticker['last'])  # 現在価格を取得
    print(f"取得された現在価格: {current_price}")

    # JPY残高を取得
    print("JPY残高を取得します。")
    assets = prv.get_asset()  # 資産情報を取得
    jpy_balance = float(assets['assets'][0]['free_amount'])  # JPYの残高を取得
    print(f"取得されたJPY残高: {jpy_balance}")

    # エントリー条件をチェック
    print("エントリー条件をチェックします。")
    if jpy_balance >= 10000 and current_position == 0:  # JPY残高が10000以上かつポジションがない場合
        price_diff = 1 - low_min / high_max  # 価格差を計算
        print(price_diff)
        if price_diff <= price_diff_percent and current_price < low_min:  # エントリー条件をチェック
            print("エントリー条件が満たされました。マーケットオーダーでエントリーします。")
            prv.order('xrp_jpy', None, order_lot, 'buy', 'market')  # マーケットオーダーでエントリー
            current_position = order_lot  # ポジションを更新
            entry_price = current_price  # エントリー価格を更新
            logging.info("Entered the position.")  # ログにエントリー情報を出力

    # イグジット条件をチェック
    print("イグジット条件をチェックします。")
    if current_position != 0:  # ポジションが存在する場合
        # 利益確定条件と損切り条件をチェック
        if current_price >= entry_price * (1 + exit_profit_percent / 100):
            print("利益確定条件が満たされました。ポジションをクローズします。")
            prv.order('xrp_jpy', None, current_position, 'sell', 'market')  # マーケットオーダーで利益確定
            current_position = 0  # ポジションをクリア
            logging.info("Exited the position with profit.")  # ログに利益確定情報を出力
        elif current_price <= entry_price * (1 - exit_loss_percent / 100):
            print("損切り条件が満たされました。ポジションをクローズします。")
            prv.order('xrp_jpy', None, current_position, 'sell', 'market')  # マーケットオーダーで損切り
            current_position = 0  # ポジションをクリア
            logging.info("Exited the position with loss.")  # ログに損切り情報を出力

    # 60秒待機
    print("60秒待機します。")
    time.sleep(60)  # 60秒間スリープ