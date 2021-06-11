import os
import json

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from solaris_liquidbot import LiquidBot

url = 'https://api.devnet.solana.com'
payer_keypair = json.loads(os.getenv('PAYER_KEYPAIR'))

bot = LiquidBot(url, payer_keypair)
bot.check_and_liquidate_unhealthy_obligations()