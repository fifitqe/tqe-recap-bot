import asyncio
import discord
from discord.ext import commands
from config import DISCORD_TOKEN
from scheduler import eod_scheduler

intents = discord.Intents.default()
intents.message_content = True
intents.members          = True
intents.presences        = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'[Main] {bot.user} is LIVE!')
    asyncio.create_task(eod_scheduler(bot))

from bot import on_message
bot.event(on_message)

bot.run(DISCORD_TOKEN)
