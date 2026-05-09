from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

BG       = (15, 14, 8)
CARD_BG  = (26, 24, 16)
HERO_BG  = (30, 27, 14)
BORDER   = (184, 134, 11)
GOLD     = (212, 160, 23)
MUTED    = (138, 122, 80)
LIGHT    = (200, 191, 160)
GREEN    = (74, 222, 128)
RED      = (248, 113, 113)
DIVIDER  = (40, 36, 20)

DISPLAY_NAMES = {
            'fifi': 'BadGirlFiFi', 'clark': 'clark kent',
            'braamski': 'Braamskis', 'tony': 'TonyD',
            'zeph': 'ZephTrades', 'vinny': 'Vinny', 'bigmac': 'BigMac',
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
                            try: return ImageFont.truetype(p, size)
                                            except: pass
                                                        return ImageFont.load_default()

        def _pnl(raw):
                    if not raw: return '', None
                                s = str(raw).strip()
    try:
                    val = float(s.replace('%','').replace('+',''))
        color = GREEN if val >= 0 else RED
    except: color = MUTED
    if not s.startswith(('+','-')): s = '+' + s
                if not s.endswith('%'): s += '%'
                            return s, color

def _rr(draw, x, y, w, h, r, fill, outline=None, ow=1):
            draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=ow)

def _card_h(trades):
            return ANALYST_H + max(len(trades),1)*ROW_H + 2

def build_graphic(trades: list, trade_date: str) -> bytes:
            by_analyst = {}
    for t in trades:
                    by_analyst.setdefault(t.get('analyst','unknown'), []).append(t)

    best_trade = None; best_pct = -9999
    for t in trades:
                    raw = t.get('pnl') or t.get('pnl_pct') or ''
        try:
                            pct = float(str(raw).replace('%','').replace('+',''))
                            if pct > best_pct: best_pct = pct; best_trade = t
                                            except: pass

    try: date_str = datetime.strptime(trade_date,'%Y-%m-%d').strftime('%a, %b %-d, %Y')
                except: date_str = trade_date

    total_h = PAD + HEADER_H + PAD
    if best_trade: total_h += HERO_H + PAD
                for g in [FIFI_GROUP, ANALYST_GROUP, TRUSTED_GROUP]:
                                total_h += SECTION_H + 6
                                for a in g: total_h += _card_h(by_analyst.get(a,[])) + 8
                                            total_h += PAD + FOOTER_H + PAD

    img = Image.new('RGB', (W, total_h), BG)
    draw = ImageDraw.Draw(img)

    fb = _font(22, True); fs = _font(12); fdl = _font(10); fd = _font(17, True)
    fsec = _font(10); fhl = _font(10); fht = _font(28, True); fhp = _font(34, True)
    fha = _font(12); fan = _font(15, True); ftk = _font(14); fpn = _font(14, True)

    y = PAD
    _rr(draw, PAD, y, 52, 52, 8, (40,34,14), BORDER)
    draw.text((PAD+6, y+14), 'TQ', font=fb, fill=GOLD)
    draw.text((PAD+62, y+6), "FiFi's TQE", font=fb, fill=GOLD)
    draw.text((PAD+62, y+32), 'Daily Trade Recap', font=fs, fill=MUTED)
    draw.text((W-PAD-180, y+4), 'DATE', font=fdl, fill=MUTED)
    draw.text((W-PAD-180, y+18), date_str, font=fd, fill=GOLD)
    y += HEADER_H
    draw.line([(PAD,y),(W-PAD,y)], fill=BORDER, width=1)
    y += PAD

    if best_trade:
                    tk = best_trade.get('ticker',''); sk = best_trade.get('strike',''); ex = best_trade.get('expiry','')
        ps, pc = _pnl(best_trade.get('pnl') or best_trade.get('pnl_pct') or '')
        bn = DISPLAY_NAMES.get(best_trade.get('analyst',''), best_trade.get('analyst',''))
        lbl = f'${tk}' + (f' {sk}' if sk else '') + (f' {ex}' if ex else '')
        _rr(draw, PAD, y, W-2*PAD, HERO_H, RADIUS, HERO_BG, BORDER)
        draw.text((PAD+16, y+10), 'TRADE OF THE DAY', font=fhl, fill=MUTED)
        draw.text((PAD+16, y+26), f'* {lbl}', font=fht, fill=GOLD)
        if ps:
                            pw = int(draw.textlength(ps, font=fhp))
            draw.text((W-PAD-16-pw, y+22), ps, font=fhp, fill=pc or GREEN)
        draw.text((PAD+16, y+68), f'>> {bn}', font=fha, fill=MUTED)
        y += HERO_H + PAD

    for sec_name, group in [("FIFI'S PLAYGROUND",FIFI_GROUP),('ANALYSTS',ANALYST_GROUP),('TRUSTED TRADERS',TRUSTED_GROUP)]:
                    draw.text((PAD, y+8), sec_name, font=fsec, fill=MUTED)
        sw = int(draw.textlength(sec_name, font=fsec))
        draw.line([(PAD+sw+10,y+14),(W-PAD,y+14)], fill=DIVIDER, width=1)
        y += SECTION_H + 6

        for analyst in group:
                            at = by_analyst.get(analyst, [])
            ch = _card_h(at)
            nm = DISPLAY_NAMES.get(analyst, analyst)
            _rr(draw, PAD, y, W-2*PAD, ch, RADIUS, CARD_BG, BORDER)
            draw.text((PAD+CARD_PAD, y+12), nm, font=fan, fill=GOLD)
            draw.line([(PAD,y+ANALYST_H),(PAD+W-2*PAD,y+ANALYST_H)], fill=DIVIDER, width=1)
            if not at:
                                    draw.text((PAD+CARD_PAD, y+ANALYST_H+10), 'No trades', font=ftk, fill=MUTED)
            else:
                for i, t in enumerate(at):
                                            ry = y + ANALYST_H + i*ROW_H
                                            tk = t.get('ticker',''); sk = t.get('strike',''); ex = t.get('expiry','')
                                            pr, pc = _pnl(t.get('pnl') or t.get('pnl_pct') or '')
                                            lbl = f'${tk}' + (f' {sk}' if sk else '') + (f' {ex}' if ex else '')
                                            dc = GREEN if pc==GREEN else RED if pc==RED else MUTED
                                            draw.ellipse([PAD+CARD_PAD, ry+13, PAD+CARD_PAD+10, ry+23], fill=dc)
                                            draw.text((PAD+CARD_PAD+18, ry+10), lbl, font=ftk, fill=LIGHT)
                                            if pr:
                                                                            pw = int(draw.textlength(pr, font=fpn))
                                                                            draw.text((W-PAD-CARD_PAD-pw, ry+10), pr, font=fpn, fill=pc)
                                                                        if i < len(at)-1:
                                                                                                        draw.line([(PAD+CARD_PAD,ry+ROW_H),(W-PAD-CARD_PAD,ry+ROW_H)], fill=DIVIDER, width=1)
                                                                                            y += ch + 8

    y += PAD
    draw.line([(PAD,y),(W-PAD,y)], fill=DIVIDER, width=1)
    y += 10
    draw.text((PAD, y), 'x.com/badgirlfifi_tqe', font=fsec, fill=MUTED)
    rt = '@Badgirlfifi_trading'
    draw.text((W-PAD-int(draw.textlength(rt,font=fsec)), y), rt, font=fsec, fill=MUTED)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
