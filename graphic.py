from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

# ── Colours ──────────────────────────────────────────────────────────────────
BG        = (18, 18, 18)
ROW_BG    = (24, 24, 24)
ROW_ALT   = (20, 20, 20)
GOLD      = (212, 175, 55)
WHITE     = (255, 255, 255)
GREY      = (160, 160, 160)
DIM       = (100, 100, 100)
GREEN_BG  = (30, 90, 40)
GREEN_FG  = (72, 199, 100)
RED_BG    = (100, 28, 28)
RED_FG    = (220, 80, 80)
AMBER_BG  = (90, 65, 10)
AMBER_FG  = (212, 175, 55)
BAR_GREEN = (72, 199, 100)
BAR_RED   = (220, 80, 80)
BAR_AMBER = (212, 175, 55)

# ── Layout ───────────────────────────────────────────────────────────────────
W        = 1400
PAD      = 48
ROW_H    = 110
HEADER_H = 130
FOOTER_H = 160
BAR_W    = 7

# Analyst order
ANALYST_ORDER = ['fifi', 'clark', 'braamski', 'tony', 'zeph', 'vinny', 'bigmac']

ANALYST_LABELS = {
    'fifi':     'FIFI',
    'clark':    'CLARK',
    'braamski': 'BRAAMSKI',
    'tony':     'TONY',
    'zeph':     'ZEPH',
    'vinny':    'VINNY',
    'bigmac':   'BIGMAC',
}


def _font(size, bold=False):
    paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _badge(draw, cx, cy, text, fg, bg, font, pad_x=22, pad_y=10, radius=18, outline=True):
    """Draw a rounded-rectangle badge centred at (cx, cy)."""
    tw = draw.textlength(text, font=font)
    th = font.size
    bw = tw + pad_x * 2
    bh = th + pad_y * 2
    x0 = cx - bw // 2
    y0 = cy - bh // 2
    x1 = x0 + bw
    y1 = y0 + bh
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=bg,
                           outline=fg if outline else None, width=2)
    draw.text((x0 + pad_x, y0 + pad_y), text, font=font, fill=fg)
    return bw


def _row_color(status, pnl):
    """Return (bar_color, status_fg, status_bg, pnl_fg, pnl_bg) for a trade row."""
    pnl_val = 0
    try:
        pnl_val = float(pnl.replace('%', '').replace('+', ''))
    except Exception:
        pass

    if status == 'Trimmed':
        return BAR_AMBER, AMBER_FG, AMBER_BG, AMBER_FG, AMBER_BG
    elif pnl_val < 0:
        return BAR_RED, RED_FG, RED_BG, RED_FG, RED_BG
    else:
        return BAR_GREEN, GREEN_FG, GREEN_BG, GREEN_FG, GREEN_BG


def _flatten_trades(data):
    """Return ordered list of (analyst_key, trade_dict) skipping analysts with no trades."""
    rows = []
    for key in ANALYST_ORDER:
        trades = data.get(key, {}).get('trades', [])
        for t in trades:
            rows.append((key, t))
    # include analysts not in order list
    for key in data:
        if key not in ANALYST_ORDER:
            for t in data[key].get('trades', []):
                rows.append((key, t))
    return rows


