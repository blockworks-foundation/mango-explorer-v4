from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from .. import types
from ..program_id import MANGO_PROGRAM_ID


class TokenEditArgs(typing.TypedDict):
    oracle_opt: typing.Optional[PublicKey]
    oracle_config_opt: typing.Optional[types.oracle_config_params.OracleConfigParams]
    group_insurance_fund_opt: typing.Optional[bool]
    interest_rate_params_opt: typing.Optional[
        types.interest_rate_params.InterestRateParams
    ]
    loan_fee_rate_opt: typing.Optional[float]
    loan_origination_fee_rate_opt: typing.Optional[float]
    maint_asset_weight_opt: typing.Optional[float]
    init_asset_weight_opt: typing.Optional[float]
    maint_liab_weight_opt: typing.Optional[float]
    init_liab_weight_opt: typing.Optional[float]
    liquidation_fee_opt: typing.Optional[float]
    stable_price_delay_interval_seconds_opt: typing.Optional[int]
    stable_price_delay_growth_limit_opt: typing.Optional[float]
    stable_price_growth_limit_opt: typing.Optional[float]
    min_vault_to_deposits_ratio_opt: typing.Optional[float]
    net_borrow_limit_per_window_quote_opt: typing.Optional[int]
    net_borrow_limit_window_size_ts_opt: typing.Optional[int]
    borrow_weight_scale_start_quote_opt: typing.Optional[float]
    deposit_weight_scale_start_quote_opt: typing.Optional[float]
    reset_stable_price: bool
    reset_net_borrow_limit: bool


layout = borsh.CStruct(
    "oracle_opt" / borsh.Option(BorshPubkey),
    "oracle_config_opt"
    / borsh.Option(types.oracle_config_params.OracleConfigParams.layout),
    "group_insurance_fund_opt" / borsh.Option(borsh.Bool),
    "interest_rate_params_opt"
    / borsh.Option(types.interest_rate_params.InterestRateParams.layout),
    "loan_fee_rate_opt" / borsh.Option(borsh.F32),
    "loan_origination_fee_rate_opt" / borsh.Option(borsh.F32),
    "maint_asset_weight_opt" / borsh.Option(borsh.F32),
    "init_asset_weight_opt" / borsh.Option(borsh.F32),
    "maint_liab_weight_opt" / borsh.Option(borsh.F32),
    "init_liab_weight_opt" / borsh.Option(borsh.F32),
    "liquidation_fee_opt" / borsh.Option(borsh.F32),
    "stable_price_delay_interval_seconds_opt" / borsh.Option(borsh.U32),
    "stable_price_delay_growth_limit_opt" / borsh.Option(borsh.F32),
    "stable_price_growth_limit_opt" / borsh.Option(borsh.F32),
    "min_vault_to_deposits_ratio_opt" / borsh.Option(borsh.F64),
    "net_borrow_limit_per_window_quote_opt" / borsh.Option(borsh.I64),
    "net_borrow_limit_window_size_ts_opt" / borsh.Option(borsh.U64),
    "borrow_weight_scale_start_quote_opt" / borsh.Option(borsh.F64),
    "deposit_weight_scale_start_quote_opt" / borsh.Option(borsh.F64),
    "reset_stable_price" / borsh.Bool,
    "reset_net_borrow_limit" / borsh.Bool,
)


class TokenEditAccounts(typing.TypedDict):
    group: PublicKey
    admin: PublicKey
    mint_info: PublicKey
    oracle: PublicKey


def token_edit(
    args: TokenEditArgs,
    accounts: TokenEditAccounts,
    program_id: PublicKey = MANGO_PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["mint_info"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["oracle"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x91\xcc\x0b\xd1\xae\x86O>"
    encoded_args = layout.build(
        {
            "oracle_opt": args["oracle_opt"],
            "oracle_config_opt": (
                None
                if args["oracle_config_opt"] is None
                else args["oracle_config_opt"].to_encodable()
            ),
            "group_insurance_fund_opt": args["group_insurance_fund_opt"],
            "interest_rate_params_opt": (
                None
                if args["interest_rate_params_opt"] is None
                else args["interest_rate_params_opt"].to_encodable()
            ),
            "loan_fee_rate_opt": args["loan_fee_rate_opt"],
            "loan_origination_fee_rate_opt": args["loan_origination_fee_rate_opt"],
            "maint_asset_weight_opt": args["maint_asset_weight_opt"],
            "init_asset_weight_opt": args["init_asset_weight_opt"],
            "maint_liab_weight_opt": args["maint_liab_weight_opt"],
            "init_liab_weight_opt": args["init_liab_weight_opt"],
            "liquidation_fee_opt": args["liquidation_fee_opt"],
            "stable_price_delay_interval_seconds_opt": args[
                "stable_price_delay_interval_seconds_opt"
            ],
            "stable_price_delay_growth_limit_opt": args[
                "stable_price_delay_growth_limit_opt"
            ],
            "stable_price_growth_limit_opt": args["stable_price_growth_limit_opt"],
            "min_vault_to_deposits_ratio_opt": args["min_vault_to_deposits_ratio_opt"],
            "net_borrow_limit_per_window_quote_opt": args[
                "net_borrow_limit_per_window_quote_opt"
            ],
            "net_borrow_limit_window_size_ts_opt": args[
                "net_borrow_limit_window_size_ts_opt"
            ],
            "borrow_weight_scale_start_quote_opt": args[
                "borrow_weight_scale_start_quote_opt"
            ],
            "deposit_weight_scale_start_quote_opt": args[
                "deposit_weight_scale_start_quote_opt"
            ],
            "reset_stable_price": args["reset_stable_price"],
            "reset_net_borrow_limit": args["reset_net_borrow_limit"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
