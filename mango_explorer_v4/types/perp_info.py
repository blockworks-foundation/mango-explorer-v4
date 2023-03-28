from __future__ import annotations
from . import (
    prices,
    i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class PerpInfoJSON(typing.TypedDict):
    perp_market_index: int
    maint_base_asset_weight: i80f48.I80F48JSON
    init_base_asset_weight: i80f48.I80F48JSON
    maint_base_liab_weight: i80f48.I80F48JSON
    init_base_liab_weight: i80f48.I80F48JSON
    maint_overall_asset_weight: i80f48.I80F48JSON
    init_overall_asset_weight: i80f48.I80F48JSON
    base_lot_size: int
    base_lots: int
    bids_base_lots: int
    asks_base_lots: int
    quote: i80f48.I80F48JSON
    prices: prices.PricesJSON
    has_open_orders: bool
    has_open_fills: bool


@dataclass
class PerpInfo:
    layout: typing.ClassVar = borsh.CStruct(
        "perp_market_index" / borsh.U16,
        "maint_base_asset_weight" / i80f48.I80F48.layout,
        "init_base_asset_weight" / i80f48.I80F48.layout,
        "maint_base_liab_weight" / i80f48.I80F48.layout,
        "init_base_liab_weight" / i80f48.I80F48.layout,
        "maint_overall_asset_weight" / i80f48.I80F48.layout,
        "init_overall_asset_weight" / i80f48.I80F48.layout,
        "base_lot_size" / borsh.I64,
        "base_lots" / borsh.I64,
        "bids_base_lots" / borsh.I64,
        "asks_base_lots" / borsh.I64,
        "quote" / i80f48.I80F48.layout,
        "prices" / prices.Prices.layout,
        "has_open_orders" / borsh.Bool,
        "has_open_fills" / borsh.Bool,
    )
    perp_market_index: int
    maint_base_asset_weight: i80f48.I80F48
    init_base_asset_weight: i80f48.I80F48
    maint_base_liab_weight: i80f48.I80F48
    init_base_liab_weight: i80f48.I80F48
    maint_overall_asset_weight: i80f48.I80F48
    init_overall_asset_weight: i80f48.I80F48
    base_lot_size: int
    base_lots: int
    bids_base_lots: int
    asks_base_lots: int
    quote: i80f48.I80F48
    prices: prices.Prices
    has_open_orders: bool
    has_open_fills: bool

    @classmethod
    def from_decoded(cls, obj: Container) -> "PerpInfo":
        return cls(
            perp_market_index=obj.perp_market_index,
            maint_base_asset_weight=i80f48.I80F48.from_decoded(
                obj.maint_base_asset_weight
            ),
            init_base_asset_weight=i80f48.I80F48.from_decoded(
                obj.init_base_asset_weight
            ),
            maint_base_liab_weight=i80f48.I80F48.from_decoded(
                obj.maint_base_liab_weight
            ),
            init_base_liab_weight=i80f48.I80F48.from_decoded(obj.init_base_liab_weight),
            maint_overall_asset_weight=i80f48.I80F48.from_decoded(
                obj.maint_overall_asset_weight
            ),
            init_overall_asset_weight=i80f48.I80F48.from_decoded(
                obj.init_overall_asset_weight
            ),
            base_lot_size=obj.base_lot_size,
            base_lots=obj.base_lots,
            bids_base_lots=obj.bids_base_lots,
            asks_base_lots=obj.asks_base_lots,
            quote=i80f48.I80F48.from_decoded(obj.quote),
            prices=prices.Prices.from_decoded(obj.prices),
            has_open_orders=obj.has_open_orders,
            has_open_fills=obj.has_open_fills,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "perp_market_index": self.perp_market_index,
            "maint_base_asset_weight": self.maint_base_asset_weight.to_encodable(),
            "init_base_asset_weight": self.init_base_asset_weight.to_encodable(),
            "maint_base_liab_weight": self.maint_base_liab_weight.to_encodable(),
            "init_base_liab_weight": self.init_base_liab_weight.to_encodable(),
            "maint_overall_asset_weight": self.maint_overall_asset_weight.to_encodable(),
            "init_overall_asset_weight": self.init_overall_asset_weight.to_encodable(),
            "base_lot_size": self.base_lot_size,
            "base_lots": self.base_lots,
            "bids_base_lots": self.bids_base_lots,
            "asks_base_lots": self.asks_base_lots,
            "quote": self.quote.to_encodable(),
            "prices": self.prices.to_encodable(),
            "has_open_orders": self.has_open_orders,
            "has_open_fills": self.has_open_fills,
        }

    def to_json(self) -> PerpInfoJSON:
        return {
            "perp_market_index": self.perp_market_index,
            "maint_base_asset_weight": self.maint_base_asset_weight.to_json(),
            "init_base_asset_weight": self.init_base_asset_weight.to_json(),
            "maint_base_liab_weight": self.maint_base_liab_weight.to_json(),
            "init_base_liab_weight": self.init_base_liab_weight.to_json(),
            "maint_overall_asset_weight": self.maint_overall_asset_weight.to_json(),
            "init_overall_asset_weight": self.init_overall_asset_weight.to_json(),
            "base_lot_size": self.base_lot_size,
            "base_lots": self.base_lots,
            "bids_base_lots": self.bids_base_lots,
            "asks_base_lots": self.asks_base_lots,
            "quote": self.quote.to_json(),
            "prices": self.prices.to_json(),
            "has_open_orders": self.has_open_orders,
            "has_open_fills": self.has_open_fills,
        }

    @classmethod
    def from_json(cls, obj: PerpInfoJSON) -> "PerpInfo":
        return cls(
            perp_market_index=obj["perp_market_index"],
            maint_base_asset_weight=i80f48.I80F48.from_json(
                obj["maint_base_asset_weight"]
            ),
            init_base_asset_weight=i80f48.I80F48.from_json(
                obj["init_base_asset_weight"]
            ),
            maint_base_liab_weight=i80f48.I80F48.from_json(
                obj["maint_base_liab_weight"]
            ),
            init_base_liab_weight=i80f48.I80F48.from_json(obj["init_base_liab_weight"]),
            maint_overall_asset_weight=i80f48.I80F48.from_json(
                obj["maint_overall_asset_weight"]
            ),
            init_overall_asset_weight=i80f48.I80F48.from_json(
                obj["init_overall_asset_weight"]
            ),
            base_lot_size=obj["base_lot_size"],
            base_lots=obj["base_lots"],
            bids_base_lots=obj["bids_base_lots"],
            asks_base_lots=obj["asks_base_lots"],
            quote=i80f48.I80F48.from_json(obj["quote"]),
            prices=prices.Prices.from_json(obj["prices"]),
            has_open_orders=obj["has_open_orders"],
            has_open_fills=obj["has_open_fills"],
        )