def build_graphic(data: dict, trade_of_day: dict, date_str: str) -> bytes:
    rows = _flatten_trades(data)
    n_rows = max(len(rows), 1)

    H = HEADER_H + n_rows * ROW_H + FOOTER_H + 20
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Gold border lines ─────────────────────────────────────────────────
    draw.rectangle([0, 0, W - 1, 4], fill=GOLD)
    draw.rectangle([0, H - 4, W - 1, H - 1], fill=GOLD)

    # ── Header ────────────────────────────────────────────────────────────
    title_f  = _font(52, bold=True)
    sub_f    = _font(26)
    title    = "FiFi's TQE \u2014 Daily Trade Recap"
    subtitle = f'{date_str}  \u2022  EOD Summary  \u2022  Trimmed & Closed Only'
    tw = draw.textlength(title, font=title_f)
    sw = draw.textlength(subtitle, font=sub_f)
    draw.text(((W - tw) // 2, 18), title, font=title_f, fill=WHITE)
    draw.text(((W - sw) // 2, 82), subtitle, font=sub_f, fill=GOLD)
    # thin gold rule below header
    draw.rectangle([PAD, HEADER_H - 4, W - PAD, HEADER_H - 2], fill=GOLD)

    # ── Trade rows ────────────────────────────────────────────────────────
    analyst_f = _font(24)
    ticker_f  = _font(54, bold=True)
    detail_f  = _font(26)
    price_f   = _font(26)
    badge_sf  = _font(22, bold=True)   # status badge font
    badge_pf  = _font(28, bold=True)   # pnl badge font

    badge_area_w = 340   # right-side area reserved for two badges
    content_right = W - PAD - badge_area_w

    for i, (analyst_key, trade) in enumerate(rows):
        y0 = HEADER_H + i * ROW_H
        y1 = y0 + ROW_H
        row_bg = ROW_BG if i % 2 == 0 else ROW_ALT
        draw.rectangle([0, y0, W - 1, y1 - 1], fill=row_bg)

        ticker = trade.get('ticker', '')
        strike = trade.get('strike', '')
        expiry = trade.get('expiry', '')
        price  = trade.get('price', '')
        pnl    = trade.get('pnl', '')
        status = trade.get('status', 'Closed')

        bar_col, st_fg, st_bg, pnl_fg, pnl_bg = _row_color(status, pnl)

        # left colour bar
        draw.rectangle([0, y0, BAR_W, y1 - 1], fill=bar_col)

        row_mid = y0 + ROW_H // 2

        # analyst label (small, grey, above ticker)
        alabel = ANALYST_LABELS.get(analyst_key, analyst_key.upper())
        draw.text((PAD + BAR_W + 6, y0 + 8), alabel, font=analyst_f, fill=GREY)

        # ticker (large bold)
        draw.text((PAD + BAR_W + 6, y0 + 32), ticker, font=ticker_f, fill=WHITE)

        # strike + expiry (detail line, right of ticker)
        ticker_w = draw.textlength(ticker, font=ticker_f)
        detail_x = PAD + BAR_W + 6 + ticker_w + 24
        detail   = f'{expiry} {strike}'
        draw.text((detail_x, y0 + 50), detail, font=detail_f, fill=GREY)

        # price arrow: $entry → $exit  (only if price available)
        if price:
            try:
                entry = float(price)
                pnl_val = float(pnl.replace('%', '').replace('+', ''))
                exit_p = round(entry * (1 + pnl_val / 100), 2)
                price_str = f'${entry:.2f} \u2192 ${exit_p:.2f}'
            except Exception:
                price_str = f'${price}'
            price_x = detail_x
            draw.text((price_x, row_mid - 16), price_str, font=price_f, fill=GREY)

        # badges (right side)
        pnl_badge_cx  = W - PAD - 80
        stat_badge_cx = W - PAD - 80 - 170
        badge_cy      = row_mid

        # status badge
        _badge(draw, stat_badge_cx, badge_cy, status.upper(), st_fg, st_bg, badge_sf)
        # pnl badge
        _badge(draw, pnl_badge_cx, badge_cy, pnl, pnl_fg, pnl_bg, badge_pf)

    # ── Footer separator ──────────────────────────────────────────────────
    footer_y = HEADER_H + n_rows * ROW_H
    draw.rectangle([PAD, footer_y + 4, W - PAD, footer_y + 6], fill=GOLD)

    # ── Stats row ─────────────────────────────────────────────────────────
    all_pnls = []
    for _, t in rows:
        try:
            all_pnls.append(float(t.get('pnl', '0').replace('%', '').replace('+', '')))
        except Exception:
            pass

    wins   = sum(1 for v in all_pnls if v > 0)
    losses = sum(1 for v in all_pnls if v < 0)
    total  = len(all_pnls)
    avg    = (sum(all_pnls) / total) if total else 0
    avg_str = f'+{avg:.0f}%' if avg >= 0 else f'{avg:.0f}%'
    avg_col = GREEN_FG if avg >= 0 else RED_FG

    stats = [
        ('TRADES TODAY', str(total), WHITE),
        ('WINS',         str(wins),  GREEN_FG),
        ('LOSSES',       str(losses), RED_FG),
        ('AVG RETURN',   avg_str,    avg_col),
    ]
    label_f = _font(22)
    val_f   = _font(44, bold=True)
    col_w   = (W - 2 * PAD) // 4
    sy      = footer_y + 20
    for ci, (lbl, val, col) in enumerate(stats):
        cx = PAD + ci * col_w + col_w // 2
        lw = draw.textlength(lbl, font=label_f)
        vw = draw.textlength(val, font=val_f)
        draw.text((cx - lw // 2, sy), lbl, font=label_f, fill=GREY)
        draw.text((cx - vw // 2, sy + 30), val, font=val_f, fill=col)

    # ── Caption ───────────────────────────────────────────────────────────
    cap_f = _font(20)
    cap   = 'TQERecapBot  \u2022  Auto-generated  \u2022  Only Trimmed & Closed positions shown'
    cw    = draw.textlength(cap, font=cap_f)
    draw.text(((W - cw) // 2, H - 38), cap, font=cap_f, fill=DIM)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
