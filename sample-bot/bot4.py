# 2023/10/30エラーハンドリングテスト
# BNBbot

import time
import logging
import python_bitbankcc
from datetime import datetime, timedelta
import requests

logging.basicConfig(level=logging.INFO)

API_KEY = ''  # APIキーを設定
API_SECRET = ''  # APIシークレットを設定
pub = python_bitbankcc.public()
prv = python_bitbankcc.private(API_KEY, API_SECRET)

order_lot = 0.03  # 注文量を設定
time_frame = 25  # 時間枠を設定
price_diff_percent = 1  # 価格差のパーセンテージを設定
exit_profit_percent = 2  # 利益確定のパーセンテージを設定
exit_loss_percent = 0.3  # 損切りのパーセンテージを設定

current_position = 0
entry_price = 0

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
        current_price = float(ticker['last'])
        print(f"現在の価格: {current_price}")

        assets = prv.get_asset()
        jpy_balance = float(assets['assets'][0]['free_amount'])
        print(f"JPY残高: {jpy_balance}")

        if jpy_balance >= 10000 and current_position == 0:
            price_diff = 1 - low_min / high_max
            if price_diff <= price_diff_percent and current_price < low_min:
                prv.order('bnb_jpy', None, order_lot, 'buy', 'market')
                current_position = order_lot
                entry_price = current_price
                logging.info("ポジションを取得しました。")

        if current_position != 0:
            if current_price >= entry_price * (1 + exit_profit_percent / 100):
                prv.order('bnb_jpy', None, current_position, 'sell', 'market')
                current_position = 0
                logging.info("利益確定でポジションを解消しました。")
            elif current_price <= entry_price * (1 - exit_loss_percent / 100):
                prv.order('bnb_jpy', None, current_position, 'sell', 'market')
                current_position = 0
                logging.info("損切りでポジションを解消しました。")

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

