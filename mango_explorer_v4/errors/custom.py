import typing
from anchorpy.error import ProgramError


class SomeError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "")

    code = 6000
    name = "SomeError"
    msg = ""


class NotImplementedError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "")

    code = 6001
    name = "NotImplementedError"
    msg = ""


class MathError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "checked math error")

    code = 6002
    name = "MathError"
    msg = "checked math error"


class UnexpectedOracle(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "")

    code = 6003
    name = "UnexpectedOracle"
    msg = ""


class UnknownOracleType(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "oracle type cannot be determined")

    code = 6004
    name = "UnknownOracleType"
    msg = "oracle type cannot be determined"


class InvalidFlashLoanTargetCpiProgram(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "")

    code = 6005
    name = "InvalidFlashLoanTargetCpiProgram"
    msg = ""


class HealthMustBePositive(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "health must be positive")

    code = 6006
    name = "HealthMustBePositive"
    msg = "health must be positive"


class HealthMustBePositiveOrIncrease(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "health must be positive or increase")

    code = 6007
    name = "HealthMustBePositiveOrIncrease"
    msg = "health must be positive or increase"


class HealthMustBeNegative(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "health must be negative")

    code = 6008
    name = "HealthMustBeNegative"
    msg = "health must be negative"


class IsBankrupt(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "the account is bankrupt")

    code = 6009
    name = "IsBankrupt"
    msg = "the account is bankrupt"


class IsNotBankrupt(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "the account is not bankrupt")

    code = 6010
    name = "IsNotBankrupt"
    msg = "the account is not bankrupt"


class NoFreeTokenPositionIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "no free token position index")

    code = 6011
    name = "NoFreeTokenPositionIndex"
    msg = "no free token position index"


class NoFreeSerum3OpenOrdersIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "no free serum3 open orders index")

    code = 6012
    name = "NoFreeSerum3OpenOrdersIndex"
    msg = "no free serum3 open orders index"


class NoFreePerpPositionIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6013, "no free perp position index")

    code = 6013
    name = "NoFreePerpPositionIndex"
    msg = "no free perp position index"


class Serum3OpenOrdersExistAlready(ProgramError):
    def __init__(self) -> None:
        super().__init__(6014, "serum3 open orders exist already")

    code = 6014
    name = "Serum3OpenOrdersExistAlready"
    msg = "serum3 open orders exist already"


class InsufficentBankVaultFunds(ProgramError):
    def __init__(self) -> None:
        super().__init__(6015, "bank vault has insufficent funds")

    code = 6015
    name = "InsufficentBankVaultFunds"
    msg = "bank vault has insufficent funds"


class BeingLiquidated(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "account is currently being liquidated")

    code = 6016
    name = "BeingLiquidated"
    msg = "account is currently being liquidated"


class InvalidBank(ProgramError):
    def __init__(self) -> None:
        super().__init__(6017, "invalid bank")

    code = 6017
    name = "InvalidBank"
    msg = "invalid bank"


class ProfitabilityMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6018, "account profitability is mismatched")

    code = 6018
    name = "ProfitabilityMismatch"
    msg = "account profitability is mismatched"


class CannotSettleWithSelf(ProgramError):
    def __init__(self) -> None:
        super().__init__(6019, "cannot settle with self")

    code = 6019
    name = "CannotSettleWithSelf"
    msg = "cannot settle with self"


class PerpPositionDoesNotExist(ProgramError):
    def __init__(self) -> None:
        super().__init__(6020, "perp position does not exist")

    code = 6020
    name = "PerpPositionDoesNotExist"
    msg = "perp position does not exist"


class MaxSettleAmountMustBeGreaterThanZero(ProgramError):
    def __init__(self) -> None:
        super().__init__(6021, "max settle amount must be greater than zero")

    code = 6021
    name = "MaxSettleAmountMustBeGreaterThanZero"
    msg = "max settle amount must be greater than zero"


