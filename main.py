import os,re,math,logging
import random
import time

import discord
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import app_commands, TextChannel
from discord.ui import View, button
from datetime import datetime
from itertools import zip_longest
import asyncio

import keep_alive

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]
SERVICE_ACCOUNT_FILE = "credentials.json"

sheet_id = '1LlWii5IAM34-Dlei9wZfDm6lMjdrFvGX7F5-tJgd35s'
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

keep_alive.keep_alive()

load_dotenv()
TOKEN, GUILD_ID = os.getenv('DISCORD_TOKEN'), 1402945521957470228

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
logging.basicConfig(level=logging.DEBUG, handlers=[handler])

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents, status=discord.Status.do_not_disturb)

TIER_EMOJIS = {
    1: "💎", 2: "👑", 3: "🏆", 4: "⭐", 5: "✨",
}

TIER_COLOURS = {
    1: 0x30a9ff, 2: 0xffcd36, 3: 0xff6f41, 4: 0xff82ad, 5: 0x886eff
}


@bot.event
async def on_ready():
    # sync commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Error syncing commands: {e}")



    print(f"Fruitbridge bot is now online. ({bot.user})")


#################
## SAY COMMAND ##
#################
@bot.tree.command(
    name="say",
    description="Make fruitbridge say something!"
)
@app_commands.describe(
    message="Your message (e.g. Hello world!)"
)
async def result(interaction: discord.Interaction,
    message: str,
    ):
    await interaction.response.send_message(content=message)
    return



bot.run(TOKEN)


# /result ign:AbyssalMC tag:@abyssalmc method1:Waterlog detector rail (1.2) method2:TNT ignite (1.4) method3:Survival waterlog (1.5) subtier:1.415 rank:2
