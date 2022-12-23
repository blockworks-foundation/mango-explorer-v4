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
        '--depth',
        default=50,
        type=int
    )

    args = parser.parse_args()

    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

    print(await mango_client.orderbook_l2(args.symbol, args.depth))

    # {
    #   'symbol': 'SOL/USDC',
    #   'slot': 168616506,
    #   'bids': [
    #       [11.826, 0.899],
    #       [11.824, 39.436],
    #       [11.82, 316.421],
    #       [11.817, 1.43],
    #       [11.816, 1.21]
    #    ],
    #  'asks': [
    #       [11.839, 0.78],
    #       [11.84, 44.392],
    #       [11.841, 1.1],
    #       [11.843, 300.89],
    #       [11.844, 355.131]
    #   ]}

if __name__ == '__main__':
    asyncio.run(main())
