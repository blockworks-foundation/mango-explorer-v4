from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.system_program import SYS_PROGRAM_ID
from solana.sysvar import SYSVAR_RENT_PUBKEY
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import MANGO_PROGRAM_ID


class TokenRegisterArgs(typing.TypedDict):
    token_index: int
    name: str
    oracle_config: types.oracle_config_params.OracleConfigParams
    interest_rate_params: types.interest_rate_params.InterestRateParams
    loan_fee_rate: float
    loan_origination_fee_rate: float
    maint_asset_weight: float
    init_asset_weight: float
    maint_liab_weight: float
    init_liab_weight: float
    liquidation_fee: float
    min_vault_to_deposits_ratio: float
    net_borrow_limit_window_size_ts: int
    net_borrow_limit_per_window_quote: int


layout = borsh.CStruct(
    "token_index" / borsh.U16,
    "name" / borsh.String,
    "oracle_config" / types.oracle_config_params.OracleConfigParams.layout,
    "interest_rate_params" / types.interest_rate_params.InterestRateParams.layout,
    "loan_fee_rate" / borsh.F32,
    "loan_origination_fee_rate" / borsh.F32,
    "maint_asset_weight" / borsh.F32,
    "init_asset_weight" / borsh.F32,
    "maint_liab_weight" / borsh.F32,
    "init_liab_weight" / borsh.F32,
    "liquidation_fee" / borsh.F32,
    "min_vault_to_deposits_ratio" / borsh.F64,
    "net_borrow_limit_window_size_ts" / borsh.U64,
    "net_borrow_limit_per_window_quote" / borsh.I64,
)


class TokenRegisterAccounts(typing.TypedDict):
    group: PublicKey
    admin: PublicKey
    mint: PublicKey
    bank: PublicKey
    vault: PublicKey
    mint_info: PublicKey
    oracle: PublicKey
    payer: PublicKey


def token_register(
    args: TokenRegisterArgs,
    accounts: TokenRegisterAccounts,
    program_id: PublicKey = MANGO_PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["bank"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["mint_info"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["oracle"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"m\x1c\x87:\xa2\xd6q&"
    encoded_args = layout.build(
        {
            "token_index": args["token_index"],
            "name": args["name"],
            "oracle_config": args["oracle_config"].to_encodable(),
            "interest_rate_params": args["interest_rate_params"].to_encodable(),
            "loan_fee_rate": args["loan_fee_rate"],
            "loan_origination_fee_rate": args["loan_origination_fee_rate"],
            "maint_asset_weight": args["maint_asset_weight"],
            "init_asset_weight": args["init_asset_weight"],
            "maint_liab_weight": args["maint_liab_weight"],
            "init_liab_weight": args["init_liab_weight"],
            "liquidation_fee": args["liquidation_fee"],
            "min_vault_to_deposits_ratio": args["min_vault_to_deposits_ratio"],
            "net_borrow_limit_window_size_ts": args["net_borrow_limit_window_size_ts"],
            "net_borrow_limit_per_window_quote": args[
                "net_borrow_limit_per_window_quote"
            ],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
