import asyncio
import itertools
import sys
import json
import logging
import pathlib
import re
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Any

import aiostream.stream

from .constants import RUST_U64_MAX, RUST_I64_MAX, QUOTE_DECIMALS
from .oracles import pyth
from .constructs.book_side_items import BookSideItems

import base58
from anchorpy import Provider, Wallet
from pyserum.market import AsyncMarket, OrderBook
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solana.rpc.websocket_api import connect
from solana.transaction import AccountMeta, Transaction
from solders.rpc.responses import AccountNotification

from mango_explorer_v4.types.side import Bid, Ask
from mango_explorer_v4.types.place_order_type import Limit
from mango_explorer_v4.types.order_tree_root import OrderTreeRoot
from mango_explorer_v4.accounts.bank import Bank
from mango_explorer_v4.accounts.group import Group
from mango_explorer_v4.accounts.book_side import BookSide
from mango_explorer_v4.accounts.mango_account import MangoAccount
from mango_explorer_v4.accounts.mint_info import MintInfo
from mango_explorer_v4.accounts.serum3_market import Serum3Market
from mango_explorer_v4.accounts.perp_market import PerpMarket
from mango_explorer_v4.types.inner_node import InnerNode
from mango_explorer_v4.types.leaf_node import LeafNode
from mango_explorer_v4.instructions.serum3_cancel_all_orders import Serum3CancelAllOrdersAccounts, Serum3CancelAllOrdersArgs, serum3_cancel_all_orders
from mango_explorer_v4.instructions.serum3_create_open_orders import Serum3CreateOpenOrdersAccounts, serum3_create_open_orders
from mango_explorer_v4.instructions.serum3_place_order import Serum3PlaceOrderArgs, Serum3PlaceOrderAccounts, serum3_place_order
from mango_explorer_v4.instructions.perp_place_order import PerpPlaceOrderArgs, PerpPlaceOrderAccounts, perp_place_order
from mango_explorer_v4.instructions.perp_cancel_all_orders import PerpCancelAllOrdersArgs, PerpCancelAllOrdersAccounts, perp_cancel_all_orders
from mango_explorer_v4.instructions.perp_place_order_pegged import PerpPlaceOrderPeggedArgs, PerpPlaceOrderPeggedAccounts, perp_place_order_pegged
from mango_explorer_v4.program_id import SERUM_PROGRAM_ID, MANGO_PROGRAM_ID
from mango_explorer_v4.types import serum3_side, serum3_self_trade_behavior, serum3_order_type
from mango_explorer_v4.types import place_order_type


logging.basicConfig(
    level=logging.INFO
)


