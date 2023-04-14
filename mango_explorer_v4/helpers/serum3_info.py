from mango_explorer_v4.types.health_type import HealthTypeKind
from mango_explorer_v4.types.token_info import TokenInfo
from mango_explorer_v4.types.i80f48 import I80F48
from mango_explorer_v4.types.serum3_info import Serum3Info
from mango_explorer_v4.helpers.token_info import TokenInfoHelper
from mango_explorer_v4.helpers.prices import PricesHelper
from mango_explorer_v4.constructs.serum3_reserved import Serum3Reserved
from decimal import Decimal

class Serum3InfoHelper:
    @staticmethod
    def health_contribution(
        serum3_info: Serum3Info,
        health_type: HealthTypeKind,
        token_infos: [TokenInfo],
        token_max_reserved: [I80F48],
        market_reserved: Serum3Reserved
    ) -> I80F48:
        if any([
            market_reserved.all_reserved_as_base == 0,
            market_reserved.all_reserved_as_quote == 0
        ]):
            return I80F48.from_decimal(Decimal(0))

        base_info, quote_info = token_infos[serum3_info.base_index], token_infos[serum3_info.quote_index]

        base_max_reserved, quote_max_reserved = token_max_reserved[serum3_info.base_index], token_max_reserved[serum3_info.quote_index]

        # How much would the health increase if the reserved balance were applied to the passed token info?
        def get_health_effect(token_info: TokenInfo, token_max_reserved: I80F48, market_reserved: I80F48) -> I80F48:
            # This balance includes all possible reserved funds from markets that relate to the
            # token, including this market itself: `tokenMaxReserved` is already included in `maxBalance`.
            max_balance = token_info.balance_native.to_decimal() + token_max_reserved.to_decimal()

            # Assuming `reserved` was added to `max_balance` last (because that gives the smallest
            # health effects): how much did health change because of it?

            if max_balance > market_reserved.to_decimal():
                asset_part, liab_part = market_reserved, 0
            elif max_balance < 0:
                asset_part, liab_part = 0, market_reserved
            else:
                asset_part, liab_part = max_balance, market_reserved.to_decimal() - max_balance

            if health_type is None:
                return I80F48.from_decimal(asset_part * token_info.prices.oracle.to_decimal() + liab_part * token_info.prices.oracle.to_decimal())

            asset_weight, liab_weight, asset_price, liab_price = [
                TokenInfoHelper.asset_weight(token_info, health_type),
                TokenInfoHelper.liab_weight(token_info, health_type),
                PricesHelper.asset(token_info.prices, health_type),
                PricesHelper.liab(token_info.prices, health_type)
            ]

            return I80F48.from_decimal(asset_weight * asset_part * asset_price + liab_weight * liab_part * liab_price)

        health_base = get_health_effect(base_info, base_max_reserved, I80F48.from_decimal(market_reserved.all_reserved_as_base))

        health_quote = get_health_effect(quote_info, quote_max_reserved, I80F48.from_decimal(market_reserved.all_reserved_as_quote))

        return I80F48.from_decimal(min(health_base.to_decimal(), health_quote.to_decimal()))


