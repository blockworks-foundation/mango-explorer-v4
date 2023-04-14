from decimal import Decimal
from dataclasses import dataclass

@dataclass
class Serum3Reserved():
    all_reserved_as_base: Decimal
    all_reserved_as_quote: Decimal
