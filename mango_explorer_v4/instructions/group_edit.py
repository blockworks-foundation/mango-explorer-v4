from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class GroupEditArgs(typing.TypedDict):
    admin_opt: typing.Optional[PublicKey]
    fast_listing_admin_opt: typing.Optional[PublicKey]
    security_admin_opt: typing.Optional[PublicKey]
    testing_opt: typing.Optional[int]
    version_opt: typing.Optional[int]
    deposit_limit_quote_opt: typing.Optional[int]
    buyback_fees_opt: typing.Optional[bool]
    buyback_fees_bonus_factor_opt: typing.Optional[float]
    buyback_fees_swap_mango_account_opt: typing.Optional[PublicKey]
    mngo_token_index_opt: typing.Optional[int]
    buyback_fees_expiry_interval_opt: typing.Optional[int]


layout = borsh.CStruct(
    "admin_opt" / borsh.Option(BorshPubkey),
    "fast_listing_admin_opt" / borsh.Option(BorshPubkey),
    "security_admin_opt" / borsh.Option(BorshPubkey),
    "testing_opt" / borsh.Option(borsh.U8),
    "version_opt" / borsh.Option(borsh.U8),
    "deposit_limit_quote_opt" / borsh.Option(borsh.U64),
    "buyback_fees_opt" / borsh.Option(borsh.Bool),
    "buyback_fees_bonus_factor_opt" / borsh.Option(borsh.F32),
    "buyback_fees_swap_mango_account_opt" / borsh.Option(BorshPubkey),
    "mngo_token_index_opt" / borsh.Option(borsh.U16),
    "buyback_fees_expiry_interval_opt" / borsh.Option(borsh.U64),
)


class GroupEditAccounts(typing.TypedDict):
    group: PublicKey
    admin: PublicKey


def group_edit(
    args: GroupEditArgs,
    accounts: GroupEditAccounts,
    program_id: PublicKey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x08X\xb7\xf9\xa6s7\xe3"
    encoded_args = layout.build(
        {
            "admin_opt": args["admin_opt"],
            "fast_listing_admin_opt": args["fast_listing_admin_opt"],
            "security_admin_opt": args["security_admin_opt"],
            "testing_opt": args["testing_opt"],
            "version_opt": args["version_opt"],
            "deposit_limit_quote_opt": args["deposit_limit_quote_opt"],
            "buyback_fees_opt": args["buyback_fees_opt"],
            "buyback_fees_bonus_factor_opt": args["buyback_fees_bonus_factor_opt"],
            "buyback_fees_swap_mango_account_opt": args[
                "buyback_fees_swap_mango_account_opt"
            ],
            "mngo_token_index_opt": args["mngo_token_index_opt"],
            "buyback_fees_expiry_interval_opt": args[
                "buyback_fees_expiry_interval_opt"
            ],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
