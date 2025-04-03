import discord
from discord.ext import commands
import os
from commands.ask import ask
from commands.clear import clear
from commands.search import search
from commands.imagegen import imagegen
from commands.music import music
from commands.mcp import mcp

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

bot.add_command(ask)
bot.add_command(clear)
bot.add_command(search)
bot.add_command(imagegen)
bot.add_command(music)
bot.add_command(mcp)

@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")

bot.run(DISCORD_TOKEN)
