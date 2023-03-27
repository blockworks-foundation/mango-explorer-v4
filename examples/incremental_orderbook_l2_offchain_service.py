import asyncio
import json
from operator import neg

import websockets
from sortedcontainers import SortedDict


class Orderbook:
    def __init__(
            self,
            bids: [[float, float]] = None,
            asks: [[float, float]] = None
    ):
        self.bids = SortedDict(neg)
        self.asks = SortedDict()

        if bids: self.bids.update({price: quantity for price, quantity in bids})

        if asks: self.asks.update({price: quantity for price, quantity in asks})


async def main():
    async for connection in websockets.connect('wss://api.mngo.cloud/orderbook/v1/'):
        await connection.send(json.dumps({
            'command': 'getMarkets'
        }))

        markets = json.loads(await connection.recv())

        # {
        #   "9Y8paZ5wUpzLFfQuHz8j2RtPrKsDtHx9sbgFmWb5abCw": "MNGO-PERP",
        #   "HwhVGkfsSQ9JSQeQYu2CbkRCLvsh3qRZxG6m4oMVwZpN": "BTC-PERP",
        #   "8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6": "SOL/USDC",
        #   "9Lyhks5bQQxb9EyyX55NtgKQzpM4WK7JCmeaWuQ5MoXD": "mSOL/USDC"
        # }

        orderbooks = {market_name: Orderbook() for market_name in markets.values()}

        await asyncio.gather(*[
            connection.send(
                json.dumps({
                    'command': 'subscribe',
                    'marketId': market_id
                })
            )
            for market_id in markets.keys()
        ])

        async for raw_message in connection:
            message = json.loads(raw_message)

            if 'market' not in message:
                continue

            is_snapshot = 'side' not in message

            market_name = markets[message['market']]

            orderbook = orderbooks[market_name]

            if is_snapshot:
                for side in ['bids', 'asks']:
                    suborderbook = getattr(orderbook, side)

                    suborderbook.clear(); suborderbook.update({price: size for price, size in message[side]})

                continue

            suborderbook = getattr(orderbook, {'bid': 'bids', 'ask': 'asks'}[message['side']])

            for price, size in message['update']:
                if size == 0:
                    suborderbook.pop(price)
                else:
                    suborderbook.update({price: size})

            print({'symbol': market_name, 'bids': orderbook.bids, 'asks': orderbook.asks})


if __name__ == '__main__':
    asyncio.run(main())
