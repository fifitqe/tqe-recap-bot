from PIL import Image, ImageDraw, ImageFont
import io

# Palette matching FiFi TQE template
BG          = (18, 17, 10)
CARD_BG     = (24, 23, 14)
HERO_BG     = (30, 28, 16)
BORDER      = (180, 140, 40)
GOLD        = (220, 175, 50)
TAN         = (180, 160, 120)
WHITE       = (240, 238, 225)
GREEN       = (80, 200, 110)
RED         = (210, 80, 70)
GREY        = (120, 115, 95)
ACCENT_LINE = (100, 90, 50)

W           = 880
SIDE_PAD    = 22

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

def _price_str(price):
    if price is None:
        return ''
    try:
        return f'${float(price):.2f}'
    except (ValueError, TypeError):
        return f'${price}'

def _section_label(draw, y, text, font):
    draw.text((SIDE_PAD, y), text, font=font, fill=TAN)
    tw = int(font.getlength(text)) + 8
    draw.line([(SIDE_PAD + tw, y + 7), (W - SIDE_PAD, y + 7)], fill=ACCENT_LINE, width=1)

def build_graphic(trades: list, trade_date: str) -> bytes:
    by_analyst = {}
    for t in trades:
        a = t.get('analyst', 'unknown')
        by_analyst.setdefault(a, []).append(t)

    FIFI_GROUP    = ['fifi']
    ANALYST_GROUP = ['clark', 'braamski']
    TRUSTED_GROUP = ['tony', 'zeph', 'vinny', 'bigmac']

    best_trade = None
    best_pct   = -9999
    for t in trades:
        try:
            raw = str(t.get('pnl') or t.get('price') or '0')
            pct = float(raw.replace('%','').replace('+','').replace('$',''))
            if pct > best_pct:
                best_pct   = pct
                best_trade = t
        except Exception:
            pass

    ROW_H            = 34
    CARD_PAD         = 12
    HEADER_H         = 88
    HERO_H           = 90
    SECTION_H        = 26
    ANALYST_HEADER_H = 36
    FOOTER_H         = 44

    DISPLAY_NAMES = {
        'fifi':     'BadGirlFiFi',
        'clark':    'clark kent',
        'braamski': 'Braamskis',
        'tony':     'TonyD',
        'zeph':     'ZephTrades',
        'vinny':    'Vinny',
        'bigmac':   'BigMac',
    }

    def card_h(analyst):
        rows = max(len(by_analyst.get(analyst, [])), 1)
        return ANALYST_HEADER_H + rows * ROW_H + CARD_PAD

    total_h = HEADER_H + 12 + HERO_H + 16
    SECTIONS = [
        ("FIFI'S PLAYGROUND", FIFI_GROUP),
        ('ANALYSTS',          ANALYST_GROUP),
        ('TRUSTED TRADERS',   TRUSTED_GROUP),
    ]
    for _, group in SECTIONS:
        total_h += SECTION_H + 6
        for a in group:
            total_h += card_h(a) + 10
    total_h += FOOTER_H + 10

    img  = Image.new('RGB', (W, total_h), BG)
    draw = ImageDraw.Draw(img)

    f_title  = _font(28, bold=True)
    f_sub    = _font(13)
    f_date_l = _font(11)
    f_date   = _font(16, bold=True)
    f_sec    = _font(11)
    f_hero_l = _font(10)
    f_hero_t = _font(32, bold=True)
    f_hero_p = _font(28, bold=True)
    f_hero_u = _font(12)
    f_aname  = _font(16, bold=True)
    f_ticker = _font(14)
    f_pct    = _font(14, bold=True)
    f_footer = _font(12)

    y = 0

    # Header
    draw.rectangle([(0, 0), (W, HEADER_H)], fill=BG)
    draw.rounded_rectangle([(SIDE_PAD, 18), (SIDE_PAD + 36, 54)], radius=6, fill=(60, 50, 20))
    draw.text((SIDE_PAD + 11, 26), 'TQ', font=_font(14, bold=True), fill=GOLD)
    draw.text((SIDE_PAD + 46, 14), "FiFi's TQE", font=f_title, fill=GOLD)
    draw.text((SIDE_PAD + 47, 50), 'Daily Trade Recap', font=f_sub, fill=TAN)
    draw.text((W - 160, 14), 'DATE', font=f_date_l, fill=TAN)
    try:
        from datetime import datetime
        d = datetime.strptime(trade_date, '%Y-%m-%d')
        date_str = d.strftime('%a, %b %-d, %Y')
    except Exception:
        date_str = trade_date
    draw.text((W - 160, 28), date_str, font=f_date, fill=WHITE)
    y = HEADER_H
    draw.line([(0, y), (W, y)], fill=BORDER, width=2)
    y += 10

    # Hero box
    hx0, hx1 = SIDE_PAD, W - SIDE_PAD
    draw.rounded_rectangle([(hx0, y), (hx1, y + HERO_H)], radius=6, fill=HERO_BG, outline=BORDER, width=2)
    draw.text((hx0 + 12, y + 8), 'TRADE OF THE DAY', font=f_hero_l, fill=TAN)
    if best_trade:
        tk = '$' + (best_trade.get('ticker') or 'N/A').upper()
        an = DISPLAY_NAMES.get(best_trade.get('analyst',''), best_trade.get('analyst','').capitalize())
        try:
            pct_str = ('+' if best_pct >= 0 else '') + f'{best_pct:.0f}%'
        except Exception:
            pct_str = ''
        pct_color = GREEN if best_pct >= 0 else RED
        draw.text((hx0 + 36, y + 22), tk, font=f_hero_t, fill=GOLD)
        pw = int(f_hero_p.getlength(pct_str))
        draw.text((hx1 - pw - 14, y + 28), pct_str, font=f_hero_p, fill=pct_color)
        draw.text((hx0 + 38, y + 66), an, font=f_hero_u, fill=GREY)
    else:
        draw.text((hx0 + 12, y + 35), 'No trades today', font=f_aname, fill=GREY)
    y += HERO_H + 16

    # Analyst card helper
    def draw_card(analyst, y_start):
        trades_list = by_analyst.get(analyst, [])
        rows = max(len(trades_list), 1)
        ch = ANALYST_HEADER_H + rows * ROW_H + CARD_PAD
        cx0, cx1 = SIDE_PAD, W - SIDE_PAD
        draw.rounded_rectangle([(cx0, y_start), (cx1, y_start + ch)], radius=6, fill=CARD_BG, outline=BORDER, width=1)
        display = DISPLAY_NAMES.get(analyst, analyst.capitalize())
        draw.text((cx0 + 10, y_start + 10), display, font=f_aname, fill=WHITE)
        draw.line([(cx0 + 8, y_start + ANALYST_HEADER_H - 2), (cx1 - 8, y_start + ANALYST_HEADER_H - 2)], fill=ACCENT_LINE, width=1)
        ry = y_start + ANALYST_HEADER_H
        if not trades_list:
            draw.text((cx0 + 12, ry + 8), 'No trades', font=f_ticker, fill=GREY)
        else:
            for t in trades_list:
                price   = t.get('price')
                price_s = _price_str(price)
                ticker_s = '$' + (t.get('ticker') or '---').upper()
                strike_s = t.get('strike') or ''
                expiry_s = t.get('expiry') or ''
                detail   = ticker_s
                if strike_s: detail += '  ' + strike_s
                if expiry_s: detail += '  ' + expiry_s
                status   = t.get('status', '')
                dot_color = GREEN if status == 'Closed' else RED
                dx, dy = cx0 + 14, ry + ROW_H // 2 - 5
                draw.ellipse([(dx, dy), (dx + 10, dy + 10)], fill=dot_color)
                draw.text((cx0 + 30, ry + 8), detail, font=f_ticker, fill=WHITE)
                if price_s:
                    pw2 = int(f_pct.getlength(price_s))
                    draw.text((cx1 - pw2 - 12, ry + 8), price_s, font=f_pct, fill=dot_color)
                ry += ROW_H
        return ch

    # Sections
    for sec_name, group in SECTIONS:
        _section_label(draw, y, sec_name, f_sec)
        y += SECTION_H + 4
        for analyst in group:
            ch = draw_card(analyst, y)
            y += ch + 10

    y += 6

    # Footer
    draw.line([(0, y), (W, y)], fill=ACCENT_LINE, width=1)
    y += 8
    draw.text((SIDE_PAD, y + 8), 'x.com/badgirlfifi_tqe', font=f_footer, fill=GREY)
    fr = '@Badgirlfi_trading'
    frw = int(f_footer.getlength(fr))
    draw.text((W - SIDE_PAD - frw, y + 8), fr, font=f_footer, fill=GREY)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
