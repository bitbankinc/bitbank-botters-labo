import time
import logging
import python_bitbankcc

# ログレベルをINFOに設定
logging.basicConfig(level=logging.INFO)

# 初期設定
print("初期設定を行います。")
API_KEY = ''
API_SECRET = ''
pub = python_bitbankcc.public()
prv = python_bitbankcc.private(API_KEY, API_SECRET)

# 各種パラメータ
print("各種パラメータを設定します。")
order_lot = 500
time_frame = 11
price_diff_percent = 0.97
exit_profit_percent = 0.27
exit_loss_percent = 0.04

# ポジション情報
current_position = 0
entry_price = 0

while True:
    print("高値・安値を計算します。")
    value = pub.get_candlestick('xrp_jpy', '1day', '2023')
    ohlcv = value['candlestick'][0]['ohlcv'][-time_frame:]
    high_prices = [float(x[1]) for x in ohlcv]
    low_prices = [float(x[2]) for x in ohlcv]
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
        if price_diff <= price_diff_percent and current_price > high_max:
            print("エントリー条件が満たされました。マーケットオーダーでエントリーします。")
            prv.order('xrp_jpy', None, order_lot, 'buy', 'market')
            current_position = order_lot
            entry_price = current_price
            logging.info("Entered the position.")

    print("イグジト条件をチェックします。")
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