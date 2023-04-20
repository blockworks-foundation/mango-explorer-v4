import asyncio
from ..mango_client import MangoClient


async def main():
    mango_client = await MangoClient.connect()

    mango_accounts = await mango_client.get_all_mango_accounts()

    for mango_account, balances in zip(
        mango_accounts,
        await asyncio.gather(*[mango_client.balances(mango_account) for mango_account in mango_accounts])
    ):
        print(mango_account.public_key, [{**entry, 'balance': round(entry['balance'], 2)} for entry in balances])

if __name__ == '__main__':
    asyncio.run(main())