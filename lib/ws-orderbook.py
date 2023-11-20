import socketio

class Bitbank():
    def __init__(self) -> None:
        self.order_book = {'asks': {}, 'bids': {}}
        self.last_price = 0
        self.sell = 0
        self.buy = 0
        self.pair_name = 'btc_jpy'
        self.wss = 'wss://stream.bitbank.cc'
        self.room_name = {
            'whole' : 'depth_whole_{}'.format(self.pair_name),
            'diff'  : 'depth_diff_{}'.format(self.pair_name),
            'ticker': 'ticker_{}'.format(self.pair_name),
        }

    def on_connect(self):
        sio.on('message', self.on_data)
        sio.emit('join-room', self.room_name['whole'])
        sio.emit('join-room', self.room_name['diff'])
        sio.emit('join-room', self.room_name['ticker'])

    def on_data(self, data):
        # 板情報を取得する
        if data['room_name'] == self.room_name['whole']:
            self.order_book['asks'] = {item[0]: item[1] for item in data['message']['data']['asks']}
            self.order_book['bids'] = {item[0]: item[1] for item in data['message']['data']['bids']}
        elif data['room_name'] == self.room_name['diff']:
            # 更新データを適用
            for side in ['a', 'b']:
                # 'a' corresponds to 'asks' and 'b' to 'bids'
                side_full = 'asks' if side == 'a' else 'bids'
                # sideが空リストでないことを確認
                if data['message']['data'][side]:
                    for price, quantity in data['message']['data'][side]:
                        if quantity == '0':
                            # 注文のキャンセルまたは完全な約定
                            if price in self.order_book[side_full]:
                                del self.order_book[side_full][price]
                        else:
                            # 新規注文または部分的な約定
                            self.order_book[side_full][price] = quantity

        # ticker情報を取得する
        if data['room_name'] == self.room_name['ticker']:
            self.last_price = data['message']['data']['last']
            self.sell = data['message']['data']['sell']
            self.buy = data['message']['data']['buy']

        # 取得した情報をprintする
        # 直感的に理解しやすいように取引画面の板情報と同じような表示にしておく
        sorted_asks = sorted(self.order_book['asks'].items(), key=lambda x: x[0])[:10]
        sorted_bids = sorted(self.order_book['bids'].items(), key=lambda x: x[0], reverse=True)[:10]
        for i, v in enumerate(reversed(sorted_asks)):
            print(v[1], v[0], '', sep='\t')
        print('', self.last_price, '', sep='\t')
        for i, v in enumerate(sorted_bids):
            print('', v[0], v[1], sep='\t')
        print('--------------------------------')

try:
    sio = socketio.Client(
        reconnection=True,
        reconnection_attempts=0,
        reconnection_delay=1,
        reconnection_delay_max=30
    )
    BB = Bitbank()
    sio.on('connect', BB.on_connect)
    sio.connect(BB.wss, transports=['websocket'])
    sio.wait()
except Exception as e:
    print(e)