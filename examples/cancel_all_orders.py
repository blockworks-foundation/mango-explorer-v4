import argparse
import asyncio
import json
import pathlib
from solana.keypair import Keypair
from base58 import b58decode

from mango_explorer_v4.mango_client import MangoClient


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--symbol',
        required=True
    )

    args = parser.parse_args()

    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect()

    keypair = Keypair.from_secret_key(b58decode(config['secret_key']))

    mango_account = await mango_client.get_mango_account(config['mango_account_pk'])

    print(await mango_client.cancel_all_orders(args.symbol, mango_account, keypair))

    # 5B9Rq1sZAjtzXFbYh7wiV1thNGiaAC716ejPSBLE3EvTNgKC8CmFETdtMx8L5nfXHYZ3R8WyAqr9upfRbVYyGVg5
    # (Check the UI)


if __name__ == '__main__':
    asyncio.run(main())
