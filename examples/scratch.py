import asyncio
import json
import pathlib
import struct
from decimal import Decimal

import pythclient.pythaccounts
import pythclient.solana
from solders.account import Account

from mango_explorer_v4.mango_client import MangoClient
from mango_explorer_v4.oracles.pyth import PRICE


def is_pyth(account: Account):
    return struct.unpack('<I', account.data[:4])[0] == pythclient.pythaccounts._MAGIC


async def main():
    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

    perp_market = mango_client.perp_markets[0]

    raw_oracle = await mango_client.provider.connection.get_account_info(perp_market.oracle)

    price_data = PRICE.parse(raw_oracle.value.data)

    oracle_price = price_data.agg.price * (Decimal(10) ** price_data.expo)

    print(oracle_price, price_data.curr_slot)



if __name__ == '__main__':
    asyncio.run(main())
