from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

BG        = (15, 14, 8)
CARD_BG   = (26, 24, 16)
HERO_BG   = (30, 27, 14)
BORDER    = (184, 134, 11)
GOLD      = (212, 160, 23)
MUTED     = (138, 122, 80)
LIGHT     = (200, 191, 160)
GREEN     = (74, 222, 128)
RED       = (248, 113, 113)
DIVIDER   = (40, 36, 20)

DISPLAY_NAMES = {
    'fifi': 'BadGirlFiFi', 'clark': 'clark kent',
    'braamski': 'Braamskis', 'tony': 'TonyD',
    'zeph': 'ZephTrades', 'vinny': 'Vinny', 'bigmac': 'BigMac',
}

FIFI_GROUP    = ['fifi']
ANALYST_GROUP = ['clark', 'braamski']
TRUSTED_GROUP = ['tony', 'zeph', 'vinny', 'bigmac']

# Canvas dimensions - wider for readability
W = 900
PAD = 32
CARD_PAD = 20
RADIUS = 12

# Heights
ROW_H = 44
ANALYST_H = 56
SECTION_H = 36
HEADER_H = 90
HERO_H = 110
FOOTER_H = 48


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


def _section_height(members, data):
    h = SECTION_H
    for m in members:
        trades = data.get(m, {}).get('trades', [])
        rows = max(1, len(trades))
        h += ANALYST_H + rows * ROW_H + CARD_PAD + 16
    return h


def _estimate_height(data, tod):
    h = HEADER_H + PAD
    h += HERO_H + PAD
    h += _section_height(FIFI_GROUP, data) + PAD
    h += _section_height(ANALYST_GROUP, data) + PAD
    h += _section_height(TRUSTED_GROUP, data) + PAD
    h += FOOTER_H + PAD
    return h


def _draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)


