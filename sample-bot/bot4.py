# 2023/10/30エラーハンドリングテスト
# BNBbot

import time
import logging
import python_bitbankcc
from datetime import datetime, timedelta
import requests
import csv  # CSV操作用のライブラリをインポート

logging.basicConfig(level=logging.INFO)

API_KEY = ''  # APIキーを設定
API_SECRET = ''  # APIシークレットを設定
pub = python_bitbankcc.public()
prv = python_bitbankcc.private(API_KEY, API_SECRET)

order_lot = 0.028  # 注文量を設定
time_frame = 25  # 時間枠を設定
price_diff_percent = 1  # 価格差のパーセンテージを設定
exit_profit_percent = 2.27  # 利益確定のパーセンテージを設定
exit_loss_percent = 0.57  # 損切りのパーセンテージを設定

current_position = 0
entry_price = 0
order_history = []  # order_idを保存するためのリスト
last_save_time = time.time()  # CSVを最後に保存した時間を記録

# order_idをCSVとして保存する関数
def save_order_history_to_csv():
    filename = f"revise_revise_bot4_order_history_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Order ID"])
        for order_id in order_history:
            writer.writerow([order_id])
    print(f"Saved order history to {filename}")

while True:
    try:
        current_date = datetime.now().strftime('%Y%m%d')
        yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

        ohlcv_combined = []

        value_yesterday = pub.get_candlestick('bnb_jpy', '1min', yesterday_date)
        ohlcv_yesterday = value_yesterday.get('candlestick', [{}])[0].get('ohlcv', [])
        ohlcv_combined += ohlcv_yesterday

        value_today = pub.get_candlestick('bnb_jpy', '1min', current_date)
        ohlcv_today = value_today.get('candlestick', [{}])[0].get('ohlcv', [])
        ohlcv_combined += ohlcv_today

        ohlcv_filtered = ohlcv_combined[-(time_frame + 1):-1]

        high_prices = [float(x[1]) for x in ohlcv_filtered]
        low_prices = [float(x[2]) for x in ohlcv_filtered]

        high_max = max(high_prices)
        low_min = min(low_prices)

        print(f"計算された最高値: {high_max}, 計算された最低値: {low_min}")

        ticker = pub.get_ticker('bnb_jpy')
        current_price_entry = float(ticker['sell'])  # Best ask price for entry
        current_price_exit = float(ticker['buy'])  # Best bid price for exit
        print(f"現在のエントリー価格: {current_price_entry}")
        print(f"現在のイグジット価格: {current_price_exit}")

        assets = prv.get_asset()
        jpy_balance = float(assets['assets'][0]['free_amount'])
        print(f"JPY残高: {jpy_balance}")

        if jpy_balance >= 10000 and current_position == 0:
            price_diff = 1 - low_min / high_max
            if price_diff <= price_diff_percent and current_price_entry < low_min:
                order_result = prv.order('bnb_jpy', None, order_lot, 'buy', 'market')
                current_position = order_lot
                entry_price = current_price_entry  # Use the entry price
                order_history.append(order_result['order_id'])  # order_idをリストに追加
                logging.info(f"Entered the position with order_id: {order_result['order_id']}")

        if current_position != 0:
            if current_price_exit >= entry_price * (1 + exit_profit_percent / 100):
                order_result = prv.order('bnb_jpy', None, current_position, 'sell', 'market')
                current_position = 0
                order_history.append(order_result['order_id'])  # order_idをリストに追加
                logging.info(f"Exited the position with profit, order_id: {order_result['order_id']}")
            elif current_price_exit <= entry_price * (1 - exit_loss_percent / 100):
                order_result = prv.order('bnb_jpy', None, current_position, 'sell', 'market')
                current_position = 0
                order_history.append(order_result['order_id'])  # order_idをリストに追加
                logging.info(f"Exited the position with loss, order_id: {order_result['order_id']}")

        # CSVファイルを定期的に保存
        current_time = time.time()
        if current_time - last_save_time >= 86400:  # 24時間ごとにCSVとして保存
            save_order_history_to_csv()
            last_save_time = current_time

        time.sleep(60)

    except requests.exceptions.RequestException as e:
        print(f"リクエスト例外が発生: {e}")
        if e.response:
            http_status_code = e.response.status_code
            if http_status_code == 429:  # Rate limit exceeded
                print("レート制限に達しました。15秒待機します。")
                time.sleep(15)
            else:
                print(f"HTTPステータスコード {http_status_code} を受け取りました。15秒待機します。")
                time.sleep(15)
        else:
            print("不明なエラーが発生しました。15秒待機します。")
            time.sleep(15)