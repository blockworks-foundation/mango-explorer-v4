# mango-explorer-v4

Python client library for interacting with Mango Markets V4.

## Installation

![PyPI](https://img.shields.io/pypi/v/mango-explorer-v4)

`mango-explorer-v4` is available as a [Python package on PyPI](https://pypi.org/project/mango-explorer-v4) and can be installed as:

```
pip install mango-explorer-v4
```

## Usage

Assuming that you have a SOL wallet already set up, visit https://app.mango.markets to create a Mango account and fund it so that you can place orders.

```python
import asyncio
from mango_explorer_v4.mango_client import MangoClient
from solana.keypair import Keypair
from base58 import b58decode

async def main():
    mango_client = await MangoClient.connect()
    
    # General data functions:
    print(mango_client.symbols())
    
    print(await mango_client.orderbook_l2('SOL/USDC'))
    
    print(await mango_client.fills('SOL-PERP'))
    
    # It is possible to livestream both orderbook & fills, look for incremental_*.py in the examples folder

    # Fill in your Mango account public key e.g 9XJt2tvSZghsMAhWto1VuPBrwXsiimPtsTR8XwGgDxK2 
    mango_account = await mango_client.get_mango_account('PUBLIC_KEY')

    # You can look up any Mango account using
    # https://app.mango.markets/?address=9XJt2tvSZghsMAhWto1VuPBrwXsiimPtsTR8XwGgDxK2
 
    print(await mango_client.balances(mango_account))
    
    print(await mango_client.equity(mango_account)) # Account Value
    
    # Fill in output from Phantom's "Export Private Key" e.g 2pvKRVh ... 1fL5qGq
    keypair = Keypair.from_secret_key(b58decode('SECRET_KEY'))
    
    # Place a limit order
    print(await mango_client.place_order(mango_account, keypair, 'SOL/USDC', 'bid', 10, 0.1, 'limit'))
    
    # Place an oracle pegged perp order: https://docs.mango.markets/mango-markets/oracle-peg-orders
    print(
        await mango_client.place_perp_pegged_order(
            mango_account,
            keypair,
            'SOL-PERP',
            'bid',
            price_offset=-5, # Will always be $5 under oracle price
            peg_limit=10, # If the oracle price moves $10 or more, the order will expire
            quantity=1
        )
    )
    
    # Cancel all orders
    print(
        await mango_client.cancel_all_orders(
            mango_account,
            keypair,
            'SOL-PERP'
        )
    )
    
    # There's a simple quoter, using atomic cancel-replace in examples/market_maker.py

asyncio.run(main())
```

## Running the examples

**Please make sure you're running mango-explorer-v4@0.7.3 or above - these instructions don't apply to older versions.**

You can find a collection of example code [here](./mango_explorer_v4/examples). These are to be run as command-line tools, with the simplest being the [symbols retrieval function](./mango_explorer_v4/examples/symbols.py), executable as:
```shell
python -m mango_explorer_v4.examples.symbols
# Output:
# [
#     {
#         'name': 'SOL/USDC',
#         'type': 'spot',
#         'base_currency': 'SOL',
#         'quote_currency': 'USDC',
#         'maker_fees': ...,
#         'taker_fees': ...
#     }
#     ... all order symbols
# ]
```

Examples may take arguments, which are specified in their source files. The [equity function](https://github.com/blockworks-foundation/mango-explorer-v4/blob/master/mango_explorer_v4/examples/equity.py) for example, takes a Mango account primary key, whilst the [order book retrieval](https://github.com/blockworks-foundation/mango-explorer-v4/blob/master/mango_explorer_v4/examples/orderbook_l2.py) takes a symbol & (optional) depth. These can be specified in the shell like this:

```shell
python -m mango_explorer_v4.examples.equity --mango-account 9XJt2tvSZghsMAhWto1VuPBrwXsiimPtsTR8XwGgDxK2
# Outputs the Account Balance at https://app.mango.markets/?address=9XJt2tvSZghsMAhWto1VuPBrwXsiimPtsTR8XwGgDxK2

python -m mango_explorer_v4.examples.orderbook_l2 --symbol SOL-PERP --depth 5
# Outputs the first 5 orders in the book at https://app.mango.markets/trade?name=SOL-PERP
```

Some transactions, like order placement, require a keypair. On [Phantom wallet](https://phantom.app/) it can be fetched as follows:

https://user-images.githubusercontent.com/28162761/233431861-5db448c1-fdf9-4dd0-8df9-156b131dfd71.mov

With the keypair at hand you can place orders using:

```shell
python -m mango_explorer_v4.examples.place_order \
    --keypair [KEYPAIR] \
    --mango-account [MANGO_ACCOUNT] \
    --symbol SOL-PERP \
    --side bids \
    --price 1 \
    --size 0.1
```

And cancel them later as:
```shell
python -m mango_explorer_v4.examples.cancel_all_orders \
    --keypair [KEYPAIR] \
    --mango-account [MANGO_ACCOUNT] \
    --symbol SOL-PERP
```

## Support

Support is available on the [Mango Markets Discord server](https://discord.gg/8vs8uJJrcp) - post in the `#dev-discussion` channel for any questions or feature requests. 
