import aiohttp
import asyncio
import ujson
from copy import deepcopy
import time
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client.bitfinex

# Pairs which generate orderbook for.
PAIRS = [
             "btcusd",
#             "btceur",
#             "ltcusd",
             "ltcbtc",
#             "ethusd",
             "ethbtc",
#             "etcbtc", "etcusd",
##             "rrtusd", "rrtbtc",
##             "zecusd", "zecbtc",
#             "xmrusd", "xmrbtc",
#             "dshusd",
             "dshbtc",
##             "bccbtc", "bcubtc",
##             "bccusd","bcuusd",
#             "xrpusd",
#             "xrpbtc",
             "iotusd",
             "iotbtc",
#             "ioteth",
#             "eosusd",
             "eosbtc",
#              "eoseth",
#             "sanusd","sanbtc","saneth",
#             "omgusd","omgbtc","omgeth",
#             "bchusd","bchbtc","bcheth",
#             "neousd","neobtc","neoeth",
##             "etpusd","etpbtc","etpeth",
##             "qtmusd","qtmbtc","qtmeth",
##             "bt1usd","bt2usd","bt1btc","bt2btc",
##             "avtusd","avtbtc","avteth",
##             "edousd","edobtc","edoeth",
##             "btgusd","btgbtc",
##             "datusd","datbtc","dateth",
##             "qshusd","qshbtc","qsheth",
##             "yywusd","yywbtc","yyweth"
]



# If there is n pairs we need to subscribe to n websocket channels.
# This the subscription message template.
# For details about settings refer to https://bitfinex.readme.io/v2/reference#ws-public-order-books.
BOOK_SUB_MESG = {
                  "event": "subscribe",
                  "channel": "book",
                  # "symbol": "tBTCUSD",
                  "prec": "P0",
                  "freq": "F0",
                  "len": 25
                }

TRADES_SUB_MESG = {
                      "event": "subscribe",
                      "channel": "trades",
                      # "symbol": "tBTCUSD"
                }


def build_book(res, pair):
    """ Updates orderbook.
    :param res: Orderbook update message.
    :param pair: Updated pair.

    """

    global orderbooks

    # Filter out subscription status messages.
    if res.data[0] == '[':
        # String to json
        data = ujson.loads(res.data)[1]

        # Build orderbook
        # Observe the structure of orderbook. The prices are keys for corresponding count and amount.
        # Structuring data in this way significantly simplifies orderbook updates.
        if len(data) > 10:
            bids = {
                       str(level[0]): [str(level[1]), str(level[2])]
                       for level in data if level[2] > 0
            }
            asks = {
                       str(level[0]): [str(level[1]), str(level[2])[1:]]
                       for level in data if level[2] < 0
            }
            orderbooks[pair]['bids'] = bids
            orderbooks[pair]['asks'] = asks

        # Update orderbook and filter out heartbeat messages.
        elif data[0] != 'h':

            # Example update message structure [1765.2, 0, 1] where we have [price, count, amount].
            # Update algorithm pseudocode from Bitfinex documentation:
            # 1. - When count > 0 then you have to add or update the price level.
            #   1.1- If amount > 0 then add/update bids.
            #   1.2- If amount < 0 then add/update asks.
            # 2. - When count = 0 then you have to delete the price level.
            #   2.1- If amount = 1 then remove from bids
            #   2.2- If amount = -1 then remove from asks
            data = [str(data[0]), str(data[1]), str(data[2])]
            if int(data[1]) > 0:  # 1.
                if float(data[2]) > 0:  # 1.1
                    orderbooks[pair]['bids'].update({data[0]: [data[1], data[2]]})
                elif float(data[2]) < 0:  # 1.2
                    orderbooks[pair]['asks'].update({data[0]: [data[1], str(data[2])[1:]]})
            elif data[1] == '0':  # 2.
                if data[2] == '1':  # 2.1
                    if orderbooks[pair]['bids'].get(data[0]):
                        del orderbooks[pair]['bids'][data[0]]
                elif data[2] == '-1':  # 2.2
                    if orderbooks[pair]['asks'].get(data[0]):
                        del orderbooks[pair]['asks'][data[0]]

async def save_books():
    """ Prints orderbooks snapshots for all pairs every 10 seconds. """
    global orderbooks
    global cnt_msg

    # give it time to create all orderbooks.
    await asyncio.sleep(30)
    exc_time = 0

    while 1:
        start_time = time.time()
        for pair in PAIRS:
            bids = [[k, v[1]] for k, v in orderbooks[pair]['bids'].items()]
            asks = [[k, v[1]] for k, v in orderbooks[pair]['asks'].items()]
            bids.sort(key=lambda x: float(x[0]))
            asks.sort(key=lambda x: float(x[0]))
            book = {}
            book['_id'] = time.time()
            book['bids'] = [{'price': float(x[0]), 'amount': float(x[1])} for x in bids]
            book['asks'] = [{'price': float(x[0]), 'amount': float(x[1])} for x in asks]
            result = await db[pair + '_books'].insert_one(book)
        # print('msg per sec: {}'.format(cnt_msg)) # debug
        cnt_msg = 0 # debug
        exc_time = time.time() - start_time
        await asyncio.sleep(1-exc_time)


async def get_book(pair, session):
    """ Subscribes for orderbook updates """
    global cnt_msg
    print('enter get_book, pair: {}'.format(pair))
    pair_dict = deepcopy(BOOK_SUB_MESG)
    pair_dict.update({'symbol': 't'+pair.upper()})
    async with session.ws_connect('wss://api.bitfinex.com/ws/2') as ws:
        ws.send_json(pair_dict)
        while 1:
            res = await ws.receive()
            cnt_msg += 1
            # print(pair_dict['symbol'], res.data)  # debug
            build_book(res, pair)

async def get_trades(pair, session):
    """ Subscribes for orderbook updates """
    global cnt_msg
    print('enter get_trades, pair: {}'.format(pair))
    pair_dict = deepcopy(TRADES_SUB_MESG)
    pair_dict.update({'symbol': 't'+pair.upper()})
    async with session.ws_connect('wss://api.bitfinex.com/ws/2') as ws:
        ws.send_json(pair_dict)
        while 1:
            res =  await ws.receive()
            cnt_msg += 1
            # print(pair_dict['symbol'], res.data)  # debug
            if 'tu' in res.data:
                res = ujson.loads(res.data)
                trade = {}
                trade['_id'] = int(res[2][0])
                trade['timestamp'] = int(res[2][1])
                trade['amount'] = abs(float(res[2][2]))
                trade['price'] = float(res[2][3])
                if float(res[2][2]) < 0:
                    trade['type'] = 'sell'
                else:
                    trade['type'] = 'buy'
                result = await db[pair + '_trades'].insert_one(trade)

async def main():
    """ Driver coroutine. """
    async with aiohttp.ClientSession() as session:
        coros = []
        for pair in PAIRS:
            coros.append(get_book(pair, session))
            coros.append(get_trades(pair, session))

        coros.append(save_books())
        print('Data collection running')
        await asyncio.wait(coros)

orderbooks = {
    pair: {}
    for pair in PAIRS
}

cnt_msg = 0

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
