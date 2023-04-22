import asyncio
import json
import logging
import pathlib
import re
import sys
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

import aiostream.stream
import anchorpy.error
from collections import defaultdict
from pyserum.async_open_orders_account import AsyncOpenOrdersAccount
from pyserum.market import AsyncMarket, OrderBook
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed
from solana.rpc.websocket_api import connect
from solana.transaction import AccountMeta, Transaction
from solders.rpc.responses import AccountNotification
from solders.account import Account

from mango_explorer_v4.accounts.bank import Bank
from mango_explorer_v4.accounts.book_side import BookSide
from mango_explorer_v4.accounts.event_queue import EventQueue
from mango_explorer_v4.accounts.mango_account import MangoAccount
from mango_explorer_v4.accounts.mint_info import MintInfo
from mango_explorer_v4.accounts.perp_market import PerpMarket
from mango_explorer_v4.accounts.serum3_market import Serum3Market
from mango_explorer_v4.helpers.serum3_orders import Serum3OrdersHelper
from mango_explorer_v4.helpers.token_position import TokenPositionHelper
from mango_explorer_v4.helpers.perp_market import PerpMarketHelper
from mango_explorer_v4.helpers.perp_position import PerpPositionHelper
from mango_explorer_v4.helpers.bank import BankHelper
from mango_explorer_v4.helpers.prices import PricesHelper
from mango_explorer_v4.helpers.mango_account import MangoAccountHelper
from mango_explorer_v4.helpers.token_info import TokenInfoHelper
from mango_explorer_v4.helpers.serum3_info import Serum3InfoHelper
from mango_explorer_v4.helpers.perp_info import PerpInfoHelper
from mango_explorer_v4.instructions.perp_cancel_all_orders import PerpCancelAllOrdersArgs, PerpCancelAllOrdersAccounts, perp_cancel_all_orders
from mango_explorer_v4.instructions.perp_place_order import PerpPlaceOrderArgs, PerpPlaceOrderAccounts, perp_place_order
from mango_explorer_v4.instructions.perp_place_order_pegged import PerpPlaceOrderPeggedArgs, PerpPlaceOrderPeggedAccounts, perp_place_order_pegged
from mango_explorer_v4.instructions.serum3_cancel_all_orders import Serum3CancelAllOrdersAccounts, Serum3CancelAllOrdersArgs, serum3_cancel_all_orders
from mango_explorer_v4.instructions.serum3_create_open_orders import Serum3CreateOpenOrdersAccounts, serum3_create_open_orders
from mango_explorer_v4.instructions.serum3_place_order import Serum3PlaceOrderArgs, Serum3PlaceOrderAccounts, serum3_place_order
from mango_explorer_v4.program_id import PROGRAM_ID as MANGO_PROGRAM_ID
from mango_explorer_v4.types import place_order_type
from mango_explorer_v4.types import serum3_side, serum3_self_trade_behavior, serum3_order_type
from mango_explorer_v4.types.fill_event import FillEvent
from mango_explorer_v4.types.place_order_type import Limit
from mango_explorer_v4.types.side import Bid, Ask
from mango_explorer_v4.types.token_info import TokenInfo
from mango_explorer_v4.types.perp_info import PerpInfo
from mango_explorer_v4.types.prices import Prices
from mango_explorer_v4.types.i80f48 import I80F48
from mango_explorer_v4.types.health_type import Init, Maint, LiquidationEnd
from mango_explorer_v4.types.serum3_info import Serum3Info
from mango_explorer_v4.types.health_cache import HealthCache
from mango_explorer_v4.types.health_type import HealthTypeKind
from .constants import RUST_I64_MAX, SERUM_PROGRAM_ID
from .constructs.book_side_items import BookSideItems
from .constructs.serum3_reserved import Serum3Reserved
from .oracles import pyth

logging.basicConfig(
    level=logging.INFO
)


