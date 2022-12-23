from __future__ import annotations
from . import (
    i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class PricesJSON(typing.TypedDict):
    oracle: i80f48.I80F48JSON
    stable: i80f48.I80F48JSON


@dataclass
class Prices:
    layout: typing.ClassVar = borsh.CStruct(
        "oracle" / i80f48.I80F48.layout, "stable" / i80f48.I80F48.layout
    )
    oracle: i80f48.I80F48
    stable: i80f48.I80F48

    @classmethod
    def from_decoded(cls, obj: Container) -> "Prices":
        return cls(
            oracle=i80f48.I80F48.from_decoded(obj.oracle),
            stable=i80f48.I80F48.from_decoded(obj.stable),
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "oracle": self.oracle.to_encodable(),
            "stable": self.stable.to_encodable(),
        }

    def to_json(self) -> PricesJSON:
        return {"oracle": self.oracle.to_json(), "stable": self.stable.to_json()}

    @classmethod
    def from_json(cls, obj: PricesJSON) -> "Prices":
        return cls(
            oracle=i80f48.I80F48.from_json(obj["oracle"]),
            stable=i80f48.I80F48.from_json(obj["stable"]),
        )
