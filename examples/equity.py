import argparse
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

    print(await mango_client.equity())


if __name__ == '__main__':
    asyncio.run(main())
