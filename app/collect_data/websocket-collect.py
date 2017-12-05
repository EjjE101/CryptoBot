#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
import ujson
from pymongo import MongoClient
import time

# symbols = [
#             "btcusd","btceur",
#             "ltcusd", "ltcbtc",
#             "ethusd", "ethbtc",
#             "etcbtc", "etcusd",
#             "rrtusd", "rrtbtc",
#             "zecusd", "zecbtc",
#             "xmrusd", "xmrbtc",
#             "dshusd", "dshbtc",
#             "bccbtc", "bcubtc",
#             "bccusd","bcuusd",
#             "xrpusd","xrpbtc",
#             "iotusd","iotbtc","ioteth",
#             "eosusd","eosbtc","eoseth",
#             "sanusd","sanbtc","saneth",
#             "omgusd","omgbtc","omgeth",
#             "bchusd","bchbtc","bcheth",
#             "neousd","neobtc","neoeth",
#             "etpusd","etpbtc","etpeth",
#             "qtmusd","qtmbtc","qtmeth",
#             "bt1usd","bt2usd","bt1btc","bt2btc",
#             "avtusd","avtbtc","avteth",
#             "edousd","edobtc","edoeth",
#             "btgusd","btgbtc",
#             "datusd","datbtc","dateth",
#             "qshusd","qshbtc","qsheth",
#             "yywusd","yywbtc","yyweth"
# ]

symbols = [
            "btcusd","btceur",
            "ltcusd", "ltcbtc",
            "ethusd", "ethbtc"
]


class Client(object):

    def __init__(self, url, timeout):
        client = MongoClient()
        self.db = client.bitfinex
        self.url = url
        self.timeout = timeout
        self.ioloop = IOLoop.instance()
        self.ws = None
        self.cnt_msg = 0
        self.subs = False
        self.orderbooks = {}
        self.connect()
	    PeriodicCallback(self.keep_alive, 1000, io_loop=self.ioloop).start()
        self.ioloop.start()

    @gen.coroutine
    def connect(self):
        print "trying to connect"
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception, e:
            print "connection error"
        else:
            print "connected"
            self.run()

    @gen.coroutine
    def run(self):
        trds_chanid = {}
        book_chanid = {}
        while True:
            msg = yield self.ws.read_message()
            if msg is None:
                print "connection closed"
                self.ws = None
                break
            else:
                msg = ujson.loads(msg)
                self.cnt_msg += 1
                if 'event' in msg:
                    if msg['event'] == 'info':
                        for symbol in symbols:
                            self.conn_trades(symbol)
                            self.conn_orderbook(symbol)
                    elif msg['event'] == 'subscribed':
                        if msg['channel'] == 'trades':
                            trds_chanid[msg['symbol']] = msg['chanId']
                            print msg['symbol'] + "_trades connectie gemaakt"
                        if msg['channel'] == 'book':
                            book_chanid[msg['symbol']] = msg['chanId']
                            print msg['symbol']+ "_books connectie gemaakt"
                elif msg[0] in trds_chanid.values() and 'te' in msg:
                    for key,value in trds_chanid.items():
                        if value == msg[0]:
                            trade = {}
                            trade['_id'] = int(msg[2][0])
                            trade['timestamp'] = int(msg[2][1])
                            trade['amount'] = abs(float(msg[2][2]))
                            trade['price'] = float(msg[2][3])
                            if float(msg[2][2]) < 0:
                                trade['type'] = 'sell'
                            else:
                                trade['type'] = 'buy'
                            self.db[key + '_trades'].insert_one(trade)
                elif msg[0] in book_chanid.values():
                    for key,value in book_chanid.items():
                        if value == msg[0]:
                            self.build_book(msg[1], key)
                    self.subs = True


    def build_book(self, data, pair):
        if len(data) > 10:
            self.orderbooks[pair] = {}
            bids = {
                    str(level[0]): [str(level[1]), str(level[2])]
                    for level in data if level[2] > 0
            }

            asks = {
                    str(level[0]): [str(level[1]), str(level[2])[1:]]
                    for level in data if level[2] < 0
            }
            self.orderbooks[pair]['bids'] = bids
            self.orderbooks[pair]['asks'] = asks
        elif data[0] != 'h':
            data = [str(data[0]), str(data[1]), str(data[2])]
            if int(data[1]) > 0:  # 1.
                if float(data[2]) > 0:  # 1.1
                    self.orderbooks[pair]['bids'].update({data[0]: [data[1], data[2]]})
                elif float(data[2]) < 0:  # 1.2
                    self.orderbooks[pair]['asks'].update({data[0]: [data[1], str(data[2])[1:]]})
            elif data[1] == '0':  # 2.
                if data[2] == '1':  # 2.1
                    if self.orderbooks[pair]['bids'].get(data[0]):
                        del self.orderbooks[pair]['bids'][data[0]]
                elif data[2] == '-1':  # 2.2
                    if self.orderbooks[pair]['asks'].get(data[0]):
                        del self.orderbooks[pair]['asks'][data[0]]

    def conn_orderbook(self, pair):
        payload = ('{"event": "subscribe",'
                '"channel": "book",'
                '"symbol": "' + pair +'",'
                '"prec": "P0",'
                '"freq": "F0",'
                '"len": 25'
                '}')
        self.ws.write_message(payload)

    def conn_trades(self, pair):
        payload = ('{"event": "subscribe",'
                    '"channel": "trades",'
                    '"symbol": "' + pair + '"'
                    '}')
        self.ws.write_message(payload)

    def keep_alive(self):
        if self.ws is None:
            self.connect()
        elif self.subs:
            print "{} aantal berichten per seconden".format(self.cnt_msg)
            self.cnt_msg = 0
            for key in self.orderbooks.keys():
                bids = [[k, v[1]] for k, v in self.orderbooks[key]['bids'].items()]
                asks = [[k, v[1]] for k, v in self.orderbooks[key]['asks'].items()]
                bids.sort(key=lambda x: float(x[0]), reverse=True)
                asks.sort(key=lambda x: float(x[0]))
                book = {}
                book['_id'] = time.time()
                book['bids'] = [{'price': float(x[0]), 'amount': float(x[1])} for x in bids]
                book['asks'] = [{'price': float(x[0]), 'amount': float(x[1])} for x in asks]
                self.db[key + '_books'].insert_one(book)


if __name__ == "__main__":
    client = Client("wss://api.bitfinex.com/ws/2", 5)
