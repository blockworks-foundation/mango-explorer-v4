from mango_explorer_v4.types.token_position import TokenPosition
from mango_explorer_v4.accounts.bank import Bank
from mango_explorer_v4.utils import i80f48 as i80f48_utils


def is_active(token_position: TokenPosition):
    return token_position.token_index != 65535


def balance(token_position: TokenPosition, bank: Bank):
    token_position = i80f48_utils.parse(token_position.indexed_position)

    bank_index = bank.deposit_index if token_position > 0 else bank.borrow_index

    return i80f48_utils.parse(bank_index) * token_position
