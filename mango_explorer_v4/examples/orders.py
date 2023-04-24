import argparse
import asyncio

from ..mango_client import MangoClient


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--mango-account',
        help='Mango account primary key.',
        required=True
    )

    args = parser.parse_args()

    mango_client = await MangoClient.connect()

    mango_account = await mango_client.get_mango_account(args.mango_account)

    orders = await mango_client.orders(mango_account)

    print(orders)



if __name__ == '__main__':
    asyncio.run(main())
