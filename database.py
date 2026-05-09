import os
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_sb = None

def get_client():
        global _sb
        if _sb is None:
                    _sb = create_client(SUPABASE_URL, SUPABASE_KEY)
                return _sb

def log_trade(analyst: str, channel_id: int, ticker: str, action: str,
                            strike: str = None, expiry: str = None, price: float = None,
                            status: str = "Open", raw_text: str = None, message_id: str = None):
                                    sb = get_client()
                                    data = {
                                        "analyst": analyst,
                                        "channel_id": str(channel_id),
                                        "ticker": ticker,
                                        "action": action,
                                        "strike": strike,
                                        "expiry": expiry,
                                        "price": price,
                                        "status": status,
                                        "raw_text": raw_text,
                                        "message_id": message_id,
                                    }
                                    sb.table("trades").insert(data).execute()

def update_trade_status(trade_id: int, status: str, exit_price: float = None):
        sb = get_client()
    update = {"status": status}
    if exit_price is not None:
                update["exit_price"] = exit_price
            sb.table("trades").update(update).eq("id", trade_id).execute()

def get_todays_closed_trimmed(today: str):
        sb = get_client()
    res = (
                sb.table("trades")
                .select("*")
                .in_("status", ["Closed", "Trimmed"])
                .gte("created_at", today + "T00:00:00")
                .lte("created_at", today + "T23:59:59")
                .execute()
    )
    return res.data or []

def log_daily_recap(date: str, closed: int, trimmed: int, message_id: str):
        sb = get_client()
    sb.table("daily_recaps").insert({
                "date": date,
                "closed_count": closed,
                "trimmed_count": trimmed,
                "message_id": message_id,
    }).execute()
