from mango_explorer_v4.types.perp_info import PerpInfo
from mango_explorer_v4.types.health_type import HealthTypeKind, Init, LiquidationEnd
from mango_explorer_v4.types.i80f48 import I80F48
from decimal import Decimal

class PerpInfoHelper:
    @staticmethod
    def unweighted_health_contribution(perp_info: PerpInfo, health_type: HealthTypeKind) -> I80F48:
        def order_execution_case(perp_info: PerpInfo, orders_base_lots: Decimal, order_price: I80F48) -> I80F48:
            net_base_native = perp_info.base_lots + orders_base_lots * perp_info.base_lot_size

            weight, base_price = None, None

    @staticmethod
    def health_contribution(perp_info: PerpInfo, health_type: HealthTypeKind) -> I80F48:
        pass
