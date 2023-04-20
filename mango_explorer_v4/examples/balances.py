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

    print(await mango_client.balances(mango_account))

    # [
    #   {'symbol': 'USDC', 'balance': 2.7435726906761744},
    #   {'symbol': 'SOL', 'balance': 0.1690007074236178},
    #   {'symbol': 'MSOL', 'balance': 0.0}
    # ]


if __name__ == '__main__':
    asyncio.run(main())
