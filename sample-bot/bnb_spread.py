# スプレッドの計測

import python_bitbankcc
import pandas as pd
import time
from datetime import datetime, timedelta

# APIクライアントを設定（公開APIのみ使用するため、APIキーは必要ありません）
client = python_bitbankcc.public()

def get_bnb_jpy_ticker():
    """
    BitbankのAPIからBNB_JPYの現在の売り買い価格を取得します。
    """
    ticker = client.get_ticker(pair='bnb_jpy')
    return {
        'sell': float(ticker['sell']),
        'buy': float(ticker['buy']),
        'timestamp': datetime.now()
    }

def main():
    start_time = datetime.now()
    data = []

    while True:
        ticker_data = get_bnb_jpy_ticker()
        data.append(ticker_data)
        print(f"{ticker_data['timestamp']}時点のデータ取得: 売り = {ticker_data['sell']}, 買い = {ticker_data['buy']}")

        # 60秒待つ
        time.sleep(60)

        # 4時間ごとにCSVにデータを保存
        if datetime.now() - start_time >= timedelta(hours=4):
            df = pd.DataFrame(data)
            csv_filename = f"bnb_jpy_data_{start_time.strftime('%Y%m%d%H%M%S')}.csv"
            df.to_csv(csv_filename, index=False)
            print(f"データを{csv_filename}に保存しました")

            # 開始時間とデータをリセット
            start_time = datetime.now()
            data = []

if __name__ == "__main__":
    main()