@dataclass
class MangoClient():
    provider: Provider
    mango_account_pk: str
    group_config: dict
    mango_account: MangoAccount
    serum_market_configs: [dict]
    perp_market_configs: [dict]
    serum_markets: [Serum3Market]
    serum_markets_external: [AsyncMarket]
    banks: [Bank]
    mint_infos: [MintInfo]
    perp_markets: [PerpMarket]
    rpc_url: str
    group: Group

    @staticmethod
    async def connect(
        secret_key: str | bytes,
        # ^ Can be the output from Phantom's "Export Private Key" - this for easy onboarding
        # as with the V3 lib folks used to get confused about how to turn it into something
        # like the output from `solana-keygen new -o scratch.json`, which is also supported
        mango_account_pk: str,
        # ^ A SOL wallet can have multiple Mango accounts - let the user pick the one he's
        # looking to use. Specifying it beforehand spares a lot of redundancy
        rpc_url: str = 'https://mango.rpcpool.com/0f9acc0d45173b51bf7d7e09c1e5'
        # ^ Can use the default RPC endpoint or whichever so desired
    ):
        # TODO: Parallelize asynchronous calls here to reduce load times - around 2 seconds right now
        provider = Provider(
            AsyncClient(rpc_url, Processed),
            Wallet(
                Keypair.from_secret_key(
                    base58.b58decode(secret_key)
                    if type(secret_key == str) else
                    Wallet(Keypair.from_secret_key(secret_key))
                )
            )
            if secret_key is not None else Wallet.dummy()
        )

        mango_account = await MangoAccount.fetch(
            provider.connection,
            PublicKey(mango_account_pk)
        )

        if mango_account.owner != provider.wallet.public_key:
            raise ValueError('Mango account is not owned by the secret key entered')

        ids = json.loads(open(pathlib.Path(__file__).parent / 'ids.json').read())
        # TODO: ^ Make this fetch from https://mango-transaction-log.herokuapp.com/v4/group-metadata instead

        group_config = [group_config for group_config in ids['groups'] if PublicKey(group_config['publicKey']) == mango_account.group][0]

        group = await Group.fetch(provider.connection, PublicKey(group_config['publicKey']))

        perp_market_configs = [
            perp_market_config for perp_market_config in group_config['perpMarkets'] if perp_market_config['active']
        ]

        serum_market_configs = [
            serum_market_config for serum_market_config in group_config['serum3Markets'] if serum_market_config['active']
        ]

        serum_markets = await Serum3Market.fetch_multiple(
            provider.connection,
            [
                PublicKey(serum3_market_config['publicKey']) for serum3_market_config in serum_market_configs
            ]
        )

        serum_markets_external = await asyncio.gather(*[
            AsyncMarket.load(provider.connection, serum_market.serum_market_external, SERUM_PROGRAM_ID)
            for serum_market in serum_markets
        ])

        banks_config = [
            {
                'tokenIndex': token_config['tokenIndex'],
                'publicKey': PublicKey(token_config['banks'][0]['publicKey'])
            }
            for token_config in group_config['tokens']
            if token_config['active']
        ]

        banks = await Bank.fetch_multiple(
            provider.connection,
            [bank_config['publicKey'] for bank_config in banks_config]
        )

        mint_infos_configs = [
            {
                'tokenIndex': token_config['tokenIndex'],
                'publicKey': PublicKey(token_config['mintInfo'])
            }
            for token_config in group_config['tokens']
            if token_config['active']
            if token_config['tokenIndex'] in [token.token_index for token in mango_account.tokens if token.token_index != 65535]
        ]

        mint_infos_configs = list(sorted(mint_infos_configs, key=lambda mint_info_config: mint_info_config['tokenIndex']))

        mint_infos = await MintInfo.fetch_multiple(
            provider.connection,
            [mint_info_config['publicKey'] for mint_info_config in mint_infos_configs]
        )

        perp_markets = await PerpMarket.fetch_multiple(
            provider.connection,
            [perp_market_config['publicKey'] for perp_market_config in perp_market_configs]
        )

        return MangoClient(
            provider=provider,
            mango_account_pk=mango_account_pk,
            mango_account=mango_account,
            group_config=group_config,
            serum_market_configs=serum_market_configs,
            perp_market_configs=perp_market_configs,
            serum_markets=serum_markets,
            serum_markets_external=serum_markets_external,
            banks=banks,
            mint_infos=mint_infos,
            perp_markets=perp_markets,
            rpc_url=rpc_url,
            group=group
        )

    def symbols(self):
        # Can't make it a static / class function yet because need to know
        # which group to use, and group is inferred from the Mango account

        # This might not be the best format for keeping symbols organized,
        # as it presumes that perpetual and spot market names would never
        # conflict, but it works for now

        # TODO: Add minimum order size, tick size, lot size and liquidation fee
        return [
            *[
                {
                    'name': perp_market_config['name'],
                    'type': 'perpetual',
                    'base_currency': perp_market_config['name'].split('-')[0],
                    'quote_currency': perp_market_config['name'].split('-')[1],
                    'maker_fees': - (1 / 1e4),
                    'taker_fees': (4 / 1e4)
                }
                for perp_market_config in self.perp_market_configs
            ],
            *[
                {
                    'name': serum3_market_config['name'],
                    'type': 'spot',
                    'base_currency': serum3_market_config['name'].split('/')[0],
                    'quote_currency': serum3_market_config['name'].split('/')[1],
                    'maker_fees': - (0.5 / 1e4),
                    'taker_fees': (1 / 1e4)
                }
                for serum3_market_config in self.serum_market_configs
            ]
        ]

    async def orderbook_l2(self, symbol: str, depth: int = 100):
        # TODO: Validate that the symbol entered is valid

        market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", symbol)[1]]

        match market_type:
            case 'spot':
                serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

                serum_market_index = serum_market_config['marketIndex']

                serum_market = [
                    serum_market
                    for serum_market in self.serum_markets
                    if serum_market.market_index == serum_market_index
                ][0]

                serum_market_external = [
                    serum_market_external
                    for serum_market_external in self.serum_markets_external
                    if serum_market_external.state.public_key() == serum_market.serum_market_external
                ][0]

                response = await self.provider.connection.get_multiple_accounts([
                    serum_market_external.state.bids(),
                    serum_market_external.state.asks()
                ])

                [raw_bids, raw_asks] = response.value

                [bids, asks] = [
                    OrderBook.from_bytes(serum_market_external.state, raw_bids.data),
                    OrderBook.from_bytes(serum_market_external.state, raw_asks.data)
                ]

                orderbook = {
                    'symbol': symbol,
                    'bids': [[bid.price, bid.size] for bid in bids.get_l2(depth)],
                    'asks': [[ask.price, ask.size] for ask in asks.get_l2(depth)],
                    'slot': response.context.slot
                }

                return orderbook
            case 'perpetual':
                perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

                perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

                accounts = await self.provider.connection.get_multiple_accounts([perp_market.bids, perp_market.asks, perp_market.oracle])

                [raw_bids, raw_asks, raw_oracle] = accounts.value

                [bids, asks] = [BookSide.decode(raw_bids.data), BookSide.decode(raw_asks.data)]

                oracle = pyth.PRICE.parse(raw_oracle.data)

                oracle_price = oracle.agg.price * (Decimal(10) ** oracle.expo)

                orderbook = {
                    'symbol': symbol,
                    'bids': BookSideItems('bids', bids, perp_market, oracle_price).l2(),
                    'asks': BookSideItems('asks', asks, perp_market, oracle_price).l2(),
                    'slot': accounts.context.slot
                }

                return orderbook

    async def snapshots_l2(self, symbol: str, depth: int = 50):
        serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

        serum_market_index = serum_market_config['marketIndex']

        serum_market = [
            serum_market
            for serum_market in self.serum_markets
            if serum_market.market_index == serum_market_index
        ][0]

        serum_market_external = [
            serum_market_external
            for serum_market_external in self.serum_markets_external
            if serum_market_external.state.public_key() == serum_market.serum_market_external
        ][0]

        orderbook = {
            'symbol': symbol,
            'bids': None,
            'asks': None
        }

        yield await self.orderbook_l2(symbol, depth)

        async def snapshots(side):
            async with connect('wss://mango.rpcpool.com/0f9acc0d45173b51bf7d7e09c1e5') as websocket:
                await websocket.account_subscribe(getattr(serum_market_external.state, side)(), Processed, 'jsonParsed')

                async for message in websocket:
                    for submessage in message:
                        if not isinstance(submessage, AccountNotification):
                            continue

                        orders = [
                            [order.price, order.size]
                            for order in OrderBook.from_bytes(
                                serum_market_external.state,
                                submessage.result.value.data
                            ).get_l2(depth)
                        ]

                        yield side, orders

        async with aiostream.stream.merge(*[stream for stream in [snapshots(side) for side in ['bids', 'asks']]]).stream() as streamer:
            async for side, orders in streamer:
                orderbook[side] = orders

                if not all([orderbook['bids'], orderbook['asks']]):
                    continue

                yield orderbook


    def _health_remaining_accounts(
        self,
        retriever: Literal['fixed', 'scanning'],
        banks: [Bank],
        perp_markets: [PerpMarket]
    ) -> [AccountMeta]:
        health_remaining_account_pks = []

        match retriever:
            case 'fixed':
                token_indices = [token.token_index for token in self.mango_account.tokens]

                if len(banks) > 0:
                    for bank in banks:
                        if bank.token_index not in token_indices:
                            index = [
                                idx for idx, token in enumerate(self.mango_account.tokens)
                                if token.token_index == 65535
                                if token_indices[idx] == 65535
                            ][0]

                            token_indices[index] = bank.token_index

                mint_infos = [
                    mint_info for mint_info in self.mint_infos
                    if mint_info.token_index in [token_index for token_index in token_indices if token_index != 65535]
                ]

                health_remaining_account_pks.extend([mint_info.banks[0] for mint_info in mint_infos])

                health_remaining_account_pks.extend([mint_info.oracle for mint_info in mint_infos])

                perp_market_indices = [perp.market_index for perp in self.mango_account.perps]

                if len(perp_markets) > 0:
                    for perp_market in perp_markets:
                        if perp_market.perp_market_index not in perp_market_indices:
                            index = [
                                idx for idx, perp in enumerate(self.mango_account.perps)
                                if perp.market_index == 65535
                                if perp_market_indices[idx] == 65535
                            ][0] = perp_market.perp_market_index

                            perp_market_indices[index] = perp_market.perp_market_index

                perp_markets = [
                    perp_market for perp_market in self.perp_markets
                    if perp_market.perp_market_index in [perp_index for perp_index in perp_market_indices if perp_index != 65535]
                ]

                perp_market_pks = [
                    PublicKey(perp_market_config['publicKey']) for perp_market_config in self.group_config['perpMarkets']
                    if perp_market_config['marketIndex'] in [perp_market.perp_market_index for perp_market in perp_markets]
                ]

                health_remaining_account_pks.extend(perp_market_pks)

                health_remaining_account_pks.extend([perp_market.oracle for perp_market in perp_markets])

                health_remaining_account_pks.extend([serum3.open_orders for serum3 in self.mango_account.serum3 if serum3.market_index != 65535])
            case 'scanning':
                raise NotImplementedError()

        remaining_accounts: [AccountMeta] = [
            AccountMeta(pubkey=remaining_account_pk, is_writable=False, is_signer=False)
            for remaining_account_pk in health_remaining_account_pks
        ]

        return remaining_accounts


    def make_serum3_place_order_ix(self, symbol: str, side: Literal['bids', 'asks'], price: float, size: float):
        serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

        serum_market_index = serum_market_config['marketIndex']

        serum_market = [
            serum_market
            for serum_market in self.serum_markets
            if serum_market.market_index == serum_market_index
        ][0]

        serum_market_external = [
            serum_market_external
            for serum_market_external in self.serum_markets_external
            if serum_market_external.state.public_key() == serum_market.serum_market_external
        ][0]

        limit_price = serum_market_external.state.price_number_to_lots(price)

        max_base_qty = serum_market_external.state.base_size_number_to_lots(size)

        order_type = {'limit': serum3_order_type.Limit(), 'immediate_or_cancel': serum3_order_type.ImmediateOrCancel()}['limit']

        max_native_quote_qty_without_fees = limit_price * max_base_qty

        is_maker = order_type == serum3_order_type.PostOnly()

        fees = {True: - (0.5 / 1e4), False: (1 / 1e4)}[is_maker]

        max_native_quote_qty_including_fees = max_native_quote_qty_without_fees + round(max_native_quote_qty_without_fees * fees)

        client_order_id = round(time.time_ns() / 1e6)

        serum3_place_order_args: Serum3PlaceOrderArgs = {
            'side': {'bids': serum3_side.Bid(), 'asks': serum3_side.Ask()}[side],
            'limit_price': limit_price,
            'max_base_qty': max_base_qty,
            'max_native_quote_qty_including_fees': max_native_quote_qty_including_fees,
            'self_trade_behavior': serum3_self_trade_behavior.DecrementTake(),
            'order_type': order_type,
            'client_order_id': client_order_id,
            'limit': 10
        }

        serum3 = [serum3 for serum3 in self.mango_account.serum3 if serum3.market_index == serum_market_index][0]

        if serum3 is None:
            raise Exception('serum3 account not found')

        payer_token_index = {
            'bids': serum_market.quote_token_index,
            'asks': serum_market.base_token_index
        }[side]

        bank = [bank for bank in self.banks if bank.token_index == payer_token_index][0]

        banks_config = [
            {
                'tokenIndex': token_config['tokenIndex'],
                'publicKey': PublicKey(token_config['banks'][0]['publicKey'])
            }
            for token_config in self.group_config['tokens']
            if token_config['active']
        ]

        bank_config = [bank_config for bank_config in banks_config if bank_config['tokenIndex'] == bank.token_index][0]

        serum_market_external_vault_signer_address = PublicKey.create_program_address([
            bytes(serum_market.serum_market_external),
            serum_market_external.state.vault_signer_nonce().to_bytes(8, 'little')
        ], SERUM_PROGRAM_ID)

        serum3_place_order_accounts: Serum3PlaceOrderAccounts = {
            'group': self.mango_account.group,
            'account': PublicKey(self.mango_account_pk),
            'owner': self.mango_account.owner,
            'open_orders': serum3.open_orders,
            'serum_market': PublicKey(serum_market_config['publicKey']),
            'serum_program': SERUM_PROGRAM_ID,
            'serum_market_external': serum_market.serum_market_external,
            'market_bids': serum_market_external.state.bids(),
            'market_asks': serum_market_external.state.asks(),
            'market_event_queue': serum_market_external.state.event_queue(),
            'market_request_queue': serum_market_external.state.request_queue(),
            'market_base_vault': serum_market_external.state.base_vault(),
            'market_quote_vault': serum_market_external.state.quote_vault(),
            'market_vault_signer': serum_market_external_vault_signer_address,
            'payer_bank': bank_config['publicKey'],
            'payer_vault': bank.vault,
            'payer_oracle': bank.oracle
        }

        remaining_accounts = self._health_remaining_accounts('fixed', [], [])

        serum3_place_order_ix = serum3_place_order(
            serum3_place_order_args,
            serum3_place_order_accounts,
            remaining_accounts=remaining_accounts
        )

        return serum3_place_order_ix

    def make_serum3_create_open_orders_ix(self, symbol):
        serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

        serum_market_index = serum_market_config['marketIndex']

        serum_market = [
            serum_market
            for serum_market in self.serum_markets
            if serum_market.market_index == serum_market_index
        ][0]

        [open_orders_pk, nonce] = PublicKey.find_program_address(
            [
                bytes('Serum3OO', 'utf-8'),
                bytes(PublicKey(self.mango_account_pk)),
                bytes(PublicKey(serum_market_config['publicKey']))
            ],
            MANGO_PROGRAM_ID
        )

        serum3_create_open_orders_accounts: Serum3CreateOpenOrdersAccounts = {
            'group': self.mango_account.group,
            'account': PublicKey(self.mango_account_pk),
            'owner': self.provider.wallet.public_key,
            'serum_market': PublicKey(serum_market_config['publicKey']),
            'serum_program': serum_market.serum_program,
            'serum_market_external': serum_market.serum_market_external,
            'open_orders': open_orders_pk,
            'payer': self.provider.wallet.public_key,
        }

        serum3_create_open_orders_ix = serum3_create_open_orders(serum3_create_open_orders_accounts)

        return serum3_create_open_orders_ix

    def make_perp_place_order_ix(self, symbol, side, price, size):
        perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

        perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

        quote_decimals = 6

        def to_native(ui_amount: float, decimals: float) -> int:
            return int(ui_amount * 10 ** decimals)

        def ui_price_to_lots(perp_market: PerpMarket, price: float) -> int:
            return int(to_native(price, quote_decimals) * perp_market.base_lot_size / (perp_market.quote_lot_size * 10 ** perp_market.base_decimals))

        def ui_base_to_lots(perp_market: PerpMarket, size: float) -> int:
            return int(to_native(size, perp_market.base_decimals) // perp_market.base_lot_size)

        perp_place_order_args: PerpPlaceOrderArgs = {
            'side': {'bids': Bid, 'asks': Ask}[side],
            'price_lots': ui_price_to_lots(perp_market, price),
            'max_base_lots': ui_base_to_lots(perp_market, size),
            'max_quote_lots': sys.maxsize,
            'client_order_id': int(time.time() * 1e3),
            'order_type': place_order_type.Limit(),
            'reduce_only': False,
            'expiry_timestamp': 0,
            'limit': 10
        }

        perp_place_order_accounts: PerpPlaceOrderAccounts = {
            'group': perp_market.group,
            'account': PublicKey(self.mango_account_pk),
            'owner': self.provider.wallet.public_key,
            'perp_market': PublicKey(perp_market_config['publicKey']),
            'bids': perp_market.bids,
            'asks': perp_market.asks,
            'event_queue': perp_market.event_queue,
            'oracle': perp_market.oracle
        }

        remaining_accounts = self._health_remaining_accounts('fixed', [[bank for bank in self.banks if bank.token_index == 0][0]], [perp_market])

        perp_place_order_ix = perp_place_order(
            perp_place_order_args,
            perp_place_order_accounts,
            remaining_accounts=remaining_accounts
        )

        return perp_place_order_ix

    async def place_order(
        self,
        symbol: str,
        side: Literal['bids', 'asks'],
        price: float,
        size: float
    ):
        market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", symbol)[1]]

        match market_type:
            case 'spot':
                serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

                serum_market_index = serum_market_config['marketIndex']

                try:
                    serum3 = [serum3 for serum3 in self.mango_account.serum3 if serum3.market_index == serum_market_index][0]
                except IndexError:
                    logging.error(f"Open orders account for {symbol} not found, creating one...")

                    serum3_create_open_orders_ix = self.make_serum3_create_open_orders_ix('SOL/USDC')

                    recent_blockhash = (await self.provider.connection.get_latest_blockhash()).value.blockhash

                    tx = Transaction()

                    tx.recent_blockhash = str(recent_blockhash)

                    tx.add(serum3_create_open_orders_ix)

                    tx.sign(self.provider.wallet.payer)

                    response = await self.provider.send(tx)

                    logging.error(f"Waiting for Open Orders account creation confirmation...")

                    await self.provider.connection.confirm_transaction(response)

                    logging.error(f"Open orders account created for {symbol}.")

                    self.mango_account = await MangoAccount.fetch(
                        self.provider.connection,
                        PublicKey(self.mango_account_pk)
                    )

                serum3_place_order_ix = self.make_serum3_place_order_ix(
                    symbol,
                    side,
                    price,
                    size
                )

                tx = Transaction()

                recent_blockhash = (await self.provider.connection.get_latest_blockhash()).value.blockhash

                tx.recent_blockhash = str(recent_blockhash)

                tx.add(serum3_place_order_ix)

                tx.sign(self.provider.wallet.payer)

                response = await self.provider.send(tx)

                return response
            case 'perpetual':
                tx = Transaction()

                recent_blockhash = (await self.provider.connection.get_latest_blockhash()).value.blockhash

                tx.recent_blockhash = str(recent_blockhash)

                perp_place_order_ix = self.make_perp_place_order_ix(symbol, side, price, size)

                tx.add(perp_place_order_ix)

                tx.sign(self.provider.wallet.payer)

                response = await self.provider.send(tx)

                return response

    def make_serum3_cancel_all_orders_ix(self, symbol: str):
        serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

        serum_market_index = serum_market_config['marketIndex']

        serum_market = [
            serum_market
            for serum_market in self.serum_markets
            if serum_market.market_index == serum_market_index
        ][0]

        try:
            serum3 = [serum3 for serum3 in self.mango_account.serum3 if serum3.market_index == serum_market_index][0]
        except IndexError as error:
            print(error)

        serum_market_external = [
            serum_market_external
            for serum_market_external in self.serum_markets_external
            if serum_market_external.state.public_key() == serum_market.serum_market_external
        ][0]

        serum3_cancel_all_orders_args: Serum3CancelAllOrdersArgs = {
            'limit': 10
        }

        serum3_cancel_all_orders_accounts: Serum3CancelAllOrdersAccounts = {
            'group': self.mango_account.group,
            'account': PublicKey(self.mango_account_pk),
            'owner': self.provider.wallet.public_key,
            'open_orders': serum3.open_orders,
            'serum_market': PublicKey(serum_market_config['publicKey']),
            'serum_program': serum_market.serum_program,
            'serum_market_external': serum_market.serum_market_external,
            'market_bids': serum_market_external.state.bids(),
            'market_asks': serum_market_external.state.asks(),
            'market_event_queue': serum_market_external.state.event_queue()
        }

        serum3_cancel_all_orders_ix = serum3_cancel_all_orders(
            serum3_cancel_all_orders_args,
            serum3_cancel_all_orders_accounts
        )

        return serum3_cancel_all_orders_ix

    def make_perp_cancel_all_orders_ix(self, symbol: str):
        perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

        perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

        perp_cancel_all_orders_args: PerpCancelAllOrdersArgs = {
            'limit': 10
        }

        perp_cancel_all_orders_accounts: PerpCancelAllOrdersAccounts = {
            'group': perp_market.group,
            'account': PublicKey(self.mango_account_pk),
            'owner': self.provider.wallet.public_key,
            'perp_market': PublicKey(perp_market_config['publicKey']),
            'bids': perp_market.bids,
            'asks': perp_market.asks
        }

        perp_cancel_all_orders_ix = perp_cancel_all_orders(perp_cancel_all_orders_args, perp_cancel_all_orders_accounts)

        return perp_cancel_all_orders_ix

    async def cancel_all_orders(self, symbol: str):
        market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", symbol)[1]]

        match market_type:
            case 'spot':
                tx = Transaction()

                recent_blockhash = (await self.provider.connection.get_latest_blockhash()).value.blockhash

                tx.recent_blockhash = str(recent_blockhash)

                serum3_cancel_all_orders_ix = self.make_serum3_cancel_all_orders_ix(symbol)

                tx.add(serum3_cancel_all_orders_ix)

                tx.sign(self.provider.wallet.payer)

                response = await self.provider.send(tx)

                return response
            case 'perpetual':
                tx = Transaction()

                recent_blockhash = (await self.provider.connection.get_latest_blockhash()).value.blockhash

                tx.recent_blockhash = str(recent_blockhash)

                perp_cancel_all_orders_ix = self.make_perp_cancel_all_orders_ix(symbol)

                tx.add(perp_cancel_all_orders_ix)

                tx.sign(self.provider.wallet.payer)

                response = await self.provider.send(tx)

                return response

    async def balances(self):
        # TODO: Clean up this mess
        return [
            {
                'symbol': meta['symbol'],
                'balance': float(
                    meta['token_indexed_position'] * (
                        meta['bank_deposit_index'] if meta['token_indexed_position'] > 0
                        else meta['bank_borrow_index']
                    )
                    /
                    meta['bank_mint_decimals']
                )
            }
            for meta in
            [
                {
                    'symbol': token_config['symbol'],
                    'token_indexed_position': Decimal(token.indexed_position.val) / divider,
                    'bank_mint_decimals': 10 ** bank.mint_decimals,
                    'bank_deposit_index': Decimal(bank.deposit_index.val) / divider,
                    'bank_borrow_index': Decimal(bank.borrow_index.val) / divider,
                }
                for token, bank, token_config, divider in
                [
                    [
                        token,
                        [bank for bank in self.banks if bank.token_index == token.token_index][0],
                        [token_config for token_config in self.group_config['tokens'] if token_config['tokenIndex'] == token.token_index][0],
                        Decimal(2 ** (8 * 6))
                    ]
                    for token in self.mango_account.tokens
                    if token.token_index != 65535
                ]
            ]
        ]

    def make_place_perp_pegged_order_ix(
        self,
        symbol: str,
        side: Literal['bids', 'asks'],
        price_offset: float,
        peg_limit: float,
        quantity: float,
        max_quote_quantity: float = None,
        client_order_id: int = int(time.time()),
        expiry_timestamp: int = 0,
        limit: int = 10,
        reduce_only: bool = False
    ):
        perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

        perp_market: PerpMarket = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

        perp_place_order_pegged_args: PerpPlaceOrderPeggedArgs = {
            'side': {'bids': Bid, 'asks': Ask}[side],
            'price_offset_lots': perp_market.ui_price_to_lots(price_offset),
            'peg_limit': perp_market.ui_price_to_lots(peg_limit),
            'max_base_lots': perp_market.ui_base_to_lots(quantity),
            'max_quote_lots': perp_market.ui_quote_to_lots(max_quote_quantity) if max_quote_quantity else RUST_I64_MAX,
            'client_order_id': client_order_id,
            'order_type': Limit,
            'reduce_only': reduce_only,
            'expiry_timestamp': expiry_timestamp,
            'limit': limit,
            'max_oracle_staleness_slots': -1
        }

        perp_place_order_pegged_accounts: PerpPlaceOrderPeggedAccounts = {
            'group': PublicKey(self.group_config['publicKey']),
            'account': PublicKey(self.mango_account_pk),
            'owner': self.mango_account.owner,
            'perp_market': PublicKey(perp_market_config['publicKey']),
            'bids': perp_market.bids,
            'asks': perp_market.asks,
            'event_queue': perp_market.event_queue,
            'oracle': perp_market.oracle
        }

        remaining_accounts = self._health_remaining_accounts(
            'fixed',
            [bank for bank in self.banks if bank.token_index == 0],
            [perp_market]
        )

        return perp_place_order_pegged(
            perp_place_order_pegged_args,
            perp_place_order_pegged_accounts,
            remaining_accounts=remaining_accounts
        )

    async def place_perp_pegged_order(
        self,
        symbol: str,
        side: Literal['bids', 'asks'],
        price_offset: float,
        peg_limit: float,
        quantity: float,
        max_quote_quantity: float = None,
        client_order_id: int = int(time.time()),
        expiry_timestamp: int = 0,
        limit: int = 10,
        reduce_only: bool = False
    ):
        tx = Transaction()

        recent_blockhash = (await self.provider.connection.get_latest_blockhash()).value.blockhash

        tx.recent_blockhash = str(recent_blockhash)

        tx.add(
            self.make_place_perp_pegged_order_ix(
                symbol,
                side,
                price_offset,
                peg_limit,
                quantity,
                max_quote_quantity,
                client_order_id,
                expiry_timestamp,
                limit,
                reduce_only
            )
        )

        tx.sign(self.provider.wallet.payer)

        response = await self.provider.send(tx)

        return response

    async def funding_rate(self, symbol: str):
        # TODO: Maybe fetch the perp market alongside the other data, just so that it's always within the same slot
        perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

        perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

        accounts = await self.provider.connection.get_multiple_accounts([perp_market.bids, perp_market.asks, perp_market.oracle])

        [raw_bids, raw_asks, raw_oracle] = accounts.value

        [bids, asks] = [BookSide.decode(raw_bids.data), BookSide.decode(raw_asks.data)]

        oracle = pyth.PRICE.parse(raw_oracle.data)

        oracle_price = float(Decimal(str(oracle.agg.price)) * Decimal(10) ** oracle.expo)

        [bids, asks] = [BookSideItems('bids', bids, perp_market, oracle_price), BookSideItems('asks', asks, perp_market, oracle_price)]

        min_funding, max_funding = float(perp_market.min_funding), float(perp_market.max_funding)

        impact_quantity = perp_market.base_lots_to_ui(perp_market.impact_quantity)

        bid, ask = [bids.impact_price(impact_quantity), asks.impact_price(impact_quantity)]

        if bid and ask:
            mid_price = (bid + ask) / 2

            funding = min(max(mid_price / oracle_price - 1, min_funding), max_funding)
        elif bid:
            funding = max_funding
        elif ask:
            funding = min_funding
        else:
            funding = 0

        return funding / 24 / 10 ** QUOTE_DECIMALS