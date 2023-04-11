import asyncio
import json
import pathlib
import logging
from decimal import Decimal

from mango_explorer_v4.accounts import PerpMarket
from mango_explorer_v4.helpers.perp_position import PerpPositionHelper
from mango_explorer_v4.mango_client import MangoClient
from mango_explorer_v4.oracles import pyth
from mango_explorer_v4.types import PerpPosition


async def main():
    logging.basicConfig(
        level=logging.DEBUG
    )

    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

    perp_market: PerpMarket = mango_client.perp_markets[1]

    perp_position: PerpPosition = mango_client.mango_account.perps[1]

    raw_oracle = await mango_client.provider.connection.get_account_info(perp_market.oracle)

    oracle = pyth.PRICE.parse(raw_oracle.value.data)

    oracle_price = oracle.agg.price * (Decimal(10) ** oracle.expo)

    print({
        'health_ratio': await mango_client.health_ratio(),
        'maintenance_health': None,
        'base_position': PerpPositionHelper.base_position_ui(perp_position, perp_market),
        'quote_position': Decimal(PerpPositionHelper.base_position_ui(perp_position, perp_market)) * oracle_price,
        'unsettled_pnl': PerpPositionHelper.unsettled_pnl(perp_position, perp_market, oracle_price)
    })



if __name__ == '__main__':
    asyncio.run(main())
