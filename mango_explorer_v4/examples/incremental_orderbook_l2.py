import argparse
import asyncio

from ..mango_client import MangoClient


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--symbol',
        required=False,
        default='SOL-PERP'
    )

    parser.add_argument(
        '--depth',
        default=50,
        type=int
    )

    args = parser.parse_args()

    mango_client = await MangoClient.connect()

    async for orderbook in mango_client.incremental_orderbook_l2(args.symbol, args.depth):
        print(orderbook)


if __name__ == '__main__':
    asyncio.run(main())
