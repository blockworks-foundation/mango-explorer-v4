import decimal
import sys

from mango_explorer_v4.accounts.bank import Bank
from mango_explorer_v4.types.i80f48 import I80F48


class BankHelper():
    @staticmethod
    def native_deposits(bank: Bank) -> decimal.Decimal:
        return bank.indexed_deposits.to_decimal() * bank.deposit_index.to_decimal()

    @staticmethod
    def native_borrows(bank: Bank) -> decimal.Decimal:
        return bank.indexed_borrows.to_decimal() * bank.borrow_index.to_decimal()

    @staticmethod
    def scaled_init_asset_weight(bank: Bank, price: decimal.Decimal) -> I80F48:
        deposits_quote = BankHelper.native_deposits(bank) * price

        if bank.deposit_weight_scale_start_quote >= sys.maxsize or deposits_quote <= bank.deposit_weight_scale_start_quote:
            return bank.init_asset_weight

        return I80F48.from_decimal(bank.init_asset_weight.to_decimal() * decimal.Decimal(bank.deposit_weight_scale_start_quote) / deposits_quote)

    @staticmethod
    def scaled_init_liab_weight(bank: Bank, price: decimal.Decimal) -> I80F48:
        borrows_quote = BankHelper.native_borrows(bank) * price

        if bank.borrow_weight_scale_start_quote >= sys.maxsize or borrows_quote <= bank.borrow_weight_scale_start_quote:
            return bank.init_liab_weight

        return I80F48.from_decimal(bank.init_liab_weight.to_decimal() * borrows_quote / decimal.Decimal(bank.borrow_weight_scale_start_quote))



