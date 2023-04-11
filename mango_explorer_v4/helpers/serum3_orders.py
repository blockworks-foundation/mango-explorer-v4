from mango_explorer_v4.types.serum3_orders import Serum3Orders


class Serum3OrdersHelper:
    @staticmethod
    def is_active(serum3: Serum3Orders):
        return serum3.market_index != 65535
