import sys
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Any

from solana.publickey import PublicKey

from mango_explorer_v4.accounts.perp_market import PerpMarket
from mango_explorer_v4.constants import RUST_U64_MAX
from mango_explorer_v4.accounts.book_side import BookSide
from mango_explorer_v4.types.order_tree_root import OrderTreeRoot
from mango_explorer_v4.types.leaf_node import LeafNode
from mango_explorer_v4.types.inner_node import InnerNode


@dataclass
class PerpOrder:
    seq_num: int
    order_id: int
    owner: PublicKey
    open_orders_slot: int
    fee_tier: 0
    ui_price: float
    price: int
    ui_size: float
    size: int
    side: Literal['bids', 'asks']
    timestamp: int
    expiry_timestamp: int
    perp_market_index: int
    is_expired: bool
    is_oracle_pegged: bool
    oracle_pegged_properties: Any

    @staticmethod
    def build(
            perp_market: PerpMarket,
            leaf_node: LeafNode,
            side: Literal['bids', 'asks'],
            oracle_price: float,
            is_oracle_pegged: bool = False
    ):
        if is_oracle_pegged:
            price_data = leaf_node.key >> 64

            price_offset = price_data - (1 << 63)

            price_lots = perp_market.ui_price_to_lots(oracle_price) + price_offset

            is_invalid = {
                'bids': price_lots > leaf_node.peg_limit,
                'asks': leaf_node.peg_limit > price_lots
            }[side]

            oracle_pegged_properties = {
                'is_invalid': is_invalid,
                'price_offset': price_offset,
                'ui_price_offset': perp_market.price_lots_to_ui(price_offset),
                'peg_limit': leaf_node.peg_limit,
                'ui_peg_limit': perp_market.price_lots_to_ui(leaf_node.peg_limit),
            }
        else:
            price_lots = leaf_node.key >> 64

            oracle_pegged_properties = None

        now = int(time.time())

        expiry_timestamp = leaf_node.timestamp + leaf_node.time_in_force if leaf_node.time_in_force else sys.maxsize

        is_expired = now > expiry_timestamp

        return PerpOrder(
            {
                'bids': RUST_U64_MAX - (leaf_node.key & ((1 << 64) - 1)),
                'asks': leaf_node.key & ((1 << 64) - 1)
            }[side],
            leaf_node.key,
            leaf_node.owner,
            leaf_node.owner_slot,
            0,
            float(Decimal(price_lots) * Decimal(perp_market.price_lots_to_ui_converter)),
            price_lots,
            float(Decimal(leaf_node.quantity) * Decimal(perp_market.base_lots_to_ui_converter)),
            leaf_node.quantity,
            side,
            leaf_node.timestamp,
            expiry_timestamp,
            perp_market.perp_market_index,
            is_expired,
            is_oracle_pegged,
            oracle_pegged_properties
        )


def items(book_side: BookSide, perp_market: PerpMarket, side: Literal['bids', 'asks'], oracle_price: float):
    def entries(order_tree_root: OrderTreeRoot, is_oracle_pegged: bool):
        if order_tree_root.leaf_count == 0:
            return

        stack = [order_tree_root.maybe_node]

        [left, right] = [1, 0] if side == 'bids' else [0, 1]

        while len(stack) > 0:
            index = stack.pop()

            node = book_side.nodes.nodes[index]

            match node.tag:
                case 1:
                    inner_node = InnerNode.layout.parse(bytes([1] + node.data))

                    stack.extend([inner_node.children[right], inner_node.children[left]])
                case 2:
                    leaf_node: LeafNode = LeafNode.layout.parse(bytes([2] + node.data))

                    yield PerpOrder.build(
                        perp_market,
                        leaf_node,
                        side,
                        oracle_price,
                        is_oracle_pegged
                    )

    fixed_items = entries(book_side.roots[0], False)

    oracle_pegged_items = entries(book_side.roots[1], True)

    def is_better(side: Literal['bids', 'asks'], a: PerpOrder, b: PerpOrder):
        # TODO: This can be comparison operators instead
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
            if is_better(side, fixed_item, oracle_pegged_item):
                yield fixed_item; fixed_item = next(fixed_items, None)
            else:
                yield oracle_pegged_item; oracle_pegged_item = next(oracle_pegged_items, None)
        elif fixed_item and not oracle_pegged_item:
            yield fixed_item; fixed_item = next(fixed_items, None)
        elif not fixed_item and oracle_pegged_item:
            yield oracle_pegged_item; oracle_pegged_item = next(oracle_pegged_items, None)
