import json

import solana
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
import solana.system_program as sp
from solana.system_program import SYS_PROGRAM_ID
from solana.transaction import AccountMeta, Transaction, TransactionInstruction
from solana.rpc.types import TxOpts
from spl.token._layouts import ACCOUNT_LAYOUT
from spl.token.instructions import AuthorityType
from solana.account import Account
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.rpc.commitment import Recent, Root

sourceLiquidityPubkey = 'C7PhDXuS9H6a5GfdUrEsakmVWokXRv6jfbRDiAPpVEtE'
reservePubkey = 'Bfs6BTc2t6Epb9hjGpLpQcSmQ1ZycKsEv6mV3QuV3VzZ'
lendingMarketPubkey = '9cu7LXZYJ6oNNi7X4anv2LP8NP58h8zKiE61LMcgJt5h'
lendingMarketDerivedAuthorityPubkey = '4B3rs3z48eW1iw3JNTrQZsTJnCqEbFMuGVk3TVMAtQeM'
flashLoanFeeReceiverPubkey = 'ESApvknZkcGwee2rhjL7yGKyabtdCvDJ28US8VhsWutw'
flashLoanFeeReceiverMintPubkey = 'So11111111111111111111111111111111111111112'
hostFeeReceiverPubkey = '6oLtsmgq3kMTJs11eM4rpdcQjyMAXw84VvTUAi2XHnqu'

flash_loan_program_id = PublicKey('2HrfwEiotfbaAKqSiqscZcc1BnLNhDY8NfeyKVHC9y6p')

url = 'http://127.0.0.1:8899'
url = 'https://api.devnet.solana.com'
client = Client(url)

keypair = [104,199,171,119,244,99,119,192,178,248,101,99,210,7,16,254,175,172,71,30,133,195,233,4,140,160,200,15,118,185,111,248,204,23,15,233,245,121,230,144,133,86,150,182,131,223,53,254,213,165,140,242,48,142,52,42,224,101,148,220,105,116,171,180]
my_tmp_account = Account(keypair[:32])
print(f'my_tmp_account: {my_tmp_account.public_key()}')

token_lending_program_pubkey = PublicKey('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
token_lending_program_pubkey = PublicKey('6h5geweHee42FbxZrYAcYJ8SGVAjG6sGow5dtzcKtrJw')

# my_bytes = 'flashloan_1324'.encode('utf-8').hex().encode('utf-8')
# my_bytes = bytes(token_lending_program_pubkey)
# # my_bytes = bytes(my_bytes)
# # my_bytes = b'flashloan'
# print(type(my_bytes))
# # address, nonce = PublicKey.find_program_address(my_bytes, flash_loan_program_id)
# seeds = list(my_bytes)
# address, nonce = PublicKey.create_program_address(list(my_bytes), flash_loan_program_id)

derive_authority_publickey = PublicKey('CQUV8znxqS1td7QZVywf2g5pmwGgUjh8WWKoNsHBPiuF')

def create_destination_liquidity(initializer_account: Account) -> PublicKey:    
    # not impl
    # wrapped_native_account = Token.create_wrapped_native_account(
    #     client,
    #     program_id=TOKEN_PROGRAM_ID,
    #     owner=derive_authority_publickey,
    #     payer=my_tmp_account,
    #     amount=100000
    # )

    token = Token(client, pubkey=flashLoanFeeReceiverMintPubkey,
        program_id=TOKEN_PROGRAM_ID,
        payer=my_tmp_account
    )

    token_account_publickey = token.create_account(
        owner=my_tmp_account.public_key()
    )

    rpc_response = token.set_authority_custum(
        account=token_account_publickey,
        current_authority=my_tmp_account.public_key(),
        authority_type=AuthorityType.ACCOUNT_OWNER,
        new_authority=derive_authority_publickey
    )
    print(f'rpc_response: {rpc_response}')

    return token_account_publickey




source_liquidity_publickey = PublicKey(sourceLiquidityPubkey)
reserve_publickey = PublicKey(reservePubkey)
lending_market_publickey = PublicKey(lendingMarketPubkey)
lending_market_derived_authority_publickey = PublicKey(lendingMarketDerivedAuthorityPubkey)
flash_loan_fee_receiver_publickey = PublicKey(flashLoanFeeReceiverPubkey)
flash_loan_fee_receiver_mint_publickey = PublicKey(flashLoanFeeReceiverMintPubkey)
host_fee_receiver_publickey = PublicKey(hostFeeReceiverPubkey)

destination_liquidity_publickey = create_destination_liquidity(my_tmp_account)


amount = 1 * 10 ** 2       # 1 0000 0000
tag = 13
data = tag.to_bytes(1, byteorder='little') + amount.to_bytes(8, byteorder='little')
# data = tag.to_bytes(1, byteorder='big') + amount.to_bytes(8, byteorder='big')
data = b'\x0D\x27\x10\x00\x00\x00\x00\x00\x00'

txn = Transaction()
txn.add(
    TransactionInstruction(
        keys=[
            AccountMeta(pubkey=source_liquidity_publickey, is_signer=False, is_writable=True),
            AccountMeta(pubkey=destination_liquidity_publickey, is_signer=False, is_writable=True),
            AccountMeta(pubkey=reserve_publickey, is_signer=False, is_writable=True),
            AccountMeta(pubkey=flash_loan_fee_receiver_publickey, is_signer=False, is_writable=True),
            AccountMeta(pubkey=host_fee_receiver_publickey, is_signer=False, is_writable=True),
            AccountMeta(pubkey=lending_market_publickey, is_signer=False, is_writable=False),
            AccountMeta(pubkey=lending_market_derived_authority_publickey, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=flash_loan_program_id, is_signer=False, is_writable=False),
        ],
        program_id=token_lending_program_pubkey,
        data=data
    )
)

rpc_response = client.send_transaction(
    txn,
    my_tmp_account,
    opts=TxOpts(skip_preflight=True, skip_confirmation=False)
)
print(f'rpc_response: {json.dumps(rpc_response, indent=2)}')