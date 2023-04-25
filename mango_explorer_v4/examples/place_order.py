import argparse
import asyncio
import time

from base58 import b58decode
from solana.keypair import Keypair

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

    parser.add_argument(
        '--symbol',
        required=True
    )

    parser.add_argument(
        '--side',
        required=True,
        choices=['bids', 'asks']
    )

    parser.add_argument(
        '--price',
        type=float,
        required=True
    )

    parser.add_argument(
        '--size',
        type=float,
        required=True
    )

    parser.add_argument(
        '--mode',
        type=str,
        required=False,
        default='Limit',
        choices=['Limit', 'ImmediateOrCancel', 'PostOnly']
    )

    parser.add_argument(
        '--client-order-id',
        type=int,
        required=False,
        default=int(time.time_ns() / 1e6)
    )

    args = parser.parse_args()

    mango_client = await MangoClient.connect()

    keypair = Keypair.from_secret_key(b58decode(args.keypair))

    mango_account = await mango_client.get_mango_account(args.mango_account)

    print(await mango_client.place_order(mango_account, keypair, args.symbol, args.side, args.price, args.size, args.mode, args.client_order_id))

    # e.g 3VQA4zqmRPLtmeHBNV2dKZKhXYX3cHBiM1LpCrjgJZwZDF418GF6RQ9DihSZq6Zg4pjqcUjTMQwEDNLuybfL8mQT
    # (Check the UI)


if __name__ == '__main__':
    asyncio.run(main())