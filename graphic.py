from PIL import Image, ImageDraw, ImageFont
import io

BG_COLOR     = (15, 15, 25)
HEADER_COLOR = (30, 30, 50)
TEXT_COLOR   = (220, 220, 220)
GREEN        = (80, 200, 120)
GOLD         = (255, 200, 50)
ACCENT       = (100, 149, 237)

CARD_W   = 900
PADDING  = 24
ROW_H    = 54
HEADER_H = 80

def _load_font(size):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()

def build_graphic(trades: list, date: str) -> bytes:
    closed_trades  = [t for t in trades if t.get("status") == "Closed"]
    trimmed_trades = [t for t in trades if t.get("status") == "Trimmed"]
    shown = closed_trades + trimmed_trades

    rows  = max(len(shown), 1)
    img_h = HEADER_H + PADDING + rows * ROW_H + PADDING * 2
    img   = Image.new("RGB", (CARD_W, img_h), BG_COLOR)
    draw  = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (CARD_W, HEADER_H)], fill=HEADER_COLOR)
    font_title = _load_font(28)
    font_sub   = _load_font(16)
    font_row   = _load_font(18)

    draw.text((PADDING, 14), "FiFi TQE -- Daily Trade Recap", font=font_title, fill=GOLD)
    draw.text((PADDING, 52), date, font=font_sub, fill=TEXT_COLOR)

    closed_count  = len(closed_trades)
    trimmed_count = len(trimmed_trades)
    summary = f"{closed_count} Closed  |  {trimmed_count} Trimmed"
    draw.text((CARD_W - 260, 30), summary, font=font_sub, fill=ACCENT)

    y = HEADER_H + PADDING // 2
    draw.line([(PADDING, y), (CARD_W - PADDING, y)], fill=ACCENT, width=1)

    if not shown:
        draw.text((PADDING, y + 20), "No closed/trimmed trades today.", font=font_row, fill=TEXT_COLOR)
    else:
        y = HEADER_H + PADDING
        for i, trade in enumerate(shown):
            row_bg = (22, 22, 38) if i % 2 == 0 else (28, 28, 48)
            draw.rectangle([(PADDING, y), (CARD_W - PADDING, y + ROW_H - 4)], fill=row_bg)
            status  = trade.get("status", "")
            color   = GREEN if status == "Closed" else GOLD
            ticker  = trade.get("ticker") or "---"
            analyst = trade.get("analyst") or ""
            strike  = trade.get("strike") or ""
            expiry  = trade.get("expiry") or ""
            price   = trade.get("price")
            price_s = f"@ ${price:.2f}" if price else ""
            label   = f"[{status}]"
            detail  = f"{ticker}  {strike}  {expiry}  {price_s}".strip()
            by_line = f"by {analyst}" if analyst else ""
            draw.text((PADDING + 8,   y + 8), label,   font=font_row, fill=color)
            draw.text((PADDING + 110, y + 8), detail,  font=font_row, fill=TEXT_COLOR)
            draw.text((CARD_W - 170, y + 8),  by_line, font=font_sub,  fill=ACCENT)
            y += ROW_H

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
