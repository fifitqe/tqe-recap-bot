import re
from config import BIGMAC_THESIS_KEYWORDS

# ─── Alertsify embed parser (FiFi + Braamski) ─────────────────────────────────
def parse_alertsify(message):
        if not message.embeds:
                    return None
                embed = message.embeds[0]
    title = embed.title or ""
    desc  = embed.description or ""
    text  = f"{title} {desc}"
    ticker_m = re.search(r'\$([A-Z]{1,5})', text)
    ticker   = ticker_m.group(1) if ticker_m else None
    if not ticker:
                return None
            action = "entry"
    if re.search(r'\btrim\b', text, re.I):
                action = "trim"
elif re.search(r'\b(exit|close|sold|out)\b', text, re.I):
        action = "exit"
    price_m  = re.search(r'\$?([\d]+\.[\d]{2})', text)
    strike_m = re.search(r'(\d+[Cc]|\d+[Pp]|\d+\.\d+[CcPp])', text)
    expiry_m = re.search(r'(\d{1,2}/\d{1,2}(?:/\d{2,4})?)', text)
    return {
                "action": action,
                "ticker": ticker,
                "price":  float(price_m.group(1)) if price_m else None,
                "strike": strike_m.group(1) if strike_m else None,
                "expiry": expiry_m.group(1) if expiry_m else None,
    }

# ─── Clark: plain text $TICKER MM/DD STRIKE $PRICE ───────────────────────────
def parse_clark(message):
        text = message.content or ""
    m = re.match(
                r'\$([A-Z]{1,5})\s+(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s+'
                r'(\S+)\s+\$([\d.]+)',
                text.strip(), re.I
    )
    if not m:
                return None
            return {
                        "action": "entry",
                        "ticker": m.group(1).upper(),
                        "expiry": m.group(2),
                        "strike": m.group(3),
                        "price":  float(m.group(4)),
            }

# ─── Tony: @tony-alerts Starter TICKER ───────────────────────────────────────
def parse_tony(message):
        text = message.content or ""
    m = re.search(r'(?:starter|entry|add|trim|exit)\s+([A-Z]{1,5})', text, re.I)
    if not m:
                return None
            action = "entry"
    low = text.lower()
    if "trim" in low:
                action = "trim"
elif "exit" in low or "out" in low:
        action = "exit"
    return {"action": action, "ticker": m.group(1).upper()}

# ─── Zeph: "In TICKER STRIKE for FRI" ────────────────────────────────────────
def parse_zeph(message):
        text = message.content or ""
    m = re.search(r'\bIn\s+([A-Z]{1,5})\s+(\S+)', text, re.I)
    if not m:
                return None
            return {
                        "action": "entry",
                        "ticker": m.group(1).upper(),
                        "strike": m.group(2),
            }

# ─── Vinny: minimal text + charts ────────────────────────────────────────────
def parse_vinny(message):
        text = message.content or ""
    m = re.search(r'\$([A-Z]{1,5})', text)
    if not m:
                return None
            return {"action": "entry", "ticker": m.group(1).upper()}

# ─── BigMac: only "BigMac APP" embeds ────────────────────────────────────────
ALPHA_ENGINE = "alpha engine"
BIGMAC_BOT   = "bigmac"

def parse_bigmac(message):
        author_name = (message.author.display_name or "").lower()
    if ALPHA_ENGINE in author_name:
                return None
            if BIGMAC_BOT not in author_name:
                        text = message.content or ""
                        low  = text.lower()
                        if any(kw in low for kw in BIGMAC_THESIS_KEYWORDS):
                                        return None
                                    if message.attachments:
                                                    return {"action": "exit", "ticker": "", "status": "PENDING_CLOSE"}
                                                return None
    if not message.embeds:
                return None
    return parse_alertsify(message)

# ─── Router ───────────────────────────────────────────────────────────────────
PARSERS = {
        "fifi":    parse_alertsify,
        "braamski": parse_alertsify,
        "clark":   parse_clark,
        "tony":    parse_tony,
        "zeph":    parse_zeph,
        "vinny":   parse_vinny,
        "bigmac":  parse_bigmac,
}

def route_message(analyst: str, message):
        parser = PARSERS.get(analyst)
    if parser is None:
                return None
    try:
                return parser(message)
except Exception as e:
        print(f"[Parser] Error for {analyst}: {e}")
        return None
