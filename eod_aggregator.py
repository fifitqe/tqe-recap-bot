import discord, io
from datetime import date
from database import get_todays_closed_trimmed, log_daily_recap
from graphic import build_graphic

async def run_eod(bot, output_channel_id: int):
    today  = date.today().isoformat()
    trades = get_todays_closed_trimmed(today)
    if not trades:
        print(f'[EOD] No trades for {today}')
        return
    closed  = sum(1 for t in trades if t['status'] == 'Closed')
    trimmed = sum(1 for t in trades if t['status'] == 'Trimmed')
    img_bytes = build_graphic(trades, today)
    channel   = bot.get_channel(output_channel_id)
    if not channel:
        print(f'[EOD] Channel {output_channel_id} not found')
        return
    file = discord.File(io.BytesIO(img_bytes), filename=f'recap_{today}.png')
    msg  = await channel.send(
        content=f'**Daily Trade Recap -- {today}** `{closed} closed, {trimmed} trimmed`',
        file=file
    )
    log_daily_recap(today, closed, trimmed, str(msg.id))
    print(f'[EOD] Recap posted: {msg.id}')
