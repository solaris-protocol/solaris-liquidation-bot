from construct import Int8ub, Int16ub, Int64ub, Struct, Array, Byte, Bytes, Container
import requests
import json
import base64

import solana
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.account import Account
from solana.publickey import PublicKey
from solana.transaction import AccountMeta, Transaction, TransactionInstruction
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import AuthorityType

PUBLIC_KEY_LAYOUT = Bytes(32)
DECIMAL = Bytes(16)

OBLIGATION_LAYOUT_LEN = 916


source_liquidity_publickey = PublicKey('C7PhDXuS9H6a5GfdUrEsakmVWokXRv6jfbRDiAPpVEtE')
reserve_publickey = PublicKey('Bfs6BTc2t6Epb9hjGpLpQcSmQ1ZycKsEv6mV3QuV3VzZ')
lending_market_publickey = PublicKey('9cu7LXZYJ6oNNi7X4anv2LP8NP58h8zKiE61LMcgJt5h')
lending_market_derived_authority_publickey = PublicKey('4B3rs3z48eW1iw3JNTrQZsTJnCqEbFMuGVk3TVMAtQeM')
flash_loan_fee_receiver_publickey = PublicKey('ESApvknZkcGwee2rhjL7yGKyabtdCvDJ28US8VhsWutw')
flash_loan_fee_receiver_mint_publickey = PublicKey('So11111111111111111111111111111111111111112')
host_fee_receiver_publickey = PublicKey('6oLtsmgq3kMTJs11eM4rpdcQjyMAXw84VvTUAi2XHnqu')
flash_loan_program_derived_authority_publickey = PublicKey('CQUV8znxqS1td7QZVywf2g5pmwGgUjh8WWKoNsHBPiuF')

flash_loan_program_id = PublicKey('2HrfwEiotfbaAKqSiqscZcc1BnLNhDY8NfeyKVHC9y6p')

derive_authority_publickey = PublicKey('CQUV8znxqS1td7QZVywf2g5pmwGgUjh8WWKoNsHBPiuF')

class LiquidBot:
    """ This is LiquidBot Class """
    def __init__(self, url: str, payer_keypair: list, token_lending_program_address: str, threaded=True):
        self.__url = url
        self.__payer = Account(payer_keypair[:32])
        self.__client = Client(url)
        self.__token_lending_program_pubkey = PublicKey(token_lending_program_address)
        self.threaded = threaded

    def get_obligaions(self) -> dict:
        headers = {'Content-Type': 'application/json'}
        body = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getProgramAccounts",
            "params": [
                str(self.__token_lending_program_pubkey),
                {
                    "encoding": "jsonParsed",
                    "filters": [
                        {
                            "dataSize": OBLIGATION_LAYOUT_LEN
                        }
                    ]
                }
            ]
        })

        responce = requests.post(self.__url, headers=headers, data=body)
        if responce.status_code != 200:
            raise ValueError("Invalid request")

        return json.loads(responce.text).get('result')

    def __deserialize_obligation(self, data: bytes) -> Struct:
        """
        data: decoded from base64 bytes
        """
        last_update_format = Struct(
            "slot" / Int64ub,
            "stale" / Int8ub,
        )

        format = Struct(
            "version" / Int8ub,
            "last_update" / last_update_format,
            "lending_market" / PUBLIC_KEY_LAYOUT,
            "owner" / PUBLIC_KEY_LAYOUT,
            "deposited_value" / Bytes(16),
            "borrowed_value" / Bytes(16),
            "allowed_borrow_value" / Bytes(16),
            "unhealthy_borrow_value" / Bytes(16),
            "deposits_len" / Int8ub,
            "borrows_len" / Int8ub
            # "data_flat" /
        )

        return format.parse(data)

    def check_and_liquidate_unhealthy_obligations(self):
        for obligation in self.get_obligaions():
            data = obligation.get('account').get('data')
            if isinstance(data, list) and len(data) > 0:
                data = data[0]

            data = base64.b64decode(data)

            obligation_container = self.__deserialize_obligation(data)
            
            borrowed_value = int.from_bytes(obligation_container.borrowed_value, "little") # amount
            unhealthy_borrow_value = int.from_bytes(obligation_container.unhealthy_borrow_value, "little")

            print(f'obligation pubkey: {obligation.get("pubkey")}')
            print(f'borrowed_value: {borrowed_value}, unhealthy_borrow_value: {unhealthy_borrow_value}, diff: {borrowed_value - unhealthy_borrow_value}')

            if borrowed_value == 0 and unhealthy_borrow_value == 0:
                continue

            if borrowed_value >= unhealthy_borrow_value:
                # print(obligation_container)
                self.__liquidate_obligation(borrowed_value)

    def __liquidate_obligation(self, amount: int):
        # create destination liquidity
        destination_liquidity_publickey = Token.create_wrapped_native_account(
            self.__client,
            program_id=TOKEN_PROGRAM_ID,
            owner=derive_authority_publickey,
            payer=self.__payer,
            amount=100000
        )

        # amount = 1 * 10 ** 2       # 100
        tag = 13
        data = tag.to_bytes(1, byteorder='little') + amount.to_bytes(8, byteorder='little')

        txn = Transaction()
        txn.add(
            TransactionInstruction(
                keys=[
                    AccountMeta(pubkey=source_liquidity_publickey, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=destination_liquidity_publickey, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=reserve_publickey, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=lending_market_publickey, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=lending_market_derived_authority_publickey, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=flash_loan_program_id, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=flash_loan_fee_receiver_publickey, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=host_fee_receiver_publickey, is_signer=False, is_writable=True),
                    AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
                    AccountMeta(pubkey=flash_loan_program_derived_authority_publickey, is_signer=False, is_writable=False)
                ],
                program_id=self.__token_lending_program_pubkey,
                data=data
            )
        )

        rpc_response = self.__client.send_transaction(
            txn,
            self.__payer,
            opts=TxOpts(skip_preflight=True, skip_confirmation=False)
        )
        # print(f'rpc_response: {json.dumps(rpc_response, indent=2)}')