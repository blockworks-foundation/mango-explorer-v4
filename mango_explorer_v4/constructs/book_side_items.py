import itertools
import sys
import time
import typing
from dataclasses import dataclass
from decimal import Decimal

from solana.publickey import PublicKey

from mango_explorer_v4.accounts.book_side import BookSide
from mango_explorer_v4.accounts.perp_market import PerpMarket
from mango_explorer_v4.constants import RUST_U64_MAX
from mango_explorer_v4.types.inner_node import InnerNode
from mango_explorer_v4.types.leaf_node import LeafNode
from mango_explorer_v4.types.order_tree_root import OrderTreeRoot
from mango_explorer_v4.helpers.perp_market import PerpMarketHelper


@dataclass
class BookSideItem:
    side: typing.Literal['bids', 'asks']
    seq_num: int
    order_id: int
    owner: PublicKey
    price: int
    price_ui: float
    size: int
    size_ui: float
    client_order_id: int
    created_at: int
    expires_at: int
    is_oracle_pegged: bool
    oracle_pegged_properties: typing.Any


@dataclass
class BookSideItems:
    side: typing.Literal['bids', 'asks']
    book_side: BookSide
    perp_market: PerpMarket
    oracle_price: float

    def __iter__(self):
        def entries(order_tree_root: OrderTreeRoot, is_oracle_pegged: bool):
            if order_tree_root.leaf_count == 0:
                return

            stack = [order_tree_root.maybe_node]

            [left, right] = [1, 0] if self.side == 'bids' else [0, 1]

            now = int(time.time())

            while len(stack) > 0:
                index = stack.pop()

                node = self.book_side.nodes.nodes[index]

                match node.tag:
                    case 1:
                        inner_node = InnerNode.layout.parse(bytes([1] + node.data))

                        stack.extend([inner_node.children[right], inner_node.children[left]])
                    case 2:
                        leaf_node: LeafNode = LeafNode.layout.parse(bytes([2] + node.data))

                        if is_oracle_pegged: # TODO: This won't change - no need to evaluate more than once
                            price_offset = (leaf_node.key >> 64) - (1 << 63)

                            price_lots = PerpMarketHelper.ui_price_to_lots(self.perp_market, self.oracle_price) + price_offset

                            is_invalid = {
                                'bids': price_lots > leaf_node.peg_limit,
                                'asks': leaf_node.peg_limit > price_lots
                            }[self.side]

                            oracle_pegged_properties = {
                                'is_invalid': is_invalid,
                                'price_offset': price_offset,
                                'ui_price_offset': PerpMarketHelper.price_lots_to_ui(self.perp_market, price_offset),
                                'peg_limit': leaf_node.peg_limit,
                                'ui_peg_limit': PerpMarketHelper.price_lots_to_ui(self.perp_market, leaf_node.peg_limit)
                            }
                        else:
                            price_lots = leaf_node.key >> 64

                            oracle_pegged_properties = None

                        expiry_timestamp = leaf_node.timestamp + leaf_node.time_in_force if leaf_node.time_in_force else sys.maxsize

                        yield BookSideItem(
                            side=self.side,
                            seq_num={
                                'bids': RUST_U64_MAX - (leaf_node.key & ((1 << 64) - 1)),
                                'asks': leaf_node.key & ((1 << 64) - 1)
                            }[self.side],
                            order_id=leaf_node.key,
                            owner=leaf_node.owner,
                            price=price_lots,
                            price_ui=float(PerpMarketHelper.price_lots_to_ui(self.perp_market, price_lots)),
                            size=leaf_node.quantity,
                            size_ui=float(PerpMarketHelper.base_lots_to_ui(self.perp_market, leaf_node.quantity)),
                            client_order_id=leaf_node.client_order_id,
                            created_at=leaf_node.timestamp,
                            expires_at=expiry_timestamp,
                            is_oracle_pegged=is_oracle_pegged,
                            oracle_pegged_properties=oracle_pegged_properties
                        )

        fixed_items = entries(self.book_side.roots[0], False)

        oracle_pegged_items = entries(self.book_side.roots[1], True)

        def is_better(side: typing.Literal['bids', 'asks'], a: BookSideItem, b: BookSideItem):
            # TODO: This can be comparison operators instead, and can could UI prices instead of native
            if a.price == b.price:
                return a.seq_num < b.seq_num
                # ^ If prices are equal, prefer the oldest created
            else:
                return {
                    'bids': a.price > b.price,
                    'asks': a.price < b.price
                }[side]

        fixed_item = next(fixed_items, None)

        oracle_pegged_item = next(oracle_pegged_items, None)

        while fixed_item or oracle_pegged_item:
            if fixed_item and oracle_pegged_item:
                if is_better(self.side, fixed_item, oracle_pegged_item):
                    yield fixed_item; fixed_item = next(fixed_items, None)
                else:
                    yield oracle_pegged_item; oracle_pegged_item = next(oracle_pegged_items, None)
            elif fixed_item and not oracle_pegged_item:
                yield fixed_item; fixed_item = next(fixed_items, None)
            elif not fixed_item and oracle_pegged_item:
                yield oracle_pegged_item; oracle_pegged_item = next(oracle_pegged_items, None)

    def l2(self):
        orders = []

        for key, groups in itertools.groupby([[order.price_ui, order.size_ui] for order in self], lambda order: order[0]):
            orders.append([key, float(sum([Decimal(str(size)) for price, size in groups]))])

        return orders

    def l3(self):
        return [
            {
                'price': order.price_ui,
                'size': order.size_ui,
                'mango_account': order.owner,
                'client_order_id': order.client_order_id
            }
            for order in self
        ]

    def impact_price(self, impact_quantity: float):
        accum = 0

        for price, size in self.l2():
            accum += size

            if size >= impact_quantity:
                return price

        return None
