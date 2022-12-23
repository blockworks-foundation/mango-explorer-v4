import asyncio
import json
import pathlib

from solana.transaction import Transaction

from mango_explorer_v4.mango_client import MangoClient


async def main():
    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

    symbol = 'SOL/USDC'

    orderbook = await mango_client.orderbook_l2(symbol)

    mid_price = (orderbook['bids'][0][0] + orderbook['asks'][0][0]) / 2

    spread = 500 / 1e4  # bps

    orders = [{
        'symbol': symbol,
        'side': 'bid',
        'price': mid_price - (mid_price * spread),
        'size': 1,  # TODO: Have here the minimum contract size
    }, {
        'symbol': symbol,
        'side': 'ask',
        'price': mid_price + (mid_price * spread),
        'size': 1,
    }]

    serum3_cancel_all_orders_ix = mango_client.make_serum3_cancel_all_orders_ix('SOL/USDC')

    serum3_place_order_ixs = map(lambda order: mango_client.make_serum3_place_order_ix(**order), orders)

    tx = Transaction()

    tx.add(serum3_cancel_all_orders_ix, *serum3_place_order_ixs)

    recent_blockhash = (await mango_client.provider.connection.get_latest_blockhash()).value.blockhash

    tx.recent_blockhash = str(recent_blockhash)

    tx.sign(mango_client.provider.wallet.payer)

    print(await mango_client.provider.send(tx))


if __name__ == '__main__':
    asyncio.run(main())
