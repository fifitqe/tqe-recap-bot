import os

DISCORD_TOKEN  = os.getenv("DISCORD_TOKEN")
SUPABASE_URL   = os.getenv("SUPABASE_URL")
SUPABASE_KEY   = os.getenv("SUPABASE_KEY")

GUILD_ID           = 1462698217106833420
OUTPUT_CHANNEL_ID  = 1496609336221503579
EOD_HOUR   = 16
EOD_MINUTE = 15

ANALYST_CHANNELS = {
    "fifi":     {"id": 1477726962951786537, "mode": "alertsify"},
    "clark":    {"id": 1481847660288671814, "mode": "text"},
    "braamski": {"id": 1486518060461588490, "mode": "alertsify"},
    "tony":     {"id": 1497020191781949511, "mode": "text"},
    "vinny":    {"id": 1497021031385137293, "mode": "text"},
    "zeph":     {"id": 1497020299965890633, "mode": "text"},
    "bigmac":   {"id": 1500930518861217852, "mode": "bigmac"},
}

CHANNEL_ID_TO_ANALYST = {v["id"]: k for k, v in ANALYST_CHANNELS.items()}

BIGMAC_THESIS_KEYWORDS = [
    "thesis", "plan", "watchlist", "watching", "tier-1", "tier 1",
    "setup", "rationale", "invalidate", "idea", "note", "target",
    "looking at", "keeping an eye", "on my radar"
]
