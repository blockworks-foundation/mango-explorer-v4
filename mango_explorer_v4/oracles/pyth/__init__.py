import typing
from decimal import Decimal

import construct
from solana.publickey import PublicKey


class PublicKeyAdapter(construct.Adapter):
    def __init__(self) -> None:
        super().__init__(construct.Bytes(32))

    def _decode(self, obj: bytes, context: typing.Any, path: typing.Any) -> typing.Optional[PublicKey]:
        if (obj is None) or (obj == bytes([0] * 32)):
            return None
        return PublicKey(obj)

    def _encode(self, obj: PublicKey, context: typing.Any, path: typing.Any) -> bytes:
        return bytes(obj)


class DecimalAdapter(construct.Adapter):
    def __init__(self, size: int = 8) -> None:
        super().__init__(construct.BytesInteger(size, swapped=True))

    def _decode(self, obj: int, context: typing.Any, path: typing.Any) -> Decimal:
        return Decimal(obj)

    def _encode(self, obj: Decimal, context: typing.Any, path: typing.Any) -> int:
        # Can only encode Decimal values.
        return int(obj)


PRICE_INFO = construct.Struct(
    "price" / DecimalAdapter(),
    "conf" / DecimalAdapter(),
    "status" / construct.Enum(construct.Int32ul, Unknown=0, Trading=1, Halted=2, Auction=3),
    "corp_act" / construct.Enum(construct.Int32ul, NoCorpAct=0),
    "pub_slot" / DecimalAdapter(),
)

ACCOUNT_TYPE = construct.Enum(
    construct.Int32ul, Unknown=0, Mapping=1, Product=2, Price=3
)

PRICE_COMP = construct.Struct(
    "publisher" / PublicKeyAdapter(), "agg" / PRICE_INFO, "latest" / PRICE_INFO
)

PRICE = construct.Struct(
    "magic" / DecimalAdapter(4),
    "ver" / DecimalAdapter(4),
    "atype" / ACCOUNT_TYPE,
    "size" / DecimalAdapter(4),
    "ptype" / construct.Enum(construct.Int32ul, Unknown=0, Price=1),
    "expo" / construct.Int32sl,
    "num" / DecimalAdapter(4),
    "unused" / DecimalAdapter(4),
    "curr_slot" / DecimalAdapter(),
    "valid_slot" / DecimalAdapter(),
    "drv" / construct.Array(8, construct.Int64sl),
    "prod" / PublicKeyAdapter(),
    "next" / PublicKeyAdapter(),
    "agg_pub" / PublicKeyAdapter(),
    "agg" / PRICE_INFO,
    "comp" / construct.Array(32, PRICE_COMP),
)
