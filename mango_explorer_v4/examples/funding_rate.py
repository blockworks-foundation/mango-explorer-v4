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

    args = parser.parse_args()

    mango_client = await MangoClient.connect()

    print(await mango_client.funding_rate(args.symbol))


if __name__ == '__main__':
    asyncio.run(main())