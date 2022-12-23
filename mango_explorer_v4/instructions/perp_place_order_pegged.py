from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import MANGO_PROGRAM_ID


class PerpPlaceOrderPeggedArgs(typing.TypedDict):
    side: types.side.SideKind
    price_offset_lots: int
    peg_limit: int
    max_base_lots: int
    max_quote_lots: int
    client_order_id: int
    order_type: types.place_order_type.PlaceOrderTypeKind
    reduce_only: bool
    expiry_timestamp: int
    limit: int
    max_oracle_staleness_slots: int


layout = borsh.CStruct(
    "side" / types.side.layout,
    "price_offset_lots" / borsh.I64,
    "peg_limit" / borsh.I64,
    "max_base_lots" / borsh.I64,
    "max_quote_lots" / borsh.I64,
    "client_order_id" / borsh.U64,
    "order_type" / types.place_order_type.layout,
    "reduce_only" / borsh.Bool,
    "expiry_timestamp" / borsh.U64,
    "limit" / borsh.U8,
    "max_oracle_staleness_slots" / borsh.I32,
)


class PerpPlaceOrderPeggedAccounts(typing.TypedDict):
    group: PublicKey
    account: PublicKey
    owner: PublicKey
    perp_market: PublicKey
    bids: PublicKey
    asks: PublicKey
    event_queue: PublicKey
    oracle: PublicKey


def perp_place_order_pegged(
    args: PerpPlaceOrderPeggedArgs,
    accounts: PerpPlaceOrderPeggedAccounts,
    program_id: PublicKey = MANGO_PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["perp_market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["bids"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["asks"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["event_queue"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["oracle"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xc0<\x99\xa2\xf6\xc82W"
    encoded_args = layout.build(
        {
            "side": args["side"].to_encodable(),
            "price_offset_lots": args["price_offset_lots"],
            "peg_limit": args["peg_limit"],
            "max_base_lots": args["max_base_lots"],
            "max_quote_lots": args["max_quote_lots"],
            "client_order_id": args["client_order_id"],
            "order_type": args["order_type"].to_encodable(),
            "reduce_only": args["reduce_only"],
            "expiry_timestamp": args["expiry_timestamp"],
            "limit": args["limit"],
            "max_oracle_staleness_slots": args["max_oracle_staleness_slots"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
