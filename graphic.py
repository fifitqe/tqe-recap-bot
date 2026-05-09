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

ANALYST_EMOJI = {
        'fifi': '\U0001f43e',
        'clark': '\U0001f976',
        'braamski': '\U0001f531',
        'tony': '\U0001f451',
        'zeph': '\U0001f389',
        'vinny': '\U0001f3b8',
        'bigmac': '\U0001f354',
}

FIFI_GROUP    = ['fifi']
ANALYST_GROUP = ['clark', 'braamski']
TRUSTED_GROUP = ['tony', 'zeph', 'vinny', 'bigmac']

W = 760; PAD = 28; CARD_PAD = 16; RADIUS = 10
ROW_H = 36; ANALYST_H = 44; SECTION_H = 30
HEADER_H = 80; HERO_H = 96; FOOTER_H = 40

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
                    h += ANALYST_H + rows * ROW_H + CARD_PAD + 12
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
        lf = _font(11)
    lw = draw.textlength(label, font=lf)
    line_y = y + SECTION_H // 2
    draw.line([(PAD, line_y), (PAD + 30, line_y)], fill=DIVIDER, width=1)
    draw.text((PAD + 36, y + 2), label, font=lf, fill=MUTED)
    right_start = PAD + 36 + lw + 10
    draw.line([(right_start, line_y), (W - PAD, line_y)], fill=DIVIDER, width=1)
    return y + SECTION_H


def _draw_analyst_card(draw, y, key, analyst_data):
        trades = analyst_data.get('trades', [])
    rows = max(1, len(trades))
    card_h = ANALYST_H + rows * ROW_H + CARD_PAD
    _draw_rounded_rect(draw, (PAD, y, W - PAD, y + card_h), RADIUS, CARD_BG, BORDER, 1)

    name = DISPLAY_NAMES.get(key, key)
    emoji = ANALYST_EMOJI.get(key, '')

    # Draw emoji
    ef = _font(18)
    ew = draw.textlength(emoji, font=ef)
    draw.text((PAD + CARD_PAD, y + 12), emoji, font=ef, fill=LIGHT)

    # Draw name next to emoji
    nf = _font(16, bold=True)
    draw.text((PAD + CARD_PAD + ew + 6, y + 14), name, font=nf, fill=GOLD)

    if not trades:
                nof = _font(12)
                draw.text((PAD + CARD_PAD, y + ANALYST_H + 4), 'No trades', font=nof, fill=MUTED)
else:
        for i, trade in enumerate(trades):
                        ry = y + ANALYST_H + i * ROW_H
                        # Divider line between rows
                        if i > 0:
                                            draw.line([(PAD + CARD_PAD, ry), (W - PAD - CARD_PAD, ry)], fill=DIVIDER, width=1)
                                        dot_color = GREEN if trade.get('pnl', '').startswith('+') or trade.get('pnl', '') == '' else RED
            draw.ellipse([(PAD + CARD_PAD, ry + 10), (PAD + CARD_PAD + 10, ry + 20)], fill=dot_color)
            tf = _font(12)
            label = trade.get('label', '')
            draw.text((PAD + CARD_PAD + 16, ry + 6), label, font=tf, fill=LIGHT)
            pnl = trade.get('pnl', '')
            if pnl:
                                pf = _font(12, bold=True)
                                pc = GREEN if pnl.startswith('+') else RED
                                pw = draw.textlength(pnl, font=pf)
                                draw.text((W - PAD - CARD_PAD - pw, ry + 6), pnl, font=pf, fill=pc)

    return y + card_h + 12


def build_graphic(data: dict, trade_of_day: dict, date_str: str) -> bytes:
        H = _estimate_height(data, trade_of_day)
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header
    hf = _font(18, bold=True)
    sf = _font(12)
    draw.text((PAD, 20), "FiFi's TQE", font=hf, fill=GOLD)
    draw.text((PAD, 46), 'Daily Trade Recap', font=sf, fill=MUTED)
    df = _font(10)
    dw = max(draw.textlength('DATE', font=df), draw.textlength(date_str, font=df))
    draw.text((W - PAD - dw, 18), 'DATE', font=df, fill=MUTED)
    draw.text((W - PAD - dw, 30), date_str, font=_font(11), fill=LIGHT)
    draw.line([(PAD, HEADER_H - 1), (W - PAD, HEADER_H - 1)], fill=DIVIDER, width=1)

    y = HEADER_H + PAD

    # Hero
    _draw_rounded_rect(draw, (PAD, y, W - PAD, y + HERO_H), RADIUS, HERO_BG, BORDER, 1)
    tlf = _font(9)
    draw.text((PAD + CARD_PAD, y + 8), 'TRADE OF THE DAY', font=tlf, fill=MUTED)
    if trade_of_day:
                ticker = trade_of_day.get('ticker', '')
        pnl = trade_of_day.get('pnl', '')
        analyst = trade_of_day.get('analyst', '')
        # Emoji + ticker on row 2
        emoji_str = '\U0001f389'
        ef = _font(20, bold=True)
        ew = draw.textlength(emoji_str, font=ef)
        draw.text((PAD + CARD_PAD, y + 24), emoji_str, font=ef, fill=LIGHT)
        tkf = _font(20, bold=True)
        draw.text((PAD + CARD_PAD + ew + 6, y + 24), ticker, font=tkf, fill=GOLD)
        if pnl:
                        pf = _font(24, bold=True)
            pc = GREEN if pnl.startswith('+') else RED
            pw = draw.textlength(pnl, font=pf)
            draw.text((W - PAD - CARD_PAD - pw, y + 20), pnl, font=pf, fill=pc)
        if analyst:
                        # analyst emoji + name row
                        analyst_key = analyst.lower().replace(' ', '')
            a_emoji = ANALYST_EMOJI.get(analyst_key, '\U0001f642')
            af = _font(11)
            aew = draw.textlength(a_emoji, font=af)
            draw.text((PAD + CARD_PAD, y + 56), a_emoji, font=af, fill=LIGHT)
            anf = _font(11)
            draw.text((PAD + CARD_PAD + aew + 4, y + 56), analyst, font=anf, fill=MUTED)
    y += HERO_H + PAD

    # Fifi section
    y = _draw_section_label(draw, y, "FIFI'S PLAYGROUND", W, H)
    for key in FIFI_GROUP:
                y = _draw_analyst_card(draw, y, key, data.get(key, {}))
    y += PAD

    # Analysts section
    y = _draw_section_label(draw, y, 'ANALYSTS', W, H)
    for key in ANALYST_GROUP:
                y = _draw_analyst_card(draw, y, key, data.get(key, {}))
    y += PAD

    # Trusted traders section
    y = _draw_section_label(draw, y, 'TRUSTED TRADERS', W, H)
    for key in TRUSTED_GROUP:
                y = _draw_analyst_card(draw, y, key, data.get(key, {}))
    y += PAD

    # Footer
    ff = _font(10)
    draw.text((PAD, y + 12), 'x.com/badgirlfifi_tqe', font=ff, fill=MUTED)
    rw = draw.textlength('@Badgirlfifi_trading', font=ff)
    draw.text((W - PAD - rw, y + 12), '@Badgirlfifi_trading', font=ff, fill=MUTED)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()
