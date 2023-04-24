from mango_explorer_v4.types.perp_open_order import PerpOpenOrder

class PerpOpenOrderHelper:
    @staticmethod
    def is_active(perp_open_order: PerpOpenOrder):
        return perp_open_order.market != 65535
