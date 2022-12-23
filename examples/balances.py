import asyncio
import json
import pathlib

from mango_explorer_v4.mango_client import MangoClient


async def main():
    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

    print(await mango_client.balances())

    # [
    #   {'symbol': 'USDC', 'balance': 2.7435726906761744},
    #   {'symbol': 'SOL', 'balance': 0.1690007074236178},
    #   {'symbol': 'MSOL', 'balance': 0.0}
    # ]


if __name__ == '__main__':
    asyncio.run(main())
