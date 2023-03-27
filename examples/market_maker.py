import asyncio
import json
import logging
import pathlib
import argparse

from solana.transaction import Transaction

from mango_explorer_v4.mango_client import MangoClient

async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--symbol',
        required=True
    )

    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

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
            state['recent_blockhash'] = str((await mango_client.provider.connection.get_latest_blockhash()).value.blockhash)

        while True: asyncio.ensure_future(poll()); await asyncio.sleep(1)

    asyncio.ensure_future(poll_orderbook())
    asyncio.ensure_future(poll_blockhash())

    while True:
        try:
            mid_price = round((state['orderbook']['bids'][0][0] + state['orderbook']['asks'][0][0]) / 2, 3)

            spread = 50 / 1e4  # 50 bps

            orders = [{
                'symbol': symbol,
                'side': 'bid',
                'price': round(mid_price - (mid_price * spread), 3),
                'size': 1,  # TODO: Have here the minimum contract size
            }, {
                'symbol': symbol,
                'side': 'ask',
                'price': round(mid_price + (mid_price * spread), 3),
                'size': 1,
            }]

            serum3_cancel_all_orders_ix = mango_client.make_serum3_cancel_all_orders_ix('SOL/USDC')

            serum3_place_order_ixs = map(lambda order: mango_client.make_serum3_place_order_ix(**order), orders)

            tx = Transaction()

            tx.add(serum3_cancel_all_orders_ix, *serum3_place_order_ixs)

            tx.recent_blockhash = state['recent_blockhash']

            tx.sign(mango_client.provider.wallet.payer)

            response = await mango_client.provider.send(tx)

            print(f"Quoted {json.dumps(orders)}: f{response}")
        except Exception as exception:
            logging.error(f"{exception}")
        finally:
            logging.info(f"Standby..."); await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
