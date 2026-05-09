import discord
from discord.ext import commands
from config import DISCORD_TOKEN, CHANNEL_ID_TO_ANALYST
from parser import route_message
from database import upsert_trade, insert_event

intents = discord.Intents.default()
intents.message_content = True
intents.members          = True
intents.presences        = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[Bot] Online as {bot.user}")
    print(f"[Bot] Watching {len(CHANNEL_ID_TO_ANALYST)} channels")

@bot.event
async def on_message(message: discord.Message):
    analyst = CHANNEL_ID_TO_ANALYST.get(message.channel.id)
    if not analyst:
        return
    if message.author.bot and analyst != "bigmac":
        return
    result = route_message(analyst, message)
    if not result:
        await bot.process_commands(message)
        return
    event_type  = result.pop("event_type", "entry")
    posted_at   = message.created_at.isoformat()
    raw_msg     = (message.content or "")[:500]
    if event_type == "entry":
        upsert_trade({**result, "analyst": analyst, "channel_id": str(message.channel.id), "message_id": str(message.id), "posted_at": posted_at, "raw_message": raw_msg})
        print(f"[Bot] Entry: {result.get('ticker')} | {analyst}")
    elif event_type in ("exit", "trim"):
        insert_event({**result, "analyst": analyst, "channel_id": str(message.channel.id), "message_id": str(message.id), "event_type": event_type, "posted_at": posted_at, "raw_message": raw_msg})
        print(f"[Bot] {event_type.capitalize()}: {analyst}")
    await bot.process_commands(message)
