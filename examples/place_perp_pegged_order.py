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
        '--price-offset',
        type=float
    )

    parser.add_argument(
        '--peg-limit',
        type=float
    )

    parser.add_argument(
        '--quantity',
        type=float
    )

    args = parser.parse_args()

    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

    print(await mango_client.place_perp_pegged_order(args.symbol, args.side, args.price_offset, args.peg_limit, args.quantity))

if __name__ == '__main__':
    asyncio.run(main())
