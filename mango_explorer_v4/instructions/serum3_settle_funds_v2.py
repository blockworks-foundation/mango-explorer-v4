from __future__ import annotations
import typing
from solana.publickey import PublicKey
from spl.token.constants import TOKEN_PROGRAM_ID
from solana.transaction import TransactionInstruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class Serum3SettleFundsV2Args(typing.TypedDict):
    fees_to_dao: bool


layout = borsh.CStruct("fees_to_dao" / borsh.Bool)


class Serum3SettleFundsV2Accounts(typing.TypedDict):
    v1: V1Nested
    v2: V2Nested


class V1Nested(typing.TypedDict):
    group: PublicKey
    account: PublicKey
    owner: PublicKey
    open_orders: PublicKey
    serum_market: PublicKey
    serum_program: PublicKey
    serum_market_external: PublicKey
    market_base_vault: PublicKey
    market_quote_vault: PublicKey
    market_vault_signer: PublicKey
    quote_bank: PublicKey
    quote_vault: PublicKey
    base_bank: PublicKey
    base_vault: PublicKey


class V2Nested(typing.TypedDict):
    quote_oracle: PublicKey
    base_oracle: PublicKey


class V1Nested(typing.TypedDict):
    group: PublicKey
    account: PublicKey
    owner: PublicKey
    open_orders: PublicKey
    serum_market: PublicKey
    serum_program: PublicKey
    serum_market_external: PublicKey
    market_base_vault: PublicKey
    market_quote_vault: PublicKey
    market_vault_signer: PublicKey
    quote_bank: PublicKey
    quote_vault: PublicKey
    base_bank: PublicKey
    base_vault: PublicKey


def serum3_settle_funds_v2(
    args: Serum3SettleFundsV2Args,
    accounts: Serum3SettleFundsV2Accounts,
    program_id: PublicKey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> TransactionInstruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["v1"]["group"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["v1"]["account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["v1"]["owner"], is_signer=True, is_writable=False),
        AccountMeta(
            pubkey=accounts["v1"]["open_orders"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["v1"]["serum_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["v1"]["serum_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["v1"]["serum_market_external"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["v1"]["market_base_vault"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["v1"]["market_quote_vault"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["v1"]["market_vault_signer"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["v1"]["quote_bank"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["v1"]["quote_vault"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["v1"]["base_bank"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["v1"]["base_vault"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["v2"]["quote_oracle"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["v2"]["base_oracle"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x05\xddk\x17\xf7\xd3/\xdd"
    encoded_args = layout.build(
        {
            "fees_to_dao": args["fees_to_dao"],
        }
    )
    data = identifier + encoded_args
    return TransactionInstruction(keys, program_id, data)
