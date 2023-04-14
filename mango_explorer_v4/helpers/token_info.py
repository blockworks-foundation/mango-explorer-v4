from decimal import Decimal
from mango_explorer_v4.types.token_info import TokenInfo
from mango_explorer_v4.types.health_type import HealthTypeKind, Init, Maint, LiquidationEnd
from mango_explorer_v4.helpers.prices import PricesHelper


class TokenInfoHelper():
    @staticmethod
    def liab_weight(token_info: TokenInfo, health_type: HealthTypeKind) -> Decimal:
        return {
            Init: token_info.init_scaled_liab_weight.to_decimal(),
            Maint: token_info.maint_liab_weight.to_decimal(),
            LiquidationEnd: token_info.init_scaled_liab_weight.to_decimal()
        }[type(health_type)]

    @staticmethod
    def asset_weight(token_info: TokenInfo, health_type: HealthTypeKind) -> Decimal:
        return {
            Init: token_info.init_scaled_asset_weight.to_decimal(),
            Maint: token_info.maint_asset_weight.to_decimal(),
            LiquidationEnd: token_info.init_asset_weight.to_decimal()
        }[type(health_type)]

    @staticmethod
    def health_contribution(token_info: TokenInfo, health_type: HealthTypeKind):
        print(type(health_type), type(health_type) == Init, type(health_type))

        if health_type is None:
            return token_info.balance_native.to_decimal() * token_info.prices.oracle.to_decimal()

        if token_info.balance_native.to_decimal() < 0:
            weight, price = TokenInfoHelper.liab_weight(token_info, health_type), PricesHelper.liab(token_info.prices, health_type)
        else:
            weight, price = TokenInfoHelper.asset_weight(token_info, health_type), PricesHelper.asset(token_info.prices, health_type)

        return token_info.balance_native.to_decimal() * weight * price
