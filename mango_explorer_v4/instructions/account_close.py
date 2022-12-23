from __future__ import annotations
import typing
from solana.publickey import PublicKey
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import MANGO_PROGRAM_ID


class AccountCloseArgs(typing.TypedDict):
    force_close: bool


layout = borsh.CStruct("force_close" / borsh.Bool)


class AccountCloseAccounts(typing.TypedDict):
    group: PublicKey
    account: PublicKey
    owner: PublicKey
    sol_destination: PublicKey


def account_close(
    args: AccountCloseArgs,
    accounts: AccountCloseAccounts,
    program_id: PublicKey = MANGO_PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(
            pubkey=accounts["sol_destination"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"s\x05\xc0\x1cV\xdd\x89f"
    encoded_args = layout.build(
        {
            "force_close": args["force_close"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
