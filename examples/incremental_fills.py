import argparse
import asyncio
import json
import pathlib

from mango_explorer_v4.mango_client import MangoClient


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--symbol',
        required=False,
        default='SOL/USDC'
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

    async for fill in mango_client.incremental_fills(args.symbol):
        print(fill)


if __name__ == '__main__':
    asyncio.run(main())
