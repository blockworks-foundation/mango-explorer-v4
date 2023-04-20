import asyncio
import json
import logging
import argparse

from solana.transaction import Transaction
from solana.keypair import Keypair
from base58 import b58decode

from ..mango_client import MangoClient


async def main():
    logging.basicConfig(
        level=logging.INFO
    )

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--mango-account',
        help='Mango account primary key.',
        required=True
    )

    parser.add_argument(
        '--keypair',
        help='Solana wallet private key, to sign transactions for the Mango account.',
        required=True
    )

    args = parser.parse_args()

    mango_client = await MangoClient.connect()

    mango_account = await mango_client.get_mango_account(args.mango_account)

    keypair = Keypair.from_secret_key(b58decode(args.keypair))

    symbol = 'SOL/USDC'

    state = {
        'orderbook': None,
        'recent_blockhash': None
    }

    async def poll_orderbook():
        async for orderbook in mango_client.incremental_orderbook_l2(symbol, 5):
            state['orderbook'] = orderbook

    async def poll_blockhash():
        # All transactions require a Blockhash attached as metadata - rather than do the RPC
        # roundtrip on each transaction build just for this, poll it in the background
        async def poll():
            state['recent_blockhash'] = str((await mango_client.connection.get_latest_blockhash()).value.blockhash)

        while True: asyncio.ensure_future(poll()); await asyncio.sleep(1)

    asyncio.ensure_future(poll_orderbook())
    asyncio.ensure_future(poll_blockhash())

    while True:
        try:
            if state['recent_blockhash'] is None:
                raise ValueError("Blockchash hasn't polled yet, skipping quote...")

            mid_price = round((state['orderbook']['bids'][0][0] + state['orderbook']['asks'][0][0]) / 2, 3)

            spread = 500 / 1e4  # 500 bps

            orders = [{
                'symbol': symbol,
                'side': 'bids',
                'price': round(mid_price - (mid_price * spread), 3),
                'size': 1,  # TODO: Have here the minimum contract size
            }, {
                'symbol': symbol,
                'side': 'asks',
                'price': round(mid_price + (mid_price * spread), 3),
                'size': 1,
            }]

            serum3_cancel_all_orders_ix = mango_client.make_serum3_cancel_all_orders_ix(mango_account, 'SOL/USDC')

            serum3_place_order_ixs = [mango_client.make_serum3_place_order_ix(mango_account, **order) for order in orders]

            tx = Transaction()

            tx.add(serum3_cancel_all_orders_ix, *serum3_place_order_ixs)

            response = await mango_client.connection.send_transaction(tx, keypair, recent_blockhash=state['recent_blockhash'])

            logging.info(f"Quoted {json.dumps(orders)}: f{response.value}")
        except Exception as exception:
            logging.error(f"{exception}")
        finally:
            logging.info(f"1 second standby..."); await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
