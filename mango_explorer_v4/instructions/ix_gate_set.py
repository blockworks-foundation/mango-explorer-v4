from __future__ import annotations
import typing
from solana.publickey import PublicKey
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class IxGateSetArgs(typing.TypedDict):
    ix_gate: int


layout = borsh.CStruct("ix_gate" / borsh.U128)


class IxGateSetAccounts(typing.TypedDict):
    group: PublicKey
    admin: PublicKey


def ix_gate_set(
    args: IxGateSetArgs,
    accounts: IxGateSetAccounts,
    program_id: PublicKey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["group"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xc9\xb1Ub/\xdd\x8a\xf8"
    encoded_args = layout.build(
        {
            "ix_gate": args["ix_gate"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
