from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh
import decimal
import math


class I80F48JSON(typing.TypedDict):
    val: int


@dataclass
class I80F48:
    layout: typing.ClassVar = borsh.CStruct("val" / borsh.I128)
    val: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "I80F48":
        return cls(val=obj.val)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"val": self.val}

    def to_json(self) -> I80F48JSON:
        return {"val": self.val}

    @classmethod
    def from_json(cls, obj: I80F48JSON) -> "I80F48":
        return cls(val=obj["val"])

    def to_decimal(self) -> decimal.Decimal:
        return decimal.Decimal(self.val) / decimal.Decimal(2 ** 48)

    @classmethod
    def from_decimal(cls, val: decimal.Decimal) -> "I80F48":
        return cls(val=int(decimal.Decimal(val) * decimal.Decimal(2 ** 48)))
