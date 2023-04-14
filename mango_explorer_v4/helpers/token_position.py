from mango_explorer_v4.types.token_position import TokenPosition
from mango_explorer_v4.accounts.bank import Bank
from decimal import Decimal


class TokenPositionHelper():
    @staticmethod
    def is_active(token_position: TokenPosition):
        return token_position.token_index != 65535

    @staticmethod
    def balance(token_position: TokenPosition, bank: Bank) -> Decimal:
        token_position = token_position.indexed_position.to_decimal()

        bank_index = bank.deposit_index if token_position > 0 else bank.borrow_index

        return (bank_index.to_decimal() * token_position) / Decimal(str(10 ** bank.mint_decimals))