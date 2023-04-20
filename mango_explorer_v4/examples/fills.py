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

    response = await mango_client.fills(args.symbol)

    for fill in response['fills']:
        print(fill)


if __name__ == '__main__':
    asyncio.run(main())
