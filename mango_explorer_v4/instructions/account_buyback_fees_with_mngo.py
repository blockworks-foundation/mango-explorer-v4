from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class AccountBuybackFeesWithMngoArgs(typing.TypedDict):
    max_buyback: int


layout = borsh.CStruct("max_buyback" / borsh.U64)


class AccountBuybackFeesWithMngoAccounts(typing.TypedDict):
    group: PublicKey
    account: PublicKey
    owner: PublicKey
    dao_account: PublicKey
    mngo_bank: PublicKey
    mngo_oracle: PublicKey
    fees_bank: PublicKey
    fees_oracle: PublicKey


def account_buyback_fees_with_mngo(
    args: AccountBuybackFeesWithMngoArgs,
    accounts: AccountBuybackFeesWithMngoAccounts,
    program_id: PublicKey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["dao_account"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["mngo_bank"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["mngo_oracle"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["fees_bank"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["fees_oracle"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x0c\x19B\x8b\x16`f\xc1"
    encoded_args = layout.build(
        {
            "max_buyback": args["max_buyback"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
