from __future__ import annotations
import typing
from solana.publickey import PublicKey
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.transaction import TransactionInstruction, AccountMeta
from ..program_id import MANGO_PROGRAM_ID


class StubOracleCloseAccounts(typing.TypedDict):
    group: PublicKey
    admin: PublicKey
    oracle: PublicKey
    sol_destination: PublicKey


def stub_oracle_close(
    accounts: StubOracleCloseAccounts,
    program_id: PublicKey = MANGO_PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["oracle"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["sol_destination"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\\\x89-\x03-<u\xe0"
    encoded_args = b""
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
