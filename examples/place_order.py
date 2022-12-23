import argparse
import asyncio
import json
import pathlib

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

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

    # print(await mango_client.place_order('SOL/USDC', 'bid', 10, 0.1))

    print(await mango_client.place_order(args.symbol, args.side, args.price, args.size))

    # 3VQA4zqmRPLtmeHBNV2dKZKhXYX3cHBiM1LpCrjgJZwZDF418GF6RQ9DihSZq6Zg4pjqcUjTMQwEDNLuybfL8mQT
    # (Check the UI)


if __name__ == '__main__':
    asyncio.run(main())