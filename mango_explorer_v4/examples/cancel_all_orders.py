import argparse
import asyncio
from solana.keypair import Keypair
from base58 import b58decode

from ..mango_client import MangoClient


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--symbol',
        required=True
    )

    parser.add_argument(
        '--mango-account',
        help='Mango account primary key.',
        required=True
    )

    parser.add_argument(
        '--keypair',
        help='Solana wallet private key, to sign transactions for the Mango account.',
        required=True
    )

    args = parser.parse_args()

    mango_client = await MangoClient.connect()

    mango_account = await mango_client.get_mango_account(args.mango_account)

    keypair = Keypair.from_secret_key(b58decode(args.keypair))

    print(await mango_client.cancel_all_orders(mango_account, keypair, args.symbol))

    # 5B9Rq1sZAjtzXFbYh7wiV1thNGiaAC716ejPSBLE3EvTNgKC8CmFETdtMx8L5nfXHYZ3R8WyAqr9upfRbVYyGVg5
    # (Check the UI)


if __name__ == '__main__':
    asyncio.run(main())
