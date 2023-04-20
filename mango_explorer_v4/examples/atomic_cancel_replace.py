import argparse
import asyncio

from base58 import b58decode
from solana.keypair import Keypair
from solana.transaction import Transaction

from ..mango_client import MangoClient


async def main():
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

    orderbook = await mango_client.orderbook_l2(symbol)

    mid_price = (orderbook['bids'][0][0] + orderbook['asks'][0][0]) / 2

    spread = 500 / 1e4  # bps

    orders = [{
        'symbol': symbol,
        'side': 'bids',
        'price': mid_price - (mid_price * spread),
        'size': 1,  # TODO: Have here the minimum order size
    }, {
        'symbol': symbol,
        'side': 'asks',
        'price': mid_price + (mid_price * spread),
        'size': 1,
    }]

    serum3_cancel_all_orders_ix = mango_client.make_serum3_cancel_all_orders_ix(mango_account, symbol)

    serum3_place_order_ixs = map(lambda order: mango_client.make_serum3_place_order_ix(mango_account, **order), orders)

    tx = Transaction()

    tx.add(serum3_cancel_all_orders_ix, *serum3_place_order_ixs)

    recent_blockhash = str((await mango_client.connection.get_latest_blockhash()).value.blockhash)

    try:
        await mango_client.connection.send_transaction(tx, keypair, recent_blockhash=recent_blockhash); print(f"Quoted: {orders}")
    except Exception as exception:
        print(f"{exception}")

if __name__ == '__main__':
    asyncio.run(main())
