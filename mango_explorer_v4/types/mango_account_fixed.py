from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solana.publickey import PublicKey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class MangoAccountFixedJSON(typing.TypedDict):
    group: str
    owner: str
    name: list[int]
    delegate: str
    account_num: int
    being_liquidated: int
    in_health_region: int
    bump: int
    padding: list[int]
    net_deposits: int
    perp_spot_transfers: int
    health_region_begin_init_health: int
    reserved: list[int]


@dataclass
class MangoAccountFixed:
    layout: typing.ClassVar = borsh.CStruct(
        "group" / BorshPubkey,
        "owner" / BorshPubkey,
        "name" / borsh.U8[32],
        "delegate" / BorshPubkey,
        "account_num" / borsh.U32,
        "being_liquidated" / borsh.U8,
        "in_health_region" / borsh.U8,
        "bump" / borsh.U8,
        "padding" / borsh.U8[1],
        "net_deposits" / borsh.I64,
        "perp_spot_transfers" / borsh.I64,
        "health_region_begin_init_health" / borsh.I64,
        "reserved" / borsh.U8[240],
    )
    group: PublicKey
    owner: PublicKey
    name: list[int]
    delegate: PublicKey
    account_num: int
    being_liquidated: int
    in_health_region: int
    bump: int
    padding: list[int]
    net_deposits: int
    perp_spot_transfers: int
    health_region_begin_init_health: int
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "MangoAccountFixed":
        return cls(
            group=obj.group,
            owner=obj.owner,
            name=obj.name,
            delegate=obj.delegate,
            account_num=obj.account_num,
            being_liquidated=obj.being_liquidated,
            in_health_region=obj.in_health_region,
            bump=obj.bump,
            padding=obj.padding,
            net_deposits=obj.net_deposits,
            perp_spot_transfers=obj.perp_spot_transfers,
            health_region_begin_init_health=obj.health_region_begin_init_health,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "group": self.group,
            "owner": self.owner,
            "name": self.name,
            "delegate": self.delegate,
            "account_num": self.account_num,
            "being_liquidated": self.being_liquidated,
            "in_health_region": self.in_health_region,
            "bump": self.bump,
            "padding": self.padding,
            "net_deposits": self.net_deposits,
            "perp_spot_transfers": self.perp_spot_transfers,
            "health_region_begin_init_health": self.health_region_begin_init_health,
            "reserved": self.reserved,
        }

    def to_json(self) -> MangoAccountFixedJSON:
        return {
            "group": str(self.group),
            "owner": str(self.owner),
            "name": self.name,
            "delegate": str(self.delegate),
            "account_num": self.account_num,
            "being_liquidated": self.being_liquidated,
            "in_health_region": self.in_health_region,
            "bump": self.bump,
            "padding": self.padding,
            "net_deposits": self.net_deposits,
            "perp_spot_transfers": self.perp_spot_transfers,
            "health_region_begin_init_health": self.health_region_begin_init_health,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: MangoAccountFixedJSON) -> "MangoAccountFixed":
        return cls(
            group=PublicKey(obj["group"]),
            owner=PublicKey(obj["owner"]),
            name=obj["name"],
            delegate=PublicKey(obj["delegate"]),
            account_num=obj["account_num"],
            being_liquidated=obj["being_liquidated"],
            in_health_region=obj["in_health_region"],
            bump=obj["bump"],
            padding=obj["padding"],
            net_deposits=obj["net_deposits"],
            perp_spot_transfers=obj["perp_spot_transfers"],
            health_region_begin_init_health=obj["health_region_begin_init_health"],
            reserved=obj["reserved"],
        )