@dataclass
class MangoClient():
    connection: AsyncClient
    group_config: dict
    serum_market_configs: [dict]
    perp_market_configs: [dict]
    serum_markets: [Serum3Market]
    serum_markets_external: [AsyncMarket]
    perp_markets: [PerpMarket]
    banks: [Bank]
    mint_infos: [MintInfo]

    @staticmethod
    async def connect(rpc_url: str = 'https://mango.rpcpool.com/0f9acc0d45173b51bf7d7e09c1e5'):
        connection = AsyncClient(rpc_url, Processed)

        ids = json.loads(open(pathlib.Path(__file__).parent / 'ids.json').read())
        # TODO: ^ Make it fetch from https://api.mngo.cloud/data/v4/group-metadata instead

        group_config = [group_config for group_config in ids['groups'] if group_config['publicKey'] == '78b8f4cGCwmZ9ysPFMWLaLTkkaYnUjwMJYStWe5RTSSX'][0]
        # TODO: ^ Un-hardcode the group config public key (not necessary for now as there's only mainnet)

        perp_market_configs = [
            perp_market_config for perp_market_config in group_config['perpMarkets'] if perp_market_config['active']
        ]

        serum_market_configs = [
            serum_market_config for serum_market_config in group_config['serum3Markets'] if serum_market_config['active']
        ]

        bank_configs = [
            {
                'tokenIndex': token_config['tokenIndex'],
                'publicKey': PublicKey(token_config['banks'][0]['publicKey'])
            }
            for token_config in group_config['tokens']
            if token_config['active']
        ]

        mint_info_configs = [
            {
                'tokenIndex': token_config['tokenIndex'],
                'publicKey': PublicKey(token_config['mintInfo'])
            }
            for token_config in group_config['tokens']
            if token_config['active']
        ]

        mint_info_configs = list(sorted(mint_info_configs, key=lambda mint_info_config: mint_info_config['tokenIndex']))

        serum_markets = await Serum3Market.fetch_multiple(
            connection,
            [
                PublicKey(serum3_market_config['publicKey']) for serum3_market_config in serum_market_configs
            ]
        )

        serum_markets_external = await asyncio.gather(*[
            AsyncMarket.load(connection, serum_market.serum_market_external, SERUM_PROGRAM_ID)
            for serum_market in serum_markets
        ])

        banks, mint_infos, perp_markets = await asyncio.gather(*[
            Bank.fetch_multiple(
                connection,
                [bank_config['publicKey'] for bank_config in bank_configs]
            ),
            MintInfo.fetch_multiple(
                connection,
                [mint_info_config['publicKey'] for mint_info_config in mint_info_configs]
            ),
            PerpMarket.fetch_multiple(
                connection,
                [perp_market_config['publicKey'] for perp_market_config in perp_market_configs]
            )
        ])

        return MangoClient(
            connection=connection,
            group_config=group_config,
            serum_market_configs=serum_market_configs,
            perp_market_configs=perp_market_configs,
            serum_markets=serum_markets,
            serum_markets_external=serum_markets_external,
            perp_markets=perp_markets,
            banks=banks,
            mint_infos=mint_infos
        )

    def symbols(self):
        # This might not be the best format for keeping symbols organized,
        # as it presumes that perpetual and spot market names would never
        # conflict, but it works for now

        # TODO: Add minimum order size, tick size and liquidation fee
        return [
            *[
                {
                    'name': perp_market_config['name'],
                    'type': 'perpetual',
                    'base_currency': perp_market_config['name'].split('-')[0],
                    'quote_currency': 'USDC',
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

                response = await self.connection.get_multiple_accounts([
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

                accounts = await self.connection.get_multiple_accounts([perp_market.bids, perp_market.asks, perp_market.oracle])

                [raw_bids, raw_asks, raw_oracle] = accounts.value

                [bids, asks] = [BookSide.decode(raw_bids.data), BookSide.decode(raw_asks.data)]

                oracle = pyth.PRICE.parse(raw_oracle.data)

                oracle_price = oracle.agg.price * (Decimal(10) ** oracle.expo)

                orderbook = {
                    'symbol': symbol,
                    'bids': BookSideItems('bids', bids, perp_market, oracle_price).l2()[:depth],
                    'asks': BookSideItems('asks', asks, perp_market, oracle_price).l2()[:depth],
                    'slot': accounts.context.slot
                }

                return orderbook

    async def incremental_orderbook_l2(self, symbol: str, depth: int = 50):
        # TODO: Validate the symbol exists
        market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", symbol)[1]]

        yield await self.orderbook_l2(symbol, depth)

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

                orderbook = {
                    'symbol': symbol,
                    'bids': None,
                    'asks': None
                }

                async def snapshots(side):
                    async with connect(self.connection._provider.endpoint_uri.replace('https://', 'wss://')) as websocket:
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

                                yield side, orders, submessage.result.context.slot

                async with aiostream.stream.merge(*[stream for stream in [snapshots(side) for side in ['bids', 'asks']]]).stream() as streamer:
                    async for side, orders, slot in streamer:
                        orderbook[side] = orders

                        if not all([orderbook['bids'], orderbook['asks']]):
                            continue

                        yield orderbook

            case 'perpetual':
                perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

                perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

                state = {
                    'oracle_price': None
                }

                orderbook = {
                    'symbol': symbol,
                    'bids': None,
                    'asks': None
                }

                async def oracle_price():
                    async with connect(self.connection._provider.endpoint_uri.replace('https://', 'wss://')) as websocket:
                        await websocket.account_subscribe(perp_market.oracle, Processed, 'jsonParsed')

                        async for message in websocket:
                            for submessage in message:
                                if not isinstance(submessage, AccountNotification):
                                    continue

                                oracle = pyth.PRICE.parse(submessage.result.value.data)

                                yield {
                                    'channel': 'oracle_price',
                                    'symbol': symbol,
                                    'value': float(Decimal(str(oracle.agg.price)) * Decimal(10) ** Decimal(str(oracle.expo)))
                                }

                async def book(side):
                    async with connect(self.connection._provider.endpoint_uri.replace('https://', 'wss://')) as websocket:
                        await websocket.account_subscribe(getattr(perp_market, side), Processed, 'jsonParsed')

                        async for message in websocket:
                            for submessage in message:
                                if not isinstance(submessage, AccountNotification):
                                    continue

                            if not state['oracle_price']:
                                continue

                            yield {
                                'channel': 'book',
                                'side': side,
                                'orders': BookSideItems(side, BookSide.decode(submessage.result.value.data), perp_market, state['oracle_price']).l2()
                            }

                async with aiostream.stream.merge(*[oracle_price(), *[book(side) for side in ['bids', 'asks']]]).stream() as streamer:
                    async for message in streamer:
                        match message['channel']:
                            case 'oracle_price':
                                state['oracle_price'] = message['value']
                            case 'book':
                                orderbook[message['side']] = message['orders']

                        if not all([orderbook['bids'], orderbook['asks']]):
                            continue

                        yield orderbook

    async def fills(self, symbol: str):
        # TODO: Validate that the symbol entered is valid

        market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", symbol)[1]]

        match market_type:
            case 'spot':
                raise NotImplementedError("Spot markets fills retrieval isn't implemented yet")
            case 'perpetual':
                perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

                perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

                response = await self.connection.get_account_info(perp_market.event_queue)

                event_queue = EventQueue.decode(response.value.data)

                fills = sorted(
                    [
                        fill
                        for fill in [
                            FillEvent.layout.parse(bytes([event.event_type] + event.padding))
                            for event in event_queue.buf
                            if event.event_type == 0
                        ]
                    ],
                    key=lambda fill: fill.seq_num
                )

                return {
                    'symbol': symbol,
                    'fills': [
                        {
                            'side': 'bids' if fill.taker_side else 'asks',
                            'price': PerpMarketHelper.price_lots_to_ui(perp_market, fill.price),
                            'size': PerpMarketHelper.base_lots_to_ui(perp_market, fill.quantity),
                            'taker': fill.taker,
                            'maker': fill.maker,
                            'timestamp': fill.timestamp
                        }
                        for fill in fills
                    ],
                    'slot': response.context.slot
                }

    async def incremental_fills(self, symbol: str):
        # TODO: Validate the symbol exists
        market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", symbol)[1]]

        match market_type:
            case 'spot':
                raise NotImplementedError("Spot markets incremental fills retrieval isn't implemented yet")
            case 'perpetual':
                perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

                perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

                lead = None

                async with connect(self.connection._provider.endpoint_uri.replace('https://', 'wss://')) as websocket:
                    await websocket.account_subscribe(perp_market.event_queue, Processed, 'jsonParsed')

                    async for message in websocket:
                        for submessage in message:
                            if not isinstance(submessage, AccountNotification):
                                continue

                            event_queue = EventQueue.decode(submessage.result.value.data)

                            fills = sorted(
                                [
                                    fill
                                    for fill in [
                                        FillEvent.layout.parse(bytes([event.event_type] + event.padding))
                                        for event in event_queue.buf
                                        if event.event_type == 0
                                    ]
                                    if fill.taker != PublicKey(0)
                                ],
                                key=lambda fill: fill.seq_num
                            )

                            if lead:
                                fills = [fill for fill in fills if fill.seq_num > lead]

                                if len(fills) == 0:
                                    continue

                            yield {
                                'symbol': symbol,
                                'is_snapshot': False,
                                'fills': [
                                    {
                                        'side': 'bids' if fill.taker_side else 'asks',
                                        'price': PerpMarketHelper.price_lots_to_ui(perp_market, fill.price),
                                        'size': PerpMarketHelper.base_lots_to_ui(perp_market, fill.quantity),
                                        'taker': fill.taker,
                                        'maker': fill.maker,
                                        'timestamp': fill.timestamp
                                    }
                                    for fill in fills
                                ],
                                'slot': submessage.result.context.slot
                            }

                            lead = fills[-1:][0].seq_num

    async def funding_rate(self, symbol: str):
        """

        Returns instantaneous funding rate for the day: funding is continuously
        applied on every interaction with a perp position. The rate is further
        multiplied by the time elapsed since it was last applied (capped to max. 1hr).

        :param symbol:
        :return: instantaneous funding rate in % form
        """
        perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

        perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

        accounts = await self.connection.get_multiple_accounts([perp_market.bids, perp_market.asks, perp_market.oracle])

        raw_bids, raw_asks, raw_oracle = accounts.value

        bids, asks, oracle = BookSide.decode(raw_bids.data), BookSide.decode(raw_asks.data), pyth.PRICE.parse(raw_oracle.data)

        oracle_price = float(Decimal(str(oracle.agg.price)) * Decimal(10) ** oracle.expo)

        [bids, asks] = [BookSideItems('bids', bids, perp_market, oracle_price), BookSideItems('asks', asks, perp_market, oracle_price)]

        min_funding, max_funding = float(perp_market.min_funding.to_decimal()), float(perp_market.max_funding.to_decimal())

        impact_quantity = PerpMarketHelper.base_lots_to_ui(perp_market, perp_market.impact_quantity)

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

        return funding * 100

    async def get_mango_account(self, public_key: str): return await MangoAccount.fetch(self.connection, PublicKey(public_key))

    async def get_all_mango_accounts(self):
        response = await self.connection.get_program_accounts(
            MANGO_PROGRAM_ID,
            encoding='base64'
        )

        mango_accounts = []

        for entry in response.value: # TODO: Use proper filters instead
            try:
                mango_account = MangoAccount.decode(entry.account.data, entry.pubkey)
            except anchorpy.error.AccountInvalidDiscriminator:
                continue

            mango_accounts.append(mango_account)

        return mango_accounts

    def _health_remaining_accounts(
        self,
        retriever: Literal['fixed', 'scanning'],
        banks: [Bank],
        perp_markets: [PerpMarket],
        mango_account: MangoAccount
    ) -> [AccountMeta]:
        health_remaining_account_pks = []

        match retriever:
            case 'fixed':
                token_indices = [token.token_index for token in mango_account.tokens]

                for bank in banks:
                    if bank.token_index not in token_indices:
                        index = [
                            idx for idx, token in enumerate(mango_account.tokens)
                            if token.token_index == 65535
                            if token_indices[idx] == 65535
                        ][0]

                        token_indices[index] = bank.token_index

                mint_infos = [
                    [mint_info for mint_info in self.mint_infos if mint_info.token_index == token_index][0]
                    for token_index in token_indices if token_index != 65535
                ]

                health_remaining_account_pks.extend([mint_info.banks[0] for mint_info in mint_infos])

                health_remaining_account_pks.extend([mint_info.oracle for mint_info in mint_infos])

                perp_market_indices = [perp.market_index for perp in mango_account.perps]

                for perp_market in perp_markets:
                    if perp_market.perp_market_index not in perp_market_indices:
                        index = [
                            idx for idx, perp in enumerate(mango_account.perps)
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

                health_remaining_account_pks.extend([serum3.open_orders for serum3 in mango_account.serum3 if serum3.market_index != 65535])
            case 'scanning':
                raise NotImplementedError()

        remaining_accounts: [AccountMeta] = [
            AccountMeta(pubkey=remaining_account_pk, is_writable=False, is_signer=False)
            for remaining_account_pk in health_remaining_account_pks
        ]

        return remaining_accounts

    def make_serum3_create_open_orders_ix(self, mango_account: MangoAccount, symbol: str):
        # TODO: Check whether the symbol matches a valid Serum market name
        serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

        serum_market_index = serum_market_config['marketIndex']

        serum_market = [
            serum_market
            for serum_market in self.serum_markets
            if serum_market.market_index == serum_market_index
        ][0]

        [open_orders, _] = PublicKey.find_program_address(
            [
                bytes('Serum3OO', 'utf-8'),
                bytes(mango_account.public_key),
                bytes(PublicKey(serum_market_config['publicKey']))
            ],
            MANGO_PROGRAM_ID
        )

        serum3_create_open_orders_accounts: Serum3CreateOpenOrdersAccounts = {
            'group': mango_account.group,
            'account': mango_account.public_key,
            'owner': mango_account.owner,
            'serum_market': PublicKey(serum_market_config['publicKey']),
            'serum_program': serum_market.serum_program,
            'serum_market_external': serum_market.serum_market_external,
            'open_orders': open_orders,
            'payer': mango_account.owner
        }

        serum3_create_open_orders_ix = serum3_create_open_orders(serum3_create_open_orders_accounts)

        return serum3_create_open_orders_ix

    def make_serum3_place_order_ix(self, mango_account: MangoAccount, symbol: str, side: Literal['bids', 'asks'], price: float, size: float):
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

        [open_orders, _] = PublicKey.find_program_address(
            [
                bytes('Serum3OO', 'utf-8'),
                bytes(mango_account.public_key),
                bytes(PublicKey(serum_market_config['publicKey']))
            ],
            MANGO_PROGRAM_ID
        )

        payer_token_index = {
            'bids': serum_market.quote_token_index,
            'asks': serum_market.base_token_index
        }[side]

        bank = [bank for bank in self.banks if bank.token_index == payer_token_index][0]

        bank_configs = [
            {
                'tokenIndex': token_config['tokenIndex'],
                'publicKey': PublicKey(token_config['banks'][0]['publicKey'])
            }
            for token_config in self.group_config['tokens']
            if token_config['active']
        ]

        bank_config = [bank_config for bank_config in bank_configs if bank_config['tokenIndex'] == bank.token_index][0]

        serum_market_external_vault_signer_address = PublicKey.create_program_address([
            bytes(serum_market.serum_market_external),
            serum_market_external.state.vault_signer_nonce().to_bytes(8, 'little')
        ], SERUM_PROGRAM_ID)

        serum3_place_order_accounts: Serum3PlaceOrderAccounts = {
            'group': mango_account.group,
            'account': mango_account.public_key,
            'owner': mango_account.owner,
            'open_orders': open_orders,
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

        remaining_accounts = self._health_remaining_accounts('fixed', [], [], mango_account)

        serum3_place_order_ix = serum3_place_order(
            serum3_place_order_args,
            serum3_place_order_accounts,
            remaining_accounts=remaining_accounts
        )

        return serum3_place_order_ix

    def make_perp_place_order_ix(self, mango_account: MangoAccount, symbol, side, price, size):
        perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

        perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

        perp_place_order_args: PerpPlaceOrderArgs = {
            'side': {'bids': Bid, 'asks': Ask}[side],
            'price_lots': PerpMarketHelper.ui_price_to_lots(perp_market, price),
            'max_base_lots': PerpMarketHelper.ui_base_to_lots(perp_market, size),
            'max_quote_lots': sys.maxsize,
            'client_order_id': int(time.time() * 1e3),
            'order_type': place_order_type.Limit(),
            'reduce_only': False,
            'expiry_timestamp': 0,
            'limit': 10
        }

        perp_place_order_accounts: PerpPlaceOrderAccounts = {
            'group': perp_market.group,
            'account': mango_account.public_key,
            'owner': mango_account.owner,
            'perp_market': PublicKey(perp_market_config['publicKey']),
            'bids': perp_market.bids,
            'asks': perp_market.asks,
            'event_queue': perp_market.event_queue,
            'oracle': perp_market.oracle
        }

        remaining_accounts = self._health_remaining_accounts('fixed', [[bank for bank in self.banks if bank.token_index == 0][0]], [perp_market], mango_account)

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
        size: float,
        mango_account: MangoAccount,
        keypair: Keypair
    ):
        market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", symbol)[1]]

        match market_type:
            case 'spot':
                serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

                serum_market_index = serum_market_config['marketIndex']

                tx = Transaction()

                try:
                    serum3 = [serum3 for serum3 in mango_account.serum3 if serum3.market_index == serum_market_index][0]
                except IndexError:
                    tx.add(self.make_serum3_create_open_orders_ix(mango_account, symbol))

                serum3_place_order_ix = self.make_serum3_place_order_ix(
                    mango_account,
                    symbol,
                    side,
                    price,
                    size
                )

                recent_blockhash = str((await self.connection.get_latest_blockhash()).value.blockhash)

                tx.add(serum3_place_order_ix)

                response = await self.connection.send_transaction(tx, keypair, recent_blockhash=recent_blockhash)

                return response
            case 'perpetual':
                tx = Transaction()

                recent_blockhash = str((await self.connection.get_latest_blockhash()).value.blockhash)

                perp_place_order_ix = self.make_perp_place_order_ix(mango_account, symbol, side, price, size)

                tx.add(perp_place_order_ix)

                response = await self.connection.send_transaction(tx, keypair, recent_blockhash=recent_blockhash)

                return response

    def make_serum3_cancel_all_orders_ix(self, mango_account: MangoAccount, symbol: str):
        serum_market_config = [serum3_market_config for serum3_market_config in self.group_config['serum3Markets'] if serum3_market_config['name'] == symbol][0]

        serum_market_index = serum_market_config['marketIndex']

        serum_market = [
            serum_market
            for serum_market in self.serum_markets
            if serum_market.market_index == serum_market_index
        ][0]

        try:
            serum3 = [serum3 for serum3 in mango_account.serum3 if serum3.market_index == serum_market_index][0]
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
            'group': mango_account.group,
            'account': mango_account.public_key,
            'owner': mango_account.owner,
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

    def make_perp_cancel_all_orders_ix(self, mango_account: MangoAccount, symbol: str):
        perp_market_config = [perp_market_config for perp_market_config in self.group_config['perpMarkets'] if perp_market_config['name'] == symbol][0]

        perp_market = [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_market_config['marketIndex']][0]

        perp_cancel_all_orders_args: PerpCancelAllOrdersArgs = {
            'limit': 10
        }

        perp_cancel_all_orders_accounts: PerpCancelAllOrdersAccounts = {
            'group': perp_market.group,
            'account': mango_account.public_key,
            'owner': mango_account.owner,
            'perp_market': PublicKey(perp_market_config['publicKey']),
            'bids': perp_market.bids,
            'asks': perp_market.asks
        }

        perp_cancel_all_orders_ix = perp_cancel_all_orders(perp_cancel_all_orders_args, perp_cancel_all_orders_accounts)

        return perp_cancel_all_orders_ix

    async def cancel_all_orders(self, mango_account: MangoAccount, keypair: Keypair, symbol: str):
        market_type = {'PERP': 'perpetual', 'USDC': 'spot'}[re.split(r"[-|/]", symbol)[1]]

        match market_type:
            case 'spot':
                tx = Transaction()

                recent_blockhash = str((await self.connection.get_latest_blockhash()).value.blockhash)

                serum3_cancel_all_orders_ix = self.make_serum3_cancel_all_orders_ix(mango_account, symbol)

                tx.add(serum3_cancel_all_orders_ix)

                response = await self.connection.send_transaction(tx, keypair, recent_blockhash=recent_blockhash)

                return response
            case 'perpetual':
                tx = Transaction()

                recent_blockhash = str((await self.connection.get_latest_blockhash()).value.blockhash)

                tx.recent_blockhash = str(recent_blockhash)

                perp_cancel_all_orders_ix = self.make_perp_cancel_all_orders_ix(mango_account, symbol)

                tx.add(perp_cancel_all_orders_ix)

                response = await self.connection.send_transaction(tx, keypair, recent_blockhash=recent_blockhash)

                return response

    async def balances(self, mango_account: MangoAccount):
        committed = defaultdict(lambda: 0.0)

        token_positions = MangoAccountHelper.active_token_positions(mango_account)

        for token_position in token_positions:
            bank = [bank for bank in self.banks if bank.token_index == token_position.token_index][0]

            token_config = [
                token_config for token_config in self.group_config['tokens']
                if token_config['tokenIndex'] == token_position.token_index
            ][0]

            token_indexed_position = token_position.indexed_position.to_decimal()

            bank_deposit_index = bank.deposit_index.to_decimal()

            bank_borrow_index = bank.borrow_index.to_decimal()

            balance = float(
                token_indexed_position * (
                    bank_deposit_index
                    if token_indexed_position > 0
                    else bank_borrow_index
                )
                /
                10 ** bank.mint_decimals
            )

            committed[token_config['symbol']] = balance

        in_orders = defaultdict(lambda: 0.0)

        unsettled = defaultdict(lambda: 0.0)

        open_orders = MangoAccountHelper.active_serum3_orders(mango_account)

        for open_order, open_orders_external in zip(
            open_orders,
            await asyncio.gather(*[
                AsyncOpenOrdersAccount.load(self.connection, str(open_orders.open_orders))
                for open_orders
                in open_orders
            ]) # TODO: ^ Use one RPC call
        ):
            base_bank = [bank for bank in self.banks if bank.token_index == open_order.base_token_index][0]

            quote_bank = [bank for bank in self.banks if bank.token_index == open_order.quote_token_index][0]

            base_name = bytes(base_bank.name).decode().strip('\x00')

            quote_name = bytes(quote_bank.name).decode().strip('\x00')

            base_token_unsettled = float(
                Decimal(open_orders_external.base_token_free) / Decimal(10 ** base_bank.mint_decimals)
            )

            quote_token_unsettled = float(
                Decimal(open_orders_external.quote_token_free) / Decimal(10 ** quote_bank.mint_decimals)
            )

            base_token_locked = float(
                Decimal(open_orders_external.base_token_total - open_orders_external.base_token_free)
                /
                Decimal(10 ** base_bank.mint_decimals)
            )

            quote_token_locked = float(
                Decimal(open_orders_external.quote_token_total - open_orders_external.quote_token_free)
                /
                Decimal(10 ** quote_bank.mint_decimals)
            )

            in_orders[base_name] += base_token_locked

            in_orders[quote_name] += quote_token_locked

            unsettled[base_name] += base_token_unsettled

            unsettled[quote_name] += quote_token_unsettled

        entries = []

        for symbol in {*committed.keys(), *in_orders.keys(), *unsettled.keys()}:
            content = {
                'balance': committed.get(symbol, 0),
                'in_orders': in_orders.get(symbol, 0),
                'unsettled': unsettled.get(symbol, 0)
            }

            entries.append((symbol, content))

        return dict(entries)

    def make_place_perp_pegged_order_ix(
        self,
        mango_account: MangoAccount,
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
            'price_offset_lots': PerpMarketHelper.ui_price_to_lots(perp_market, price_offset),
            'peg_limit': PerpMarketHelper.ui_price_to_lots(perp_market, peg_limit),
            'max_base_lots': PerpMarketHelper.ui_base_to_lots(perp_market, quantity),
            'max_quote_lots': PerpMarketHelper.ui_quote_to_lots(perp_market, max_quote_quantity) if max_quote_quantity else RUST_I64_MAX,
            'client_order_id': client_order_id,
            'order_type': Limit,
            'reduce_only': reduce_only,
            'expiry_timestamp': expiry_timestamp,
            'limit': limit,
            'max_oracle_staleness_slots': -1
        }

        perp_place_order_pegged_accounts: PerpPlaceOrderPeggedAccounts = {
            'group': PublicKey(self.group_config['publicKey']),
            'account': mango_account.public_key,
            'owner': mango_account.owner,
            'perp_market': PublicKey(perp_market_config['publicKey']),
            'bids': perp_market.bids,
            'asks': perp_market.asks,
            'event_queue': perp_market.event_queue,
            'oracle': perp_market.oracle
        }

        remaining_accounts = self._health_remaining_accounts(
            'fixed',
            [bank for bank in self.banks if bank.token_index == 0],
            [perp_market],
            mango_account
        )

        return perp_place_order_pegged(
            perp_place_order_pegged_args,
            perp_place_order_pegged_accounts,
            remaining_accounts=remaining_accounts
        )

    async def place_perp_pegged_order(
        self,
        mango_account: MangoAccount,
        keypair: Keypair,
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

        recent_blockhash = str((await self.connection.get_latest_blockhash()).value.blockhash)

        tx.add(
            self.make_place_perp_pegged_order_ix(
                mango_account,
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

        response = await self.connection.send_transaction(tx, keypair, recent_blockhash=recent_blockhash)

        return response

    async def equity(self, mango_account: MangoAccount):
        oracle_price_by_token_index = {}

        oracle_price_by_oracle_pk = {}

        for bank, raw_oracle in zip(
            self.banks,
            await asyncio.gather(*[self.connection.get_account_info(bank.oracle) for bank in self.banks])
        ):
            name = bytes(bank.name).decode().strip('\x00')

            if name == 'USDC':
                oracle_price = 1
            else:
                # TODO: Handle MNGO's oracle (not Pyth)

                oracle = pyth.PRICE.parse(raw_oracle.value.data)

                oracle_price = oracle.agg.price * (Decimal(10) ** oracle.expo)

            oracle_price_by_token_index[bank.token_index] = oracle_price

            oracle_price_by_oracle_pk[bank.oracle] = oracle_price

        balance_by_token_index = {}

        for token, bank in [
            (
                token,
                [bank for bank in self.banks if bank.token_index == token.token_index][0]
            )
            for token in filter(TokenPositionHelper.is_active, mango_account.tokens)
        ]:
            oracle_price = oracle_price_by_token_index[token.token_index]

            balance_by_token_index[token.token_index] = Decimal(str(TokenPositionHelper.balance(token, bank))) * oracle_price

        active_open_orders = [open_orders for open_orders in mango_account.serum3 if Serum3OrdersHelper.is_active(open_orders)]

        for open_orders, open_orders_external in zip(
            active_open_orders,
            await asyncio.gather(*[
                AsyncOpenOrdersAccount.load(self.connection, str(open_orders.open_orders))
                for open_orders
                in active_open_orders
            ])
        ):
            balance_by_token_index[open_orders.base_token_index] += ((open_orders_external.base_token_total) * oracle_price_by_token_index[open_orders.base_token_index] * Decimal(10 ** (6 - bank.mint_decimals))) / Decimal(1e6)

            balance_by_token_index[open_orders.base_token_index] += (open_orders_external.quote_token_total * oracle_price_by_token_index[open_orders.quote_token_index]) / Decimal(1e6)

        token_equity = sum(balance_by_token_index.values())

        perp_equity = sum([
            PerpPositionHelper.equity(perp_position, perp_market, oracle_price_by_oracle_pk[perp_market.oracle])
            for perp_position, perp_market in [
                (
                    perp_position,
                    [perp_market for perp_market in self.perp_markets if perp_market.perp_market_index == perp_position.market_index][0]
                )
                for perp_position in mango_account.perps
                if PerpPositionHelper.is_active(perp_position)
            ]
        ])

        return token_equity + perp_equity

    async def health_ratio(self, mango_account: MangoAccount, health_type: Literal['init', 'maint', 'liquidation_end']):
        health_type: HealthTypeKind = {
            'init': Init(),
            'maint': Maint(),
            'liquidation_end': LiquidationEnd()
        }[health_type]

        # Build the health cache

        token_positions = [
            token_position
            for token_position in mango_account.tokens
            if token_position.token_index != 65535
        ]

        banks = [
            [bank for bank in self.banks if bank.token_index == token_position.token_index][0]
            for token_position in token_positions
        ]

        raw_oracles = await self.connection.get_multiple_accounts([bank.oracle for bank in banks])

        def oracle_price_from_account_info(account: Account):
            match str(account.owner):
                case 'FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH': # Pyth
                    oracle = pyth.PRICE.parse(account.data)

                    return oracle.agg.price * (Decimal(10) ** oracle.expo)
                case '4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg': # For now it's always USDC
                    return Decimal(1)

        oracle_prices = [
            oracle_price_from_account_info(account)
            for account in raw_oracles.value
        ]

        token_infos = [
            TokenInfo(
                bank.token_index,
                bank.maint_asset_weight,
                bank.init_asset_weight,
                BankHelper.scaled_init_asset_weight(bank, PricesHelper.liab(prices, Init())),
                bank.maint_liab_weight,
                bank.init_liab_weight,
                BankHelper.scaled_init_liab_weight(bank, PricesHelper.liab(prices, Init())),
                prices,
                I80F48.from_decimal(TokenPositionHelper.balance(token_position, bank))
            )
            for bank, token_position, prices
            in zip(
                banks,
                token_positions,
                [
                    Prices(
                        oracle=I80F48.from_decimal(oracle_price * Decimal(10 ** (6 - bank.mint_decimals))),
                        stable=I80F48.from_decimal(Decimal(bank.stable_price_model.stable_price))
                    )
                    for bank, oracle_price in zip(banks, oracle_prices)
                ]
            )
        ]

        serum3_infos = []

        for open_orders, open_orders_external in zip(
                MangoAccountHelper.active_serum3_orders(mango_account),
                await asyncio.gather(*[
                    AsyncOpenOrdersAccount.load(self.connection, str(open_orders.open_orders))
                    for open_orders
                    in MangoAccountHelper.active_serum3_orders(mango_account)
                ])
        ):
            base_index, base_info = [
                (index, token_info)
                for index, token_info in enumerate(token_infos)
                if token_info.token_index == open_orders.base_token_index
            ][0]

            if not base_info:
                raise ValueError(f"Base token info not found for market index {open_orders.market_index}")

            quote_index, quote_info = [
                (index, token_info)
                for index, token_info in enumerate(token_infos)
                if token_info.token_index == open_orders.quote_token_index
            ][0]

            if not quote_info:
                raise ValueError(f"Quote token info not found for market index {open_orders.market_index}")

            reserved_base = open_orders_external.base_token_total - open_orders_external.base_token_free

            reserved_quote = open_orders_external.quote_token_total - open_orders_external.quote_token_free

            serum3_infos.append(
                Serum3Info(
                    reserved_base=I80F48.from_decimal(Decimal(reserved_base)),
                    reserved_quote=I80F48.from_decimal(Decimal(reserved_quote)),
                    base_index=base_index,
                    quote_index=quote_index,
                    market_index=open_orders.market_index,
                    has_zero_funds=False
                )
            )

        perp_positions = MangoAccountHelper.active_perp_positions(mango_account)

        perp_markets = [
            [
                perp_market
                for perp_market in self.perp_markets
                if perp_market.perp_market_index == perp_position.market_index
            ][0]
            for perp_position in perp_positions

        ]

        perp_market_oracle_prices = [
            oracle_price_from_account_info(raw_oracle)
            for raw_oracle in (await self.connection.get_multiple_accounts([perp_market.oracle for perp_market in perp_markets])).value
        ]

        perp_infos = []

        for perp_position, perp_market, perp_market_oracle_price in zip(
            perp_positions,
            perp_markets,
            perp_market_oracle_prices
        ):
            base_lots = perp_position.base_position_lots + perp_position.taker_base_lots

            unsettled_funding = PerpPositionHelper.unsettled_funding(perp_position, perp_market)

            taker_quote = perp_position.taker_quote_lots * perp_market.quote_lot_size

            quote_current = I80F48.from_decimal(perp_position.quote_position_native.to_decimal() - unsettled_funding + Decimal(taker_quote))

            perp_info = PerpInfo(
                perp_market.perp_market_index,
                perp_market.maint_base_asset_weight,
                perp_market.init_base_asset_weight,
                perp_market.maint_base_liab_weight,
                perp_market.init_base_liab_weight,
                perp_market.maint_overall_asset_weight,
                perp_market.init_overall_asset_weight,
                perp_market.base_lot_size,
                base_lots,
                perp_position.bids_base_lots,
                perp_position.asks_base_lots,
                quote_current,
                Prices(
                    oracle=I80F48.from_decimal(perp_market_oracle_price * Decimal(10 ** (6 - perp_market.base_decimals))),
                    stable=I80F48.from_decimal(Decimal(perp_market.stable_price_model.stable_price))
                ),
                PerpPositionHelper.has_open_orders(perp_position),
                PerpPositionHelper.has_open_fills(perp_position)
            )

            perp_infos.append(perp_info)

        health_cache = HealthCache(
            token_infos,
            serum3_infos,
            perp_infos,
            False
        )

        # Compute assets and liabilities

        assets = 0

        liabs = 0

        for token_info in health_cache.token_infos:
            contrib = TokenInfoHelper.health_contribution(token_info, health_type)

            if contrib > 0:
                assets += contrib
            else:
                liabs -= contrib

        def get_serum3_reservations(health_type: HealthTypeKind):
            token_max_reserved = [0 for _ in range(0, len(token_infos))]

            serum3_reserved: [Serum3Reserved] = []

            for serum3_info in serum3_infos:
                quote, base = token_infos[serum3_info.quote_index], token_infos[serum3_info.base_index]

                reserved_base, reserved_quote = serum3_info.reserved_base.to_decimal(), serum3_info.reserved_quote.to_decimal()

                quote_asset = PricesHelper.asset(quote.prices, health_type)

                base_liab = PricesHelper.liab(base.prices, health_type)

                all_reserved_as_base = reserved_base + reserved_quote * quote_asset / base_liab

                base_asset = PricesHelper.asset(base.prices, health_type)

                quote_liab = PricesHelper.liab(quote.prices, health_type)

                all_reserved_as_quote = reserved_quote + reserved_base * base_asset / quote_liab

                token_max_reserved[serum3_info.base_index] += all_reserved_as_base

                token_max_reserved[serum3_info.quote_index] += all_reserved_as_quote

                serum3_reserved.append(Serum3Reserved(all_reserved_as_base, all_reserved_as_quote))

            return {
                'token_max_reserved': token_max_reserved,
                'serum3_reserved': serum3_reserved
            }

        res = get_serum3_reservations(Maint())

        for index, serum3_info in enumerate(serum3_infos):
            contrib = Serum3InfoHelper.health_contribution(
                serum3_info,
                health_type,
                health_cache.token_infos,
                res['token_max_reserved'],
                res['serum3_reserved'][index]
            ).to_decimal()

            if contrib > 0:
                assets += contrib
            else:
                liabs -= contrib

        for perp_info in health_cache.perp_infos:
            contrib = PerpInfoHelper.health_contribution(perp_info, health_type).to_decimal()

            if contrib > 0:
                assets += contrib
            else:
                liabs -= contrib

        if liabs > 0.001:
            return 100 * (assets - liabs) / liabs
        else:
            return sys.maxsize

    async def positions(self, mango_account: MangoAccount):
        perp_positions = MangoAccountHelper.active_perp_positions(mango_account)

        perp_markets = [
            [
                perp_market for perp_market in self.perp_markets
                if perp_market.perp_market_index == perp_position.market_index
            ][0]
            for perp_position in perp_positions
        ]

        perp_market_configs = [
            [
                perp_market_config for perp_market_config in self.perp_market_configs
                if perp_market_config['marketIndex'] == perp_position.market_index
            ][0]
            for perp_position in perp_positions
        ]

        oracle_prices = [
            oracle.agg.price * (Decimal(10) ** oracle.expo)
            for oracle in [
                pyth.PRICE.parse(account.data)
                for account in
                (await self.connection.get_multiple_accounts([perp_market.oracle for perp_market in perp_markets])).value
            ]
        ]

        entries = []

        for perp_position, perp_market, perp_market_config, oracle_price in zip(
            perp_positions,
            perp_markets,
            perp_market_configs,
            oracle_prices
        ):
            size = PerpPositionHelper.base_position_ui(perp_position, perp_market)

            unsettled_pnl = PerpPositionHelper.unsettled_pnl(perp_position, perp_market, oracle_price)

            entry_price = PerpPositionHelper.average_entry_price(perp_position, perp_market)

            pnl = PerpPositionHelper.cumulative_pnl_over_position_lifetime(perp_position, perp_market, oracle_price)

            entries.append(
                (
                    perp_market_config['name'],
                    {
                        'size': size,
                        'notional': float(Decimal(size) *  oracle_price),
                        'entry_price': float(entry_price),
                        'oracle_price': float(oracle_price),
                        'unsettled_pnl': float(unsettled_pnl),
                        'pnl': float(pnl)
                    }
                )
            )

        return dict(entries)

    async def orders(self, mango_account: MangoAccount):
        pass