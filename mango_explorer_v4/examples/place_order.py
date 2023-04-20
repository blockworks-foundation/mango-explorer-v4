import argparse
import asyncio

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
        type=float
    )

    parser.add_argument(
        '--size',
        type=float
    )

    args = parser.parse_args()

    mango_client = await MangoClient.connect()

    keypair = Keypair.from_secret_key(b58decode(args.keypair))

    mango_account = await mango_client.get_mango_account(args.mango_account)

    print(await mango_client.place_order(args.symbol, args.side, args.price, args.size, mango_account, keypair))

    # e.g 3VQA4zqmRPLtmeHBNV2dKZKhXYX3cHBiM1LpCrjgJZwZDF418GF6RQ9DihSZq6Zg4pjqcUjTMQwEDNLuybfL8mQT
    # (Check the UI)


if __name__ == '__main__':
    asyncio.run(main())