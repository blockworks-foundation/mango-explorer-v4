from __future__ import annotations
from . import (
    i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
from solana.publickey import PublicKey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class FillEventJSON(typing.TypedDict):
    event_type: int
    taker_side: int
    maker_out: int
    maker_slot: int
    padding: list[int]
    timestamp: int
    seq_num: int
    maker: str
    maker_order_id: int
    maker_fee: i80f48.I80F48JSON
    maker_timestamp: int
    taker: str
    taker_order_id: int
    taker_client_order_id: int
    taker_fee: i80f48.I80F48JSON
    price: int
    quantity: int
    reserved: list[int]


@dataclass
class FillEvent:
    layout: typing.ClassVar = borsh.CStruct(
        "event_type" / borsh.U8,
        "taker_side" / borsh.U8,
        "maker_out" / borsh.U8,
        "maker_slot" / borsh.U8,
        "padding" / borsh.U8[4],
        "timestamp" / borsh.U64,
        "seq_num" / borsh.U64,
        "maker" / BorshPubkey,
        "maker_order_id" / borsh.U128,
        "maker_fee" / i80f48.I80F48.layout,
        "maker_timestamp" / borsh.U64,
        "taker" / BorshPubkey,
        "taker_order_id" / borsh.U128,
        "taker_client_order_id" / borsh.U64,
        "taker_fee" / i80f48.I80F48.layout,
        "price" / borsh.I64,
        "quantity" / borsh.I64,
        "reserved" / borsh.U8[24],
    )
    event_type: int
    taker_side: int
    maker_out: int
    maker_slot: int
    padding: list[int]
    timestamp: int
    seq_num: int
    maker: PublicKey
    maker_order_id: int
    maker_fee: i80f48.I80F48
    maker_timestamp: int
    taker: PublicKey
    taker_order_id: int
    taker_client_order_id: int
    taker_fee: i80f48.I80F48
    price: int
    quantity: int
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "FillEvent":
        return cls(
            event_type=obj.event_type,
            taker_side=obj.taker_side,
            maker_out=obj.maker_out,
            maker_slot=obj.maker_slot,
            padding=obj.padding,
            timestamp=obj.timestamp,
            seq_num=obj.seq_num,
            maker=obj.maker,
            maker_order_id=obj.maker_order_id,
            maker_fee=i80f48.I80F48.from_decoded(obj.maker_fee),
            maker_timestamp=obj.maker_timestamp,
            taker=obj.taker,
            taker_order_id=obj.taker_order_id,
            taker_client_order_id=obj.taker_client_order_id,
            taker_fee=i80f48.I80F48.from_decoded(obj.taker_fee),
            price=obj.price,
            quantity=obj.quantity,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "event_type": self.event_type,
            "taker_side": self.taker_side,
            "maker_out": self.maker_out,
            "maker_slot": self.maker_slot,
            "padding": self.padding,
            "timestamp": self.timestamp,
            "seq_num": self.seq_num,
            "maker": self.maker,
            "maker_order_id": self.maker_order_id,
            "maker_fee": self.maker_fee.to_encodable(),
            "maker_timestamp": self.maker_timestamp,
            "taker": self.taker,
            "taker_order_id": self.taker_order_id,
            "taker_client_order_id": self.taker_client_order_id,
            "taker_fee": self.taker_fee.to_encodable(),
            "price": self.price,
            "quantity": self.quantity,
            "reserved": self.reserved,
        }

    def to_json(self) -> FillEventJSON:
        return {
            "event_type": self.event_type,
            "taker_side": self.taker_side,
            "maker_out": self.maker_out,
            "maker_slot": self.maker_slot,
            "padding": self.padding,
            "timestamp": self.timestamp,
            "seq_num": self.seq_num,
            "maker": str(self.maker),
            "maker_order_id": self.maker_order_id,
            "maker_fee": self.maker_fee.to_json(),
            "maker_timestamp": self.maker_timestamp,
            "taker": str(self.taker),
            "taker_order_id": self.taker_order_id,
            "taker_client_order_id": self.taker_client_order_id,
            "taker_fee": self.taker_fee.to_json(),
            "price": self.price,
            "quantity": self.quantity,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: FillEventJSON) -> "FillEvent":
        return cls(
            event_type=obj["event_type"],
            taker_side=obj["taker_side"],
            maker_out=obj["maker_out"],
            maker_slot=obj["maker_slot"],
            padding=obj["padding"],
            timestamp=obj["timestamp"],
            seq_num=obj["seq_num"],
            maker=PublicKey(obj["maker"]),
            maker_order_id=obj["maker_order_id"],
            maker_fee=i80f48.I80F48.from_json(obj["maker_fee"]),
            maker_timestamp=obj["maker_timestamp"],
            taker=PublicKey(obj["taker"]),
            taker_order_id=obj["taker_order_id"],
            taker_client_order_id=obj["taker_client_order_id"],
            taker_fee=i80f48.I80F48.from_json(obj["taker_fee"]),
            price=obj["price"],
            quantity=obj["quantity"],
            reserved=obj["reserved"],
        )
