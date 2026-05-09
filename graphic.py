from PIL import Image, ImageDraw, ImageFont
import io

BG          = (18, 18, 18)
ROW_BG      = (24, 24, 24)
ROW_ALT     = (20, 20, 20)
GOLD        = (212, 175, 55)
WHITE       = (255, 255, 255)
GREY        = (160, 160, 160)
DIM         = (100, 100, 100)
GREEN_BG    = (30, 90, 40)
GREEN_FG    = (72, 199, 100)
RED_BG      = (100, 28, 28)
RED_FG      = (220, 80, 80)
AMBER_BG    = (90, 65, 10)
AMBER_FG    = (212, 175, 55)
BAR_GREEN   = (72, 199, 100)
BAR_RED     = (220, 80, 80)
BAR_AMBER   = (212, 175, 55)

W           = 1400
PAD         = 48
ROW_H       = 110
HEADER_H    = 130
FOOTER_H    = 160
BAR_W       = 7


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


def _badge(draw, x, y, text, fg, bg, min_w=110):
    f = _font(22, bold=True)
    tw = draw.textlength(text, font=f)
    bw = max(tw + 28, min_w)
    bh = 40
    draw.rounded_rectangle([x, y, x + bw, y + bh], radius=8, fill=bg, outline=fg, width=2)
    draw.text((x + (bw - tw) // 2, y + 8), text, font=f, fill=fg)
    return int(bw)


def _status_colors(status):
    s = (status or '').upper()
    if 'TRIM' in s:
        return AMBER_FG, AMBER_BG
    if 'CLOSE' in s:
        return GREEN_FG, GREEN_BG
    return (160, 160, 160), (40, 40, 40)


def _pnl_colors(pnl):
    if pnl.startswith('+'):
        return GREEN_FG, GREEN_BG
    if pnl.startswith('-'):
        return RED_FG, RED_BG
    return (160, 160, 160), (40, 40, 40)


def build_graphic(data: dict, trade_of_day: dict, date_str: str) -> bytes:
    ORDER = ['fifi', 'clark', 'braamski', 'tony', 'zeph', 'vinny', 'bigmac']
    NAMES = {
        'fifi': 'FIFI', 'clark': 'CLARK', 'braamski': 'BRAAMSKI',
        'tony': 'TONY', 'zeph': 'ZEPH', 'vinny': 'VINNY', 'bigmac': 'BIGMAC',
    }

    rows = []
    for key in ORDER:
        analyst_data = data.get(key, {})
        for trade in analyst_data.get('trades', []):
            rows.append({
                'analyst': NAMES.get(key, key.upper()),
                'ticker':  trade.get('ticker', ''),
                'strike':  trade.get('strike', ''),
                'expiry':  trade.get('expiry', ''),
                'price':   trade.get('price', ''),
                'pnl':     trade.get('pnl', ''),
                'status':  trade.get('status', 'Closed'),
            })

    wins   = sum(1 for r in rows if r['pnl'].startswith('+'))
    losses = sum(1 for r in rows if r['pnl'].startswith('-'))
    total  = len(rows)
    vals = []
    for r in rows:
        try:
            vals.append(float(r['pnl'].replace('+', '').replace('%', '')))
        except Exception:
            pass
    if vals:
        avg_num = sum(vals) / len(vals)
        avg = ('+' if avg_num >= 0 else '') + f'{avg_num:.0f}%'
    else:
        avg = 'N/A'

    H = HEADER_H + len(rows) * ROW_H + FOOTER_H + 20
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Gold border lines
    draw.line([(0, 4), (W, 4)], fill=GOLD, width=4)
    draw.line([(0, H - 4), (W, H - 4)], fill=GOLD, width=4)

    # Header
    h1 = _font(58, bold=True)
    h2 = _font(28)
    title = "FiFi's TQE — Daily Trade Recap"
    tw = draw.textlength(title, font=h1)
    draw.text(((W - tw) // 2, 18), title, font=h1, fill=WHITE)
    sub = date_str + '  •  EOD Summary  •  Trimmed & Closed Only'
    sw = draw.textlength(sub, font=h2)
    draw.text(((W - sw) // 2, 84), sub, font=h2, fill=GOLD)
    draw.line([(PAD, HEADER_H + 6), (W - PAD, HEADER_H + 6)], fill=GOLD, width=2)

    # Trade rows
    for i, row in enumerate(rows):
        ry = HEADER_H + 14 + i * ROW_H
        bg_col = ROW_BG if i % 2 == 0 else ROW_ALT
        draw.rectangle([0, ry, W, ry + ROW_H], fill=bg_col)

        status_fg, _ = _status_colors(row['status'])
        draw.rectangle([0, ry + 6, BAR_W, ry + ROW_H - 6], fill=status_fg)

        af = _font(20)
        draw.text((PAD, ry + 10), row['analyst'], font=af, fill=GREY)

        tf = _font(44, bold=True)
        draw.text((PAD, ry + 34), row['ticker'], font=tf, fill=WHITE)

        detail = (row['expiry'] + ' ' + row['strike']).strip()
        df = _font(28)
        ticker_w = int(draw.textlength(row['ticker'], font=tf))
        draw.text((PAD + ticker_w + 20, ry + 50), detail, font=df, fill=GREY)

        if row.get('price'):
            raw = row['price']
            if '->' in raw:
                p = raw.split('->')
                price_str = '$' + p[0].strip() + ' → $' + p[1].strip()
            elif '→' in raw:
                p = raw.split('→')
                price_str = '$' + p[0].strip() + ' → $' + p[1].strip()
            else:
                price_str = raw
            pf2 = _font(26)
            px = W // 2 - 60
            draw.text((px, ry + 40), price_str, font=pf2, fill=GREY)

        pnl_text = row['pnl']
        st_text  = (row['status'] or 'CLOSED').upper()
        st_fg, st_bg   = _status_colors(st_text)
        pnl_fg, pnl_bg = _pnl_colors(pnl_text)

        badge_y = ry + (ROW_H - 40) // 2
        pnl_w   = max(int(draw.textlength(pnl_text, font=_font(22, bold=True))) + 28, 110)
        st_w    = max(int(draw.textlength(st_text,  font=_font(22, bold=True))) + 28, 130)

        pnl_x = W - PAD - pnl_w
        st_x  = pnl_x - st_w - 16

        _badge(draw, pnl_x, badge_y, pnl_text, pnl_fg, pnl_bg, pnl_w)
        _badge(draw, st_x,  badge_y, st_text,  st_fg,  st_bg,  st_w)

        draw.line([(PAD, ry + ROW_H - 1), (W - PAD, ry + ROW_H - 1)], fill=(40, 40, 40), width=1)

    # Footer stats
    fy = HEADER_H + 14 + len(rows) * ROW_H + 20
    draw.line([(PAD, fy - 4), (W - PAD, fy - 4)], fill=(50, 50, 50), width=1)

    avg_color = GREEN_FG if not avg.startswith('-') else RED_FG
    stats = [
        ('TRADES TODAY', str(total), WHITE),
        ('WINS',         str(wins),  GREEN_FG),
        ('LOSSES',       str(losses), RED_FG),
        ('AVG RETURN',   avg,        avg_color),
    ]
    col_w = W // len(stats)
    lf = _font(22)
    vf = _font(52, bold=True)
    for ci, (label, value, color) in enumerate(stats):
        cx = ci * col_w + col_w // 2
        lw = int(draw.textlength(label, font=lf))
        vw = int(draw.textlength(value, font=vf))
        draw.text((cx - lw // 2, fy + 10), label, font=lf, fill=GREY)
        draw.text((cx - vw // 2, fy + 40), value, font=vf, fill=color)

    cap = 'TQERecapBot  •  Auto-generated  •  Only Trimmed & Closed positions shown'
    cf = _font(20)
    cw = int(draw.textlength(cap, font=cf))
    draw.text(((W - cw) // 2, fy + 110), cap, font=cf, fill=DIM)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.read()
