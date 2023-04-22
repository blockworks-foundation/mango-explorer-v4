import asyncio

from mango_explorer_v4.mango_client import MangoClient

async def main():
    mango_client = await MangoClient.connect()

    mango_account = await mango_client.get_mango_account('5qqRJ5PasJguEWS1dbgTQpGW219UMVqqoq4Hpmnc7p8X')

    serum3_create_open_orders_ix = mango_client.make_serum3_create_open_orders_ix(
        mango_account,
        'SOL/USDC'
    )

    print(serum3_create_open_orders_ix.keys[6].pubkey)


if __name__ == '__main__':
    asyncio.run(main())