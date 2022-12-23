from __future__ import annotations
from . import (
    prices,
    i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class TokenInfoJSON(typing.TypedDict):
    token_index: int
    maint_asset_weight: i80f48.I80F48JSON
    init_asset_weight: i80f48.I80F48JSON
    maint_liab_weight: i80f48.I80F48JSON
    init_liab_weight: i80f48.I80F48JSON
    prices: prices.PricesJSON
    balance_native: i80f48.I80F48JSON


@dataclass
class TokenInfo:
    layout: typing.ClassVar = borsh.CStruct(
        "token_index" / borsh.U16,
        "maint_asset_weight" / i80f48.I80F48.layout,
        "init_asset_weight" / i80f48.I80F48.layout,
        "maint_liab_weight" / i80f48.I80F48.layout,
        "init_liab_weight" / i80f48.I80F48.layout,
        "prices" / prices.Prices.layout,
        "balance_native" / i80f48.I80F48.layout,
    )
    token_index: int
    maint_asset_weight: i80f48.I80F48
    init_asset_weight: i80f48.I80F48
    maint_liab_weight: i80f48.I80F48
    init_liab_weight: i80f48.I80F48
    prices: prices.Prices
    balance_native: i80f48.I80F48

    @classmethod
    def from_decoded(cls, obj: Container) -> "TokenInfo":
        return cls(
            token_index=obj.token_index,
            maint_asset_weight=i80f48.I80F48.from_decoded(obj.maint_asset_weight),
            init_asset_weight=i80f48.I80F48.from_decoded(obj.init_asset_weight),
            maint_liab_weight=i80f48.I80F48.from_decoded(obj.maint_liab_weight),
            init_liab_weight=i80f48.I80F48.from_decoded(obj.init_liab_weight),
            prices=prices.Prices.from_decoded(obj.prices),
            balance_native=i80f48.I80F48.from_decoded(obj.balance_native),
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "token_index": self.token_index,
            "maint_asset_weight": self.maint_asset_weight.to_encodable(),
            "init_asset_weight": self.init_asset_weight.to_encodable(),
            "maint_liab_weight": self.maint_liab_weight.to_encodable(),
            "init_liab_weight": self.init_liab_weight.to_encodable(),
            "prices": self.prices.to_encodable(),
            "balance_native": self.balance_native.to_encodable(),
        }

    def to_json(self) -> TokenInfoJSON:
        return {
            "token_index": self.token_index,
            "maint_asset_weight": self.maint_asset_weight.to_json(),
            "init_asset_weight": self.init_asset_weight.to_json(),
            "maint_liab_weight": self.maint_liab_weight.to_json(),
            "init_liab_weight": self.init_liab_weight.to_json(),
            "prices": self.prices.to_json(),
            "balance_native": self.balance_native.to_json(),
        }

    @classmethod
    def from_json(cls, obj: TokenInfoJSON) -> "TokenInfo":
        return cls(
            token_index=obj["token_index"],
            maint_asset_weight=i80f48.I80F48.from_json(obj["maint_asset_weight"]),
            init_asset_weight=i80f48.I80F48.from_json(obj["init_asset_weight"]),
            maint_liab_weight=i80f48.I80F48.from_json(obj["maint_liab_weight"]),
            init_liab_weight=i80f48.I80F48.from_json(obj["init_liab_weight"]),
            prices=prices.Prices.from_json(obj["prices"]),
            balance_native=i80f48.I80F48.from_json(obj["balance_native"]),
        )