class HasOpenPerpOrders(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6022, "the perp position has open orders or unprocessed fill events"
        )

    code = 6022
    name = "HasOpenPerpOrders"
    msg = "the perp position has open orders or unprocessed fill events"


class OracleConfidence(ProgramError):
    def __init__(self) -> None:
        super().__init__(6023, "an oracle does not reach the confidence threshold")

    code = 6023
    name = "OracleConfidence"
    msg = "an oracle does not reach the confidence threshold"


class OracleStale(ProgramError):
    def __init__(self) -> None:
        super().__init__(6024, "an oracle is stale")

    code = 6024
    name = "OracleStale"
    msg = "an oracle is stale"


class SettlementAmountMustBePositive(ProgramError):
    def __init__(self) -> None:
        super().__init__(6025, "settlement amount must always be positive")

    code = 6025
    name = "SettlementAmountMustBePositive"
    msg = "settlement amount must always be positive"


class BankBorrowLimitReached(ProgramError):
    def __init__(self) -> None:
        super().__init__(6026, "bank utilization has reached limit")

    code = 6026
    name = "BankBorrowLimitReached"
    msg = "bank utilization has reached limit"


class BankNetBorrowsLimitReached(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6027,
            "bank net borrows has reached limit - this is an intermittent error - the limit will reset regularly",
        )

    code = 6027
    name = "BankNetBorrowsLimitReached"
    msg = "bank net borrows has reached limit - this is an intermittent error - the limit will reset regularly"


class TokenPositionDoesNotExist(ProgramError):
    def __init__(self) -> None:
        super().__init__(6028, "token position does not exist")

    code = 6028
    name = "TokenPositionDoesNotExist"
    msg = "token position does not exist"


CustomError = typing.Union[
    SomeError,
    NotImplementedError,
    MathError,
    UnexpectedOracle,
    UnknownOracleType,
    InvalidFlashLoanTargetCpiProgram,
    HealthMustBePositive,
    HealthMustBePositiveOrIncrease,
    HealthMustBeNegative,
    IsBankrupt,
    IsNotBankrupt,
    NoFreeTokenPositionIndex,
    NoFreeSerum3OpenOrdersIndex,
    NoFreePerpPositionIndex,
    Serum3OpenOrdersExistAlready,
    InsufficentBankVaultFunds,
    BeingLiquidated,
    InvalidBank,
    ProfitabilityMismatch,
    CannotSettleWithSelf,
    PerpPositionDoesNotExist,
    MaxSettleAmountMustBeGreaterThanZero,
    HasOpenPerpOrders,
    OracleConfidence,
    OracleStale,
    SettlementAmountMustBePositive,
    BankBorrowLimitReached,
    BankNetBorrowsLimitReached,
    TokenPositionDoesNotExist,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: SomeError(),
    6001: NotImplementedError(),
    6002: MathError(),
    6003: UnexpectedOracle(),
    6004: UnknownOracleType(),
    6005: InvalidFlashLoanTargetCpiProgram(),
    6006: HealthMustBePositive(),
    6007: HealthMustBePositiveOrIncrease(),
    6008: HealthMustBeNegative(),
    6009: IsBankrupt(),
    6010: IsNotBankrupt(),
    6011: NoFreeTokenPositionIndex(),
    6012: NoFreeSerum3OpenOrdersIndex(),
    6013: NoFreePerpPositionIndex(),
    6014: Serum3OpenOrdersExistAlready(),
    6015: InsufficentBankVaultFunds(),
    6016: BeingLiquidated(),
    6017: InvalidBank(),
    6018: ProfitabilityMismatch(),
    6019: CannotSettleWithSelf(),
    6020: PerpPositionDoesNotExist(),
    6021: MaxSettleAmountMustBeGreaterThanZero(),
    6022: HasOpenPerpOrders(),
    6023: OracleConfidence(),
    6024: OracleStale(),
    6025: SettlementAmountMustBePositive(),
    6026: BankBorrowLimitReached(),
    6027: BankNetBorrowsLimitReached(),
    6028: TokenPositionDoesNotExist(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
