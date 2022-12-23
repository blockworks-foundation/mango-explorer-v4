import asyncio
import json
import re

import websockets

from mango_explorer_v4.accounts.event_queue import EventQueue


async def main():
    async for connection in websockets.connect('wss://api.mngo.cloud/fills/v1/'):
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

        print(markets)

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

            if not 'slot' in message:
                continue

            is_snapshot = 'events' in message

            market_name = markets[message['market']]

            market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", market_name)[1]]

            if is_snapshot:
                match market_type:
                    case 'perpetual':
                        print(len(message['events']))
                        # print(EventQueue.decode(message['events']))
            else:
                pass
                # print(message, market_name, market_type)



if __name__ == '__main__':
    asyncio.run(main())
