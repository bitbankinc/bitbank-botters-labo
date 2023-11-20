import requests
import time
import logging

import pandas as pd
# !pip install mplfinance
import mplfinance as mpf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

class BitbankGetCandlestickToCsv(object):
    def __init__(self, pair, start_date, end_date, candle_type):
        self.pair = pair
        self.start_date = start_date
        self.end_date = end_date
        self.date_list = []
        self.candle_type = candle_type
        self.candlestick_df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume', 'time'])
        self._create_date_list()
        self._create_candlestick_df()
        self._set_float()

    def _get_candlestick(self, time):
        api_endpoint = 'https://public.bitbank.cc'
        endpoint = f'{api_endpoint}/{self.pair}/candlestick/{self.candle_type}/{time}'
        response = requests.get(endpoint)
        return response.json()

    def _create_date_list(self):
        dt_start_date = pd.to_datetime(self.start_date, format='%Y%m%d')
        dt_end_date = pd.to_datetime(self.end_date, format='%Y%m%d')
        if self.candle_type in ['1min', '5min', '15min', '30min', '1hour']:
            self.date_list = pd.date_range(start=dt_start_date, end=dt_end_date, freq='D').strftime('%Y%m%d').tolist()
        else:
            self.date_list = [str(year) for year in range(dt_start_date.year, dt_end_date.year + 1)]

    def _create_candlestick_df(self):
        for date in self.date_list:
            data = self._get_candlestick(date)
            if 'data' in data and 'candlestick' in data['data']:
                ohlcv = data['data']['candlestick'][0]['ohlcv']
                df = pd.DataFrame(ohlcv, columns=['open', 'high', 'low', 'close', 'volume', 'unix_time_ms'])
                df['time'] = pd.to_datetime(df['unix_time_ms'], unit='ms')
                df = df[(df['time'] >= self.start_date) & (df['time'] <= self.end_date)]
                df = df.drop(columns=['unix_time_ms'])
                self.candlestick_df = pd.concat([self.candlestick_df, df], ignore_index=True)
            else:
                logger.error(f'KeyError: {date}:{data}')
            time.sleep(0.1)

    def _set_float(self):
        self.candlestick_df['open'] = self.candlestick_df['open'].astype(float)
        self.candlestick_df['high'] = self.candlestick_df['high'].astype(float)
        self.candlestick_df['low'] = self.candlestick_df['low'].astype(float)
        self.candlestick_df['close'] = self.candlestick_df['close'].astype(float)
        self.candlestick_df['volume'] = self.candlestick_df['volume'].astype(float)  # 'volume' 列を float に変換

    def to_csv(self, name):
        self.candlestick_df.to_csv(name, index=False)
        first_date = self.candlestick_df['time'].iloc[0]
        last_date = self.candlestick_df['time'].iloc[-1]
        print(f'pair: {self.pair}\ncandle-type: {self.candle_type}\nterm: {first_date} 〜 {last_date}\ncreated csv')

    def plot_line(self):
        df = self.candlestick_df.set_index('time') 
        mpf.plot(df, type='line', style='default', title=f'{self.pair}({self.candle_type})', ylabel='Price')

    def plot_candlestick(self, width=1):
        df = self.candlestick_df.set_index('time')
        mpf.plot(df, type='candle', style='default', title=f'{self.pair}({self.candle_type})', ylabel='Price')

# pairを設定
pair = 'btc_jpy'

# 取得したい期間の日付を設定
start_date = '20200101'
end_date = '20231109'

# candle_typeを設定
# '1min', '5min', '15min', '30min', '1hour', '4hour', '8hour', '12hour', '1day', '1week', '1month'
candle_type = '1day'

# main
bb_candlestick = BitbankGetCandlestickToCsv(pair, start_date, end_date, candle_type)
bb_candlestick.to_csv(f'{pair}_{candle_type}_{start_date}-{end_date}.csv')
bb_candlestick.plot_candlestick()
