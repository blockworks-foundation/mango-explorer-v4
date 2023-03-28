from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class AccountToggleFreezeArgs(typing.TypedDict):
    freeze: bool


layout = borsh.CStruct("freeze" / borsh.Bool)


class AccountToggleFreezeAccounts(typing.TypedDict):
    group: PublicKey
    account: PublicKey
    admin: PublicKey


def account_toggle_freeze(
    args: AccountToggleFreezeArgs,
    accounts: AccountToggleFreezeAccounts,
    program_id: PublicKey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x0b\xf3\xe9\xf7WO`\xc6"
    encoded_args = layout.build(
        {
            "freeze": args["freeze"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
