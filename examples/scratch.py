import asyncio
import json
import pathlib

from mango_explorer_v4.helpers.perp_position import PerpPositionHelper
from mango_explorer_v4.mango_client import MangoClient


async def main():
    config = json.load(open(pathlib.Path(__file__).parent.parent / 'config.json'))

    mango_client = await MangoClient.connect(
        secret_key=config['secret_key'],
        mango_account_pk=config['mango_account_pk']
    )

    perp_market = mango_client.perp_markets[1]

    perp_position = mango_client.mango_account.perps[1]

    print(perp_position.base_position_lots, perp_market.base_lot_size)

    print(PerpPositionHelper.base_position_native(perp_position, perp_market))

    print(PerpPositionHelper.base_position_ui(perp_position, perp_market))

    print(PerpPositionHelper.unsettled_pnl(perp_position, perp_market))



if __name__ == '__main__':
    asyncio.run(main())
