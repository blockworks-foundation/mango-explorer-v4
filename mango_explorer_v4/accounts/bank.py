import typing
from dataclasses import dataclass
from solana.publickey import PublicKey
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
import borsh_construct as borsh
from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from anchorpy.borsh_extension import BorshPubkey
from ..program_id import MANGO_PROGRAM_ID
from .. import types


class BankJSON(typing.TypedDict):
    group: str
    name: list[int]
    mint: str
    vault: str
    oracle: str
    oracle_config: types.oracle_config.OracleConfigJSON
    stable_price_model: types.stable_price_model.StablePriceModelJSON
    deposit_index: types.i80f48.I80F48JSON
    borrow_index: types.i80f48.I80F48JSON
    indexed_deposits: types.i80f48.I80F48JSON
    indexed_borrows: types.i80f48.I80F48JSON
    index_last_updated: int
    bank_rate_last_updated: int
    avg_utilization: types.i80f48.I80F48JSON
    adjustment_factor: types.i80f48.I80F48JSON
    util0: types.i80f48.I80F48JSON
    rate0: types.i80f48.I80F48JSON
    util1: types.i80f48.I80F48JSON
    rate1: types.i80f48.I80F48JSON
    max_rate: types.i80f48.I80F48JSON
    collected_fees_native: types.i80f48.I80F48JSON
    loan_origination_fee_rate: types.i80f48.I80F48JSON
    loan_fee_rate: types.i80f48.I80F48JSON
    maint_asset_weight: types.i80f48.I80F48JSON
    init_asset_weight: types.i80f48.I80F48JSON
    maint_liab_weight: types.i80f48.I80F48JSON
    init_liab_weight: types.i80f48.I80F48JSON
    liquidation_fee: types.i80f48.I80F48JSON
    dust: types.i80f48.I80F48JSON
    flash_loan_token_account_initial: int
    flash_loan_approved_amount: int
    token_index: int
    bump: int
    mint_decimals: int
    bank_num: int
    min_vault_to_deposits_ratio: float
    net_borrow_limit_window_size_ts: int
    last_net_borrows_window_start_ts: int
    net_borrow_limit_per_window_quote: int
    net_borrows_in_window: int
    borrow_weight_scale_start_quote: float
    deposit_weight_scale_start_quote: float
    reserved: list[int]


