import asyncio
import discord
import io
from datetime import date, datetime, timedelta
import pytz
from config import OUTPUT_CHANNEL_ID, EOD_HOUR, EOD_MINUTE
from database import get_todays_closed_trimmed, log_daily_recap
from graphic import build_graphic

ET = pytz.timezone("America/New_York")

async def run_eod(bot):
    today  = date.today().isoformat()
    trades = get_todays_closed_trimmed(today)
    if not trades:
        print(f"[EOD] No closed/trimmed trades for {today}")
        return
    closed  = sum(1 for t in trades if t.get("status") == "Closed")
    trimmed = sum(1 for t in trades if t.get("status") == "Trimmed")
    img_bytes = build_graphic(trades, today)
    channel   = bot.get_channel(OUTPUT_CHANNEL_ID)
    if not channel:
        print(f"[EOD] Channel {OUTPUT_CHANNEL_ID} not found")
        return
    file = discord.File(io.BytesIO(img_bytes), filename=f"recap_{today}.png")
    msg  = await channel.send(
        content=f"**Daily Trade Recap -- {today}**",
        file=file,
    )
    log_daily_recap(today, closed, trimmed, str(msg.id))
    print(f"[EOD] Recap posted: {msg.id}")

async def eod_scheduler(bot):
    print(f"[Scheduler] Started - fires daily at {EOD_HOUR}:{EOD_MINUTE:02d} ET")
    while True:
        now_et  = datetime.now(ET)
        fire_et = now_et.replace(hour=EOD_HOUR, minute=EOD_MINUTE, second=0, microsecond=0)
        if now_et >= fire_et:
            fire_et = fire_et + timedelta(days=1)
        wait_s = (fire_et - now_et).total_seconds()
        print(f"[Scheduler] Next EOD in {wait_s/3600:.1f}h")
        await asyncio.sleep(wait_s)
        try:
            await run_eod(bot)
        except Exception as e:
            print(f"[Scheduler] Error: {e}")
