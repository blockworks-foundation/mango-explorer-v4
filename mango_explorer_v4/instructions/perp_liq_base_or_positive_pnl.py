from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class PerpLiqBaseOrPositivePnlArgs(typing.TypedDict):
    max_base_transfer: int
    max_pnl_transfer: int


layout = borsh.CStruct("max_base_transfer" / borsh.I64, "max_pnl_transfer" / borsh.U64)


class PerpLiqBaseOrPositivePnlAccounts(typing.TypedDict):
    group: PublicKey
    perp_market: PublicKey
    oracle: PublicKey
    liqor: PublicKey
    liqor_owner: PublicKey
    liqee: PublicKey
    settle_bank: PublicKey
    settle_vault: PublicKey
    settle_oracle: PublicKey


def perp_liq_base_or_positive_pnl(
    args: PerpLiqBaseOrPositivePnlArgs,
    accounts: PerpLiqBaseOrPositivePnlAccounts,
    program_id: PublicKey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["perp_market"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["oracle"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["liqor"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["liqor_owner"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["liqee"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_bank"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["settle_vault"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["settle_oracle"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"k\xaa]\x8b\xc0\x8dy\xcd"
    encoded_args = layout.build(
        {
            "max_base_transfer": args["max_base_transfer"],
            "max_pnl_transfer": args["max_pnl_transfer"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