@dataclass
class Bank:
    discriminator: typing.ClassVar = b"\x8e1\xa6\xf22Ba\xbc"
    layout: typing.ClassVar = borsh.CStruct(
        "group" / BorshPubkey,
        "name" / borsh.U8[16],
        "mint" / BorshPubkey,
        "vault" / BorshPubkey,
        "oracle" / BorshPubkey,
        "oracle_config" / types.oracle_config.OracleConfig.layout,
        "stable_price_model" / types.stable_price_model.StablePriceModel.layout,
        "deposit_index" / types.i80f48.I80F48.layout,
        "borrow_index" / types.i80f48.I80F48.layout,
        "indexed_deposits" / types.i80f48.I80F48.layout,
        "indexed_borrows" / types.i80f48.I80F48.layout,
        "index_last_updated" / borsh.U64,
        "bank_rate_last_updated" / borsh.U64,
        "avg_utilization" / types.i80f48.I80F48.layout,
        "adjustment_factor" / types.i80f48.I80F48.layout,
        "util0" / types.i80f48.I80F48.layout,
        "rate0" / types.i80f48.I80F48.layout,
        "util1" / types.i80f48.I80F48.layout,
        "rate1" / types.i80f48.I80F48.layout,
        "max_rate" / types.i80f48.I80F48.layout,
        "collected_fees_native" / types.i80f48.I80F48.layout,
        "loan_origination_fee_rate" / types.i80f48.I80F48.layout,
        "loan_fee_rate" / types.i80f48.I80F48.layout,
        "maint_asset_weight" / types.i80f48.I80F48.layout,
        "init_asset_weight" / types.i80f48.I80F48.layout,
        "maint_liab_weight" / types.i80f48.I80F48.layout,
        "init_liab_weight" / types.i80f48.I80F48.layout,
        "liquidation_fee" / types.i80f48.I80F48.layout,
        "dust" / types.i80f48.I80F48.layout,
        "flash_loan_token_account_initial" / borsh.U64,
        "flash_loan_approved_amount" / borsh.U64,
        "token_index" / borsh.U16,
        "bump" / borsh.U8,
        "mint_decimals" / borsh.U8,
        "bank_num" / borsh.U32,
        "min_vault_to_deposits_ratio" / borsh.F64,
        "net_borrow_limit_window_size_ts" / borsh.U64,
        "last_net_borrows_window_start_ts" / borsh.U64,
        "net_borrow_limit_per_window_quote" / borsh.I64,
        "net_borrows_in_window" / borsh.I64,
        "borrow_weight_scale_start_quote" / borsh.F64,
        "deposit_weight_scale_start_quote" / borsh.F64,
        "reserved" / borsh.U8[2120],
    )
    group: PublicKey
    name: list[int]
    mint: PublicKey
    vault: PublicKey
    oracle: PublicKey
    oracle_config: types.oracle_config.OracleConfig
    stable_price_model: types.stable_price_model.StablePriceModel
    deposit_index: types.i80f48.I80F48
    borrow_index: types.i80f48.I80F48
    indexed_deposits: types.i80f48.I80F48
    indexed_borrows: types.i80f48.I80F48
    index_last_updated: int
    bank_rate_last_updated: int
    avg_utilization: types.i80f48.I80F48
    adjustment_factor: types.i80f48.I80F48
    util0: types.i80f48.I80F48
    rate0: types.i80f48.I80F48
    util1: types.i80f48.I80F48
    rate1: types.i80f48.I80F48
    max_rate: types.i80f48.I80F48
    collected_fees_native: types.i80f48.I80F48
    loan_origination_fee_rate: types.i80f48.I80F48
    loan_fee_rate: types.i80f48.I80F48
    maint_asset_weight: types.i80f48.I80F48
    init_asset_weight: types.i80f48.I80F48
    maint_liab_weight: types.i80f48.I80F48
    init_liab_weight: types.i80f48.I80F48
    liquidation_fee: types.i80f48.I80F48
    dust: types.i80f48.I80F48
    flash_loan_token_account_initial: int
    flash_loan_approved_amount: int
    token_index: int
    bump: int
    mint_decimals: int
    bank_num: int
    min_vault_to_deposits_ratio: float
    net_borrow_limit_window_size_ts: int
    last_net_borrows_window_start_ts: int
    net_borrow_limit_per_window_quote: int
    net_borrows_in_window: int
    borrow_weight_scale_start_quote: float
    deposit_weight_scale_start_quote: float
    reserved: list[int]

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: PublicKey,
        commitment: typing.Optional[Commitment] = None,
        program_id: PublicKey = MANGO_PROGRAM_ID,
    ) -> typing.Optional["Bank"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id.to_solders():
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[PublicKey],
        commitment: typing.Optional[Commitment] = None,
        program_id: PublicKey = MANGO_PROGRAM_ID,
    ) -> typing.List[typing.Optional["Bank"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["Bank"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "Bank":
        if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
            raise AccountInvalidDiscriminator(
                "The discriminator for this account is invalid"
            )
        dec = Bank.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        return cls(
            group=dec.group,
            name=dec.name,
            mint=dec.mint,
            vault=dec.vault,
            oracle=dec.oracle,
            oracle_config=types.oracle_config.OracleConfig.from_decoded(
                dec.oracle_config
            ),
            stable_price_model=types.stable_price_model.StablePriceModel.from_decoded(
                dec.stable_price_model
            ),
            deposit_index=types.i80f48.I80F48.from_decoded(dec.deposit_index),
            borrow_index=types.i80f48.I80F48.from_decoded(dec.borrow_index),
            indexed_deposits=types.i80f48.I80F48.from_decoded(dec.indexed_deposits),
            indexed_borrows=types.i80f48.I80F48.from_decoded(dec.indexed_borrows),
            index_last_updated=dec.index_last_updated,
            bank_rate_last_updated=dec.bank_rate_last_updated,
            avg_utilization=types.i80f48.I80F48.from_decoded(dec.avg_utilization),
            adjustment_factor=types.i80f48.I80F48.from_decoded(dec.adjustment_factor),
            util0=types.i80f48.I80F48.from_decoded(dec.util0),
            rate0=types.i80f48.I80F48.from_decoded(dec.rate0),
            util1=types.i80f48.I80F48.from_decoded(dec.util1),
            rate1=types.i80f48.I80F48.from_decoded(dec.rate1),
            max_rate=types.i80f48.I80F48.from_decoded(dec.max_rate),
            collected_fees_native=types.i80f48.I80F48.from_decoded(
                dec.collected_fees_native
            ),
            loan_origination_fee_rate=types.i80f48.I80F48.from_decoded(
                dec.loan_origination_fee_rate
            ),
            loan_fee_rate=types.i80f48.I80F48.from_decoded(dec.loan_fee_rate),
            maint_asset_weight=types.i80f48.I80F48.from_decoded(dec.maint_asset_weight),
            init_asset_weight=types.i80f48.I80F48.from_decoded(dec.init_asset_weight),
            maint_liab_weight=types.i80f48.I80F48.from_decoded(dec.maint_liab_weight),
            init_liab_weight=types.i80f48.I80F48.from_decoded(dec.init_liab_weight),
            liquidation_fee=types.i80f48.I80F48.from_decoded(dec.liquidation_fee),
            dust=types.i80f48.I80F48.from_decoded(dec.dust),
            flash_loan_token_account_initial=dec.flash_loan_token_account_initial,
            flash_loan_approved_amount=dec.flash_loan_approved_amount,
            token_index=dec.token_index,
            bump=dec.bump,
            mint_decimals=dec.mint_decimals,
            bank_num=dec.bank_num,
            min_vault_to_deposits_ratio=dec.min_vault_to_deposits_ratio,
            net_borrow_limit_window_size_ts=dec.net_borrow_limit_window_size_ts,
            last_net_borrows_window_start_ts=dec.last_net_borrows_window_start_ts,
            net_borrow_limit_per_window_quote=dec.net_borrow_limit_per_window_quote,
            net_borrows_in_window=dec.net_borrows_in_window,
            borrow_weight_scale_start_quote=dec.borrow_weight_scale_start_quote,
            deposit_weight_scale_start_quote=dec.deposit_weight_scale_start_quote,
            reserved=dec.reserved,
        )

    def to_json(self) -> BankJSON:
        return {
            "group": str(self.group),
            "name": self.name,
            "mint": str(self.mint),
            "vault": str(self.vault),
            "oracle": str(self.oracle),
            "oracle_config": self.oracle_config.to_json(),
            "stable_price_model": self.stable_price_model.to_json(),
            "deposit_index": self.deposit_index.to_json(),
            "borrow_index": self.borrow_index.to_json(),
            "indexed_deposits": self.indexed_deposits.to_json(),
            "indexed_borrows": self.indexed_borrows.to_json(),
            "index_last_updated": self.index_last_updated,
            "bank_rate_last_updated": self.bank_rate_last_updated,
            "avg_utilization": self.avg_utilization.to_json(),
            "adjustment_factor": self.adjustment_factor.to_json(),
            "util0": self.util0.to_json(),
            "rate0": self.rate0.to_json(),
            "util1": self.util1.to_json(),
            "rate1": self.rate1.to_json(),
            "max_rate": self.max_rate.to_json(),
            "collected_fees_native": self.collected_fees_native.to_json(),
            "loan_origination_fee_rate": self.loan_origination_fee_rate.to_json(),
            "loan_fee_rate": self.loan_fee_rate.to_json(),
            "maint_asset_weight": self.maint_asset_weight.to_json(),
            "init_asset_weight": self.init_asset_weight.to_json(),
            "maint_liab_weight": self.maint_liab_weight.to_json(),
            "init_liab_weight": self.init_liab_weight.to_json(),
            "liquidation_fee": self.liquidation_fee.to_json(),
            "dust": self.dust.to_json(),
            "flash_loan_token_account_initial": self.flash_loan_token_account_initial,
            "flash_loan_approved_amount": self.flash_loan_approved_amount,
            "token_index": self.token_index,
            "bump": self.bump,
            "mint_decimals": self.mint_decimals,
            "bank_num": self.bank_num,
            "min_vault_to_deposits_ratio": self.min_vault_to_deposits_ratio,
            "net_borrow_limit_window_size_ts": self.net_borrow_limit_window_size_ts,
            "last_net_borrows_window_start_ts": self.last_net_borrows_window_start_ts,
            "net_borrow_limit_per_window_quote": self.net_borrow_limit_per_window_quote,
            "net_borrows_in_window": self.net_borrows_in_window,
            "borrow_weight_scale_start_quote": self.borrow_weight_scale_start_quote,
            "deposit_weight_scale_start_quote": self.deposit_weight_scale_start_quote,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: BankJSON) -> "Bank":
        return cls(
            group=PublicKey(obj["group"]),
            name=obj["name"],
            mint=PublicKey(obj["mint"]),
            vault=PublicKey(obj["vault"]),
            oracle=PublicKey(obj["oracle"]),
            oracle_config=types.oracle_config.OracleConfig.from_json(
                obj["oracle_config"]
            ),
            stable_price_model=types.stable_price_model.StablePriceModel.from_json(
                obj["stable_price_model"]
            ),
            deposit_index=types.i80f48.I80F48.from_json(obj["deposit_index"]),
            borrow_index=types.i80f48.I80F48.from_json(obj["borrow_index"]),
            indexed_deposits=types.i80f48.I80F48.from_json(obj["indexed_deposits"]),
            indexed_borrows=types.i80f48.I80F48.from_json(obj["indexed_borrows"]),
            index_last_updated=obj["index_last_updated"],
            bank_rate_last_updated=obj["bank_rate_last_updated"],
            avg_utilization=types.i80f48.I80F48.from_json(obj["avg_utilization"]),
            adjustment_factor=types.i80f48.I80F48.from_json(obj["adjustment_factor"]),
            util0=types.i80f48.I80F48.from_json(obj["util0"]),
            rate0=types.i80f48.I80F48.from_json(obj["rate0"]),
            util1=types.i80f48.I80F48.from_json(obj["util1"]),
            rate1=types.i80f48.I80F48.from_json(obj["rate1"]),
            max_rate=types.i80f48.I80F48.from_json(obj["max_rate"]),
            collected_fees_native=types.i80f48.I80F48.from_json(
                obj["collected_fees_native"]
            ),
            loan_origination_fee_rate=types.i80f48.I80F48.from_json(
                obj["loan_origination_fee_rate"]
            ),
            loan_fee_rate=types.i80f48.I80F48.from_json(obj["loan_fee_rate"]),
            maint_asset_weight=types.i80f48.I80F48.from_json(obj["maint_asset_weight"]),
            init_asset_weight=types.i80f48.I80F48.from_json(obj["init_asset_weight"]),
            maint_liab_weight=types.i80f48.I80F48.from_json(obj["maint_liab_weight"]),
            init_liab_weight=types.i80f48.I80F48.from_json(obj["init_liab_weight"]),
            liquidation_fee=types.i80f48.I80F48.from_json(obj["liquidation_fee"]),
            dust=types.i80f48.I80F48.from_json(obj["dust"]),
            flash_loan_token_account_initial=obj["flash_loan_token_account_initial"],
            flash_loan_approved_amount=obj["flash_loan_approved_amount"],
            token_index=obj["token_index"],
            bump=obj["bump"],
            mint_decimals=obj["mint_decimals"],
            bank_num=obj["bank_num"],
            min_vault_to_deposits_ratio=obj["min_vault_to_deposits_ratio"],
            net_borrow_limit_window_size_ts=obj["net_borrow_limit_window_size_ts"],
            last_net_borrows_window_start_ts=obj["last_net_borrows_window_start_ts"],
            net_borrow_limit_per_window_quote=obj["net_borrow_limit_per_window_quote"],
            net_borrows_in_window=obj["net_borrows_in_window"],
            borrow_weight_scale_start_quote=obj["borrow_weight_scale_start_quote"],
            deposit_weight_scale_start_quote=obj["deposit_weight_scale_start_quote"],
            reserved=obj["reserved"],
        )
