import asyncio

from mango_explorer_v4.mango_client import MangoClient


async def main(): print((await MangoClient.connect()).symbols())


if __name__ == '__main__':
    asyncio.run(main())
