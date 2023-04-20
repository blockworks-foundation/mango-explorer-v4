import argparse
import asyncio

from ..mango_client import MangoClient


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

    mango_client = await MangoClient.connect()

    print(await mango_client.orderbook_l2(args.symbol, args.depth))

if __name__ == '__main__':
    asyncio.run(main())