def _draw_section_label(draw, y, label, fw, fh):
    lf = _font(13)
    lw = draw.textlength(label, font=lf)
    line_y = y + SECTION_H // 2
    draw.line([(PAD, line_y), (PAD + 24, line_y)], fill=DIVIDER, width=1)
    draw.text((PAD + 30, y + (SECTION_H - 14) // 2), label, font=lf, fill=MUTED)
    right_start = PAD + 30 + lw + 12
    draw.line([(right_start, line_y), (W - PAD, line_y)], fill=DIVIDER, width=1)
    return y + SECTION_H


def _draw_analyst_card(draw, y, key, analyst_data):
    trades = analyst_data.get('trades', [])
    rows = max(1, len(trades))
    card_h = ANALYST_H + rows * ROW_H + CARD_PAD
    _draw_rounded_rect(draw, (PAD, y, W - PAD, y + card_h), RADIUS, CARD_BG, BORDER, 1)

    name = DISPLAY_NAMES.get(key, key)
    nf = _font(18, bold=True)
    draw.text((PAD + CARD_PAD, y + (ANALYST_H - 20) // 2), name, font=nf, fill=GOLD)

    if not trades:
        nof = _font(14)
        draw.text((PAD + CARD_PAD, y + ANALYST_H + (ROW_H - 16) // 2), 'No trades', font=nof, fill=MUTED)
    else:
        for i, trade in enumerate(trades):
            ry = y + ANALYST_H + i * ROW_H
            if i > 0:
                draw.line([(PAD + CARD_PAD, ry), (W - PAD - CARD_PAD, ry)], fill=DIVIDER, width=1)
            pnl_val = trade.get('pnl', '')
            dot_color = GREEN if pnl_val.startswith('+') or pnl_val == '' else RED
            dot_r = 6
            dot_cx = PAD + CARD_PAD + dot_r
            dot_cy = ry + ROW_H // 2
            draw.ellipse([(dot_cx - dot_r, dot_cy - dot_r), (dot_cx + dot_r, dot_cy + dot_r)], fill=dot_color)
            tf = _font(14)
            label = trade.get('label', '')
            draw.text((PAD + CARD_PAD + dot_r * 2 + 8, ry + (ROW_H - 16) // 2), label, font=tf, fill=LIGHT)
            if pnl_val:
                pf = _font(14, bold=True)
                pc = GREEN if pnl_val.startswith('+') else RED
                pw = draw.textlength(pnl_val, font=pf)
                draw.text((W - PAD - CARD_PAD - pw, ry + (ROW_H - 16) // 2), pnl_val, font=pf, fill=pc)

    return y + card_h + 16


def build_graphic(data: dict, trade_of_day: dict, date_str: str) -> bytes:
    H = _estimate_height(data, trade_of_day)
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── Header ──────────────────────────────────────────────
    hf = _font(26, bold=True)
    sf = _font(14)
    draw.text((PAD, 18), "FiFi's TQE", font=hf, fill=GOLD)
    draw.text((PAD, 52), 'Daily Trade Recap', font=sf, fill=MUTED)

    df_label = _font(11)
    df_date  = _font(16, bold=True)
    date_w = draw.textlength(date_str, font=df_date)
    label_w = draw.textlength('DATE', font=df_label)
    right_x = W - PAD - max(date_w, label_w)
    draw.text((right_x, 20), 'DATE', font=df_label, fill=MUTED)
    draw.text((right_x, 36), date_str, font=df_date, fill=LIGHT)

    draw.line([(PAD, HEADER_H - 1), (W - PAD, HEADER_H - 1)], fill=DIVIDER, width=1)

    y = HEADER_H + PAD

    # ── Hero ────────────────────────────────────────────────
    _draw_rounded_rect(draw, (PAD, y, W - PAD, y + HERO_H), RADIUS, HERO_BG, BORDER, 1)
    tlf = _font(11)
    draw.text((PAD + CARD_PAD, y + 10), 'TRADE OF THE DAY', font=tlf, fill=MUTED)
    if trade_of_day:
        ticker  = trade_of_day.get('ticker', '')
        pnl     = trade_of_day.get('pnl', '')
        analyst = trade_of_day.get('analyst', '')
        tkf = _font(28, bold=True)
        draw.text((PAD + CARD_PAD, y + 30), ticker, font=tkf, fill=GOLD)
        if pnl:
            pf = _font(32, bold=True)
            pc = GREEN if pnl.startswith('+') else RED
            pw = draw.textlength(pnl, font=pf)
            draw.text((W - PAD - CARD_PAD - pw, y + 28), pnl, font=pf, fill=pc)
        if analyst:
            af = _font(13)
            draw.text((PAD + CARD_PAD, y + 72), analyst, font=af, fill=MUTED)
    y += HERO_H + PAD

    # ── Fifi section ────────────────────────────────────────
    y = _draw_section_label(draw, y, "FIFI'S PLAYGROUND", W, H)
    for key in FIFI_GROUP:
        y = _draw_analyst_card(draw, y, key, data.get(key, {}))
    y += PAD

    # ── Analysts section ────────────────────────────────────
    y = _draw_section_label(draw, y, 'ANALYSTS', W, H)
    for key in ANALYST_GROUP:
        y = _draw_analyst_card(draw, y, key, data.get(key, {}))
    y += PAD

    # ── Trusted traders section ──────────────────────────────
    y = _draw_section_label(draw, y, 'TRUSTED TRADERS', W, H)
    for key in TRUSTED_GROUP:
        y = _draw_analyst_card(draw, y, key, data.get(key, {}))
    y += PAD

    # ── Footer ──────────────────────────────────────────────
    ff = _font(12)
    draw.text((PAD, y + 16), 'x.com/badgirlfifi_tqe', font=ff, fill=MUTED)
    rw = draw.textlength('@Badgirlfifi_trading', font=ff)
    draw.text((W - PAD - rw, y + 16), '@Badgirlfifi_trading', font=ff, fill=MUTED)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()
