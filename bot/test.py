import os
import json

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from solaris_liquidbot import LiquidBot

def test_check_and_liquidate_unhealthy_obligations():
    url = 'https://api.devnet.solana.com'
    payer_keypair = json.loads(os.getenv('PAYER_KEYPAIR'))

    token_lending_program_address = os.getenv('TOKEN_LENDING_PROGRAM_ADDRESS')
    bot = LiquidBot(url, payer_keypair, token_lending_program_address)
    bot.check_and_liquidate_unhealthy_obligations()

def test_get_obligaions():
    url = 'https://api.devnet.solana.com'
    payer_keypair = json.loads(os.getenv('PAYER_KEYPAIR'))

    token_lending_program_address = os.getenv('TOKEN_LENDING_PROGRAM_ADDRESS')
    bot = LiquidBot(url, payer_keypair, token_lending_program_address)
    obligaions = bot.get_obligaions()
    print(obligaions)