from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class Serum3EditMarketArgs(typing.TypedDict):
    reduce_only_opt: typing.Optional[bool]


layout = borsh.CStruct("reduce_only_opt" / borsh.Option(borsh.Bool))


class Serum3EditMarketAccounts(typing.TypedDict):
    group: PublicKey
    admin: PublicKey
    market: PublicKey


def serum3_edit_market(
    args: Serum3EditMarketArgs,
    accounts: Serum3EditMarketAccounts,
    program_id: PublicKey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["market"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"1s\xff\x17R\t^~"
    encoded_args = layout.build(
        {
            "reduce_only_opt": args["reduce_only_opt"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
