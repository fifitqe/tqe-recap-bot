import asyncio
import discord
from discord.ext import commands
from config import CHANNEL_ID_TO_ANALYST
from parser import route_message
from database import log_trade
from scheduler import eod_scheduler

intents = discord.Intents.default()
intents.message_content = True
intents.members          = True
intents.presences        = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
            print(f"[Bot] Online as {bot.user}")
            print(f"[Bot] Watching {len(CHANNEL_ID_TO_ANALYST)} channels")
            asyncio.create_task(eod_scheduler(bot))

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
                action     = result.get("action", "entry")
    ticker     = result.get("ticker", "")
    strike     = result.get("strike")
    expiry     = result.get("expiry")
    price      = result.get("price")
    status_map = {"trim": "Trimmed", "exit": "Closed"}
    status     = status_map.get(action, "Open")
    raw_text   = (message.content or "")[:500]
    message_id = str(message.id)
    log_trade(
                    analyst=analyst,
                    channel_id=message.channel.id,
                    ticker=ticker,
                    action=action,
                    strike=strike,
                    expiry=expiry,
                    price=price,
                    status=status,
                    raw_text=raw_text,
                    message_id=message_id,
    )
    print(f"[Bot] {action.upper()} {ticker} | {analyst}")
    await bot.process_commands(message)
