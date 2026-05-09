import asyncio
import discord
import io
from datetime import date, datetime, timedelta
import pytz
from config import OUTPUT_CHANNEL_ID, EOD_HOUR, EOD_MINUTE
from database import get_todays_closed_trimmed, log_daily_recap
from graphic import build_graphic

ET = pytz.timezone('America/New_York')

SAMPLE_TRADES = [
    {'analyst': 'fifi',     'ticker': 'SPY',  'strike': '580C', 'expiry': '5/9',  'price': '2.45', 'pnl': '+67%',  'status': 'Closed'},
    {'analyst': 'clark',    'ticker': 'NVDA', 'strike': '870P', 'expiry': '5/9',  'price': '1.80', 'pnl': '+100%', 'status': 'Closed'},
    {'analyst': 'braamski', 'ticker': 'AAPL', 'strike': '195C', 'expiry': '5/16', 'price': '3.20', 'pnl': '+50%',  'status': 'Trimmed'},
    {'analyst': 'tony',     'ticker': 'QQQ',  'strike': '470P', 'expiry': '5/9',  'price': '0.95', 'pnl': '+95%',  'status': 'Closed'},
    {'analyst': 'zeph',     'ticker': 'META', 'strike': '550C', 'expiry': '5/16', 'price': '5.50', 'pnl': '-24%',  'status': 'Closed'},
    {'analyst': 'bigmac',   'ticker': 'TSLA', 'strike': '265C', 'expiry': '5/9',  'price': '2.10', 'pnl': '+86%',  'status': 'Closed'},
]

async def run_eod(bot, today=None, trades=None):
    if today is None:
        today = date.today().isoformat()
    if trades is None:
        trades = get_todays_closed_trimmed(today)
    if not trades:
        print(f'[EOD] No closed/trimmed trades for {today}')
        return
    closed  = sum(1 for t in trades if t.get('status') == 'Closed')
    trimmed = sum(1 for t in trades if t.get('status') == 'Trimmed')
    img_bytes = build_graphic(trades, today)
    channel = bot.get_channel(OUTPUT_CHANNEL_ID)
    if not channel:
        print(f'[EOD] Channel {OUTPUT_CHANNEL_ID} not found')
        return
    file = discord.File(io.BytesIO(img_bytes), filename=f'recap_{today}.png')
    msg  = await channel.send(
        content=f'**Daily Trade Recap -- {today}**',
        file=file,
    )
    log_daily_recap(today, closed, trimmed, str(msg.id))
    print(f'[EOD] Recap posted: {msg.id}')

async def run_test_eod(bot):
    today = date.today().isoformat()
    print('[EOD] Running TEST recap with sample data')
    await run_eod(bot, today=today, trades=SAMPLE_TRADES)

async def eod_scheduler(bot):
    print(f'[Scheduler] Started - fires daily at {EOD_HOUR}:{EOD_MINUTE:02d} ET')
    while True:
        now_et  = datetime.now(ET)
        fire_et = now_et.replace(hour=EOD_HOUR, minute=EOD_MINUTE, second=0, microsecond=0)
        if now_et >= fire_et:
            fire_et = fire_et + timedelta(days=1)
        wait_s = (fire_et - now_et).total_seconds()
        print(f'[Scheduler] Next EOD in {wait_s/3600:.1f}h')
        await asyncio.sleep(wait_s)
        try:
            await run_eod(bot)
        except Exception as e:
            print(f'[Scheduler] Error: {e}')
