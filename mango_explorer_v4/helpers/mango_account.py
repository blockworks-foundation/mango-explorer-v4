from mango_explorer_v4.accounts.mango_account import MangoAccount
from mango_explorer_v4.types.token_position import TokenPosition
from mango_explorer_v4.types.serum3_orders import Serum3Orders
from mango_explorer_v4.types.perp_position import PerpPosition
from mango_explorer_v4.helpers.perp_position import PerpPositionHelper
from mango_explorer_v4.helpers.serum3_orders import Serum3OrdersHelper
from mango_explorer_v4.helpers.token_position import TokenPositionHelper


class MangoAccountHelper:
    @staticmethod
    def active_token_positions(mango_account: MangoAccount) -> [TokenPosition]:
        return [
            token_position for token_position in mango_account.tokens
            if TokenPositionHelper.is_active(token_position)
        ]

    @staticmethod
    def active_serum3_orders(mango_account: MangoAccount) -> [Serum3Orders]:
        return [
            serum3_orders for serum3_orders in mango_account.serum3
            if Serum3OrdersHelper.is_active(serum3_orders)
        ]

    @staticmethod
    def active_perp_positions(mango_account: MangoAccount) -> [PerpPosition]:
        return [
            perp_position for perp_position in mango_account.perps
            if PerpPositionHelper.is_active(perp_position)
        ]
