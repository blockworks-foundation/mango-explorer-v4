from mango_explorer_v4.types.perp_info import PerpInfo
from mango_explorer_v4.types.health_type import HealthTypeKind, Init, LiquidationEnd
from mango_explorer_v4.types.i80f48 import I80F48
from mango_explorer_v4.helpers.prices import PricesHelper
from decimal import Decimal

class PerpInfoHelper:
    @staticmethod
    def unweighted_health_contribution(perp_info: PerpInfo, health_type: HealthTypeKind) -> I80F48:
        def order_execution_case(perp_info: PerpInfo, orders_base_lots: Decimal, order_price: I80F48) -> I80F48:
            net_base_native = perp_info.base_lots + orders_base_lots * perp_info.base_lot_size

            if health_type in [Init(), LiquidationEnd()]:
                if net_base_native < 0:
                    weight = perp_info.init_base_liab_weight
                else:
                    weight = perp_info.init_base_asset_weight
            else:
                if net_base_native < 0:
                    weight = perp_info.maint_base_liab_weight
                else:
                    weight = perp_info.maint_base_asset_weight

            if net_base_native < 0:
                base_price = PricesHelper.liab(perp_info.prices, health_type)
            else:
                base_price = PricesHelper.asset(perp_info.prices, health_type)

            # Total value of the order-execution adjusted base position
            base_health = net_base_native * weight.to_decimal() * base_price

            orders_base_native = orders_base_lots * perp_info.base_lot_size

            order_quote = orders_base_native * -1 * order_price.to_decimal()

            return I80F48.from_decimal(base_health + order_quote)

        bids_case = order_execution_case(
            perp_info,
            Decimal(perp_info.bids_base_lots),
            I80F48.from_decimal(PricesHelper.liab(perp_info.prices, health_type))
        ).to_decimal()

        asks_case = order_execution_case(
            perp_info,
            Decimal(perp_info.bids_base_lots) * -1,
            I80F48.from_decimal(PricesHelper.asset(perp_info.prices, health_type))
        ).to_decimal()

        worst_case = min(bids_case, asks_case)

        return I80F48.from_decimal(perp_info.quote.to_decimal() + worst_case)

    @staticmethod
    def health_contribution(perp_info: PerpInfo, health_type: HealthTypeKind) -> I80F48:
        contrib = PerpInfoHelper.unweighted_health_contribution(perp_info, health_type).to_decimal()

        if contrib > 0:
            asset_weight = (perp_info.init_overall_asset_weight if health_type in [Init(), LiquidationEnd()] else perp_info.maint_overall_asset_weight).to_decimal()

            return I80F48.from_decimal(asset_weight * contrib)

        return I80F48.from_decimal(contrib)
