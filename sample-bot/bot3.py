# 逆ナベbot｜XRP逆張り｜上げ相場対応板

import time
import logging
import python_bitbankcc
import datetime
from datetime import datetime, timedelta
import requests

logging.basicConfig(level=logging.INFO)

print("初期設定を行います。")
API_KEY = ''  # APIキーを設定
API_SECRET = ''  # APIシークレットを設定
pub = python_bitbankcc.public()
prv = python_bitbankcc.private(API_KEY, API_SECRET)

# 各種パラメータ
print("各種パラメータを設定します。")
order_lot = 49  # 注文量を設定
time_frame = 8  # 時間枠を設定
price_diff_percent = 1  # 価格差のパーセンテージを設定
exit_profit_percent = 5  # 利益確定のパーセンテージを設定
exit_loss_percent = 0.75  # 損切りのパーセンテージを設定

current_position = 0
entry_price = 0

while True:
    try:
      current_date = datetime.now().strftime('%Y%m%d')
      yesterday_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')

      ohlcv_combined = []

      # 昨日のデータを取得
      value_yesterday = pub.get_candlestick('xrp_jpy', '1hour', yesterday_date)
      ohlcv_yesterday = value_yesterday.get('candlestick', [{}])[0].get('ohlcv', [])
      if ohlcv_yesterday:
          ohlcv_combined += ohlcv_yesterday

      # 今日のデータを取得
      value_today = pub.get_candlestick('xrp_jpy', '1hour', current_date)
      ohlcv_today = value_today.get('candlestick', [{}])[0].get('ohlcv', [])
      if ohlcv_today:
          ohlcv_combined += ohlcv_today

      if not ohlcv_combined:
          print("ローソク足データが存在しないため、スキップします。")
          continue

      ohlcv_filtered = ohlcv_combined[-(time_frame + 1):-1]

      high_prices = [float(x[1]) for x in ohlcv_filtered]
      low_prices = [float(x[2]) for x in ohlcv_filtered]

      high_max = max(high_prices)
      low_min = min(low_prices)

      print(f"計算された高値: {high_max}, 計算された安値: {low_min}")

      print("現在価格を取得します。")
      ticker = pub.get_ticker('xrp_jpy')
      current_price = float(ticker['last'])
      print(f"取得された現在価格: {current_price}")

      print("JPY残高を取得します。")
      assets = prv.get_asset()
      jpy_balance = float(assets['assets'][0]['free_amount'])
      print(f"取得されたJPY残高: {jpy_balance}")

      print("エントリー条件をチェックします。")
      if jpy_balance >= 10000 and current_position == 0:
          price_diff = 1 - low_min / high_max
          print(price_diff)
          if price_diff <= price_diff_percent and current_price < low_min:
              print("エントリー条件が満たされました。マーケットオーダーでエントリーします。")
              prv.order('xrp_jpy', None, order_lot, 'buy', 'market')
              current_position = order_lot
              entry_price = current_price
              logging.info("Entered the position.")

      print("イグジット条件をチェックします。")
      if current_position != 0:
          if current_price >= entry_price * (1 + exit_profit_percent / 100):
              print("利益確定条件が満たされました。ポジションをクローズします。")
              prv.order('xrp_jpy', None, current_position, 'sell', 'market')
              current_position = 0
              logging.info("Exited the position with profit.")
          elif current_price <= entry_price * (1 - exit_loss_percent / 100):
              print("損切り条件が満たされました。ポジションをクローズします。")
              prv.order('xrp_jpy', None, current_position, 'sell', 'market')
              current_position = 0
              logging.info("Exited the position with loss.")

      print("60秒待機します。")
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