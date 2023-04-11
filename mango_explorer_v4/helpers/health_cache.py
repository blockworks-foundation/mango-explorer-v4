from mango_explorer_v4.accounts.mango_account import MangoAccount
from mango_explorer_v4.types.health_cache import HealthCache
from mango_explorer_v4.helpers.mango_account import MangoAccountHelper


class HealthCacheHelper():
    @staticmethod
    def from_mango_account(mango_account: MangoAccount):
        token_infos = [
            token_position.token_index
            for token_position in  MangoAccountHelper.active_token_positions(mango_account)
        ]