import argparse
import asyncio
from base58 import b58decode
from solana.keypair import Keypair

from ..mango_client import MangoClient


async def main():
    parser = argparse.ArgumentParser()

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

    parser.add_argument(
        '--symbol',
        required=True
    )

    parser.add_argument(
        '--side',
        required=True,
        choices=['bids', 'asks']
    )

    parser.add_argument(
        '--price-offset',
        type=float
    )

    parser.add_argument(
        '--peg-limit',
        type=float
    )

    parser.add_argument(
        '--quantity',
        type=float
    )

    args = parser.parse_args()

    mango_client = await MangoClient.connect()

    mango_account = await mango_client.get_mango_account(args.mango_account)

    keypair = Keypair.from_secret_key(b58decode(args.keypair))

    print(
        await mango_client.place_perp_pegged_order(
            mango_account,
            keypair,
            args.symbol,
            args.side,
            args.price_offset,
            args.peg_limit,
            args.quantity
        )
    )

if __name__ == '__main__':
    asyncio.run(main())
