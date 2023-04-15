import argparse
import asyncio
import json
import pathlib

from base58 import b58decode
from solana.keypair import Keypair

from mango_explorer_v4.mango_client import MangoClient


async def main():
    parser = argparse.ArgumentParser()

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

    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect()

    keypair = Keypair.from_secret_key(b58decode(config['secret_key']))

    mango_account = await mango_client.get_mango_account(config['mango_account_pk'])

    print(await mango_client.place_order(args.symbol, args.side, args.price, args.size, mango_account, keypair))

    # e.g 3VQA4zqmRPLtmeHBNV2dKZKhXYX3cHBiM1LpCrjgJZwZDF418GF6RQ9DihSZq6Zg4pjqcUjTMQwEDNLuybfL8mQT
    # (Check the UI)


if __name__ == '__main__':
    asyncio.run(main())