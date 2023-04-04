from mango_explorer_v4.types.i80f48 import I80F48
from decimal import Decimal

# TODO: This can be appended to the cla
def parse(i80f48: I80F48) -> float:
    return float(Decimal(i80f48.val) / Decimal(2 ** 48))
