import io
from datetime import datetime
from playwright.sync_api import sync_playwright

DISPLAY_NAMES = {
        'fifi': 'BadGirlFiFi',
        'clark': 'clark kent',
        'braamski': 'Braamskis',
        'tony': 'TonyD',
        'zeph': 'ZephTrades',
        'vinny': 'Vinny',
        'bigmac': 'BigMac',
}

EMOJIS = {
        'fifi': '💀',
        'clark': '😤',
        'braamski': '🔱',
        'tony': '🤩',
        'zeph': '😊',
        'vinny': '🐐',
        'bigmac': '🍔',
}

FIFI_GROUP = ['fifi']
ANALYST_GROUP = ['clark', 'braamski']
TRUSTED_GROUP = ['tony', 'zeph', 'vinny', 'bigmac']

def _pnl_str(pnl_raw):
        if not pnl_raw:
                    return '', False
                s = str(pnl_raw).strip()
    try:
                val = float(s.replace('%', '').replace('+', ''))
                positive = val >= 0
except Exception:
        positive = True
    if not s.startswith(('+', '-')):
                s = '+' + s
            if not s.endswith('%'):
                        s = s + '%'
                    return s, positive

def _trade_rows(trades):
        html = ''
    for t in trades:
                ticker = t.get('ticker', '')
                strike = t.get('strike', '')
                expiry = t.get('expiry', '')
                pnl_raw = t.get('pnl') or t.get('pnl_pct') or ''
                pnl_str, positive = _pnl_str(pnl_raw)
                label = f'${ticker}'
                if strike:
                                label += f' {strike}'
                            if expiry:
                                            label += f' {expiry}'
                                        dot_color = '#4ade80' if positive else '#f87171'
        pnl_color = '#4ade80' if positive else '#f87171'
        pnl_html = f'<span style="color:{pnl_color};font-weight:700">{pnl_str}</span>' if pnl_str else ''
        html += f'''
                <div class="trade-row">
                            <div style="display:flex;align-items:center;gap:10px">
                                            <div style="width:10px;height:10px;border-radius:50%;background:{dot_color};flex-shrink:0"></div>
                                                            <span class="trade-ticker">{label}</span>
                                                                        </div>
                                                                                    {pnl_html}
                                                                                            </div>'''
    return html

def _analyst_card(analyst, trades):
        name = DISPLAY_NAMES.get(analyst, analyst)
    emoji = EMOJIS.get(analyst, '👤')
    if trades:
                rows = _trade_rows(trades)
else:
        rows = '<div class="no-trades">No trades</div>'
    return f'''
        <div class="card">
                <div class="analyst-header">
                            <span class="analyst-emoji">{emoji}</span>
                                        <span class="analyst-name">{name}</span>
                                                </div>
                                                        {rows}
                                                            </div>'''

def build_graphic(trades: list, trade_date: str) -> bytes:
        by_analyst = {}
    for t in trades:
                a = t.get('analyst', 'unknown')
        by_analyst.setdefault(a, []).append(t)

    # Best trade
    best_trade = None
    best_pct = -9999
    for t in trades:
                pnl_raw = t.get('pnl') or t.get('pnl_pct') or ''
        try:
                        pct = float(str(pnl_raw).replace('%', '').replace('+', ''))
                        if pct > best_pct:
                                            best_pct = pct
                                            best_trade = t
        except Exception:
            pass

    # Format date
    try:
                dt = datetime.strptime(trade_date, '%Y-%m-%d')
        date_display = dt.strftime('%a, %b %-d, %Y')
except Exception:
        date_display = trade_date

    # Hero section
    if best_trade:
                bt_analyst = best_trade.get('analyst', '')
        bt_ticker = best_trade.get('ticker', '')
        bt_strike = best_trade.get('strike', '')
        bt_expiry = best_trade.get('expiry', '')
        bt_pnl, _ = _pnl_str(best_trade.get('pnl') or best_trade.get('pnl_pct') or '')
        bt_name = DISPLAY_NAMES.get(bt_analyst, bt_analyst)
        bt_emoji = EMOJIS.get(bt_analyst, '👤')
        bt_label = f'${bt_ticker}'
        hero_html = f'''
                <div class="hero">
                            <div class="hero-label">TRADE OF THE DAY</div>
                                        <div class="hero-main">
                                                        <div class="hero-ticker">🎉 ${bt_ticker}</div>
                                                                        <div class="hero-pnl">{bt_pnl}</div>
                                                                                    </div>
                                                                                                <div class="hero-analyst">{bt_emoji} {bt_name}</div>
                                                                                                        </div>'''
else:
        hero_html = ''

    # Sections
    sections_html = ''
    for section_name, group in [("FIFI'S PLAYGROUND", FIFI_GROUP), ('ANALYSTS', ANALYST_GROUP), ('TRUSTED TRADERS', TRUSTED_GROUP)]:
                cards_html = ''
        for analyst in group:
                        analyst_trades = by_analyst.get(analyst, [])
                        cards_html += _analyst_card(analyst, analyst_trades)
                    sections_html += f'''
                            <div class="section-label">{section_name}</div>
                                    {cards_html}'''

    html = f'''<!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;700&display=swap');
        * {{ margin:0; padding:0; box-sizing:border-box; }}
          body {{
              background: #0f0e08;
                  font-family: 'Share Tech Mono', 'Courier New', monospace;
                      color: #e8e4d0;
                          padding: 24px;
                              width: 800px;
                                }}
                                  .wrapper {{
                                      background: #161510;
                                          border: 1px solid #b8860b44;
                                              border-radius: 12px;
                                                  padding: 28px;
                                                    }}
                                                      .header {{
                                                          display: flex;
                                                              align-items: center;
                                                                  justify-content: space-between;
                                                                      margin-bottom: 20px;
                                                                          padding-bottom: 20px;
                                                                              border-bottom: 1px solid #b8860b33;
                                                                                }}
                                                                                  .header-left {{ display:flex; align-items:center; gap:14px; }}
                                                                                    .logo {{
                                                                                        width: 52px; height: 52px;
                                                                                            background: #b8860b22;
                                                                                                border: 1px solid #b8860b66;
                                                                                                    border-radius: 8px;
                                                                                                        display: flex; align-items: center; justify-content: center;
                                                                                                            font-size: 24px;
                                                                                                              }}
                                                                                                                .brand-name {{
                                                                                                                    font-size: 22px; font-weight: 700;
                                                                                                                        color: #d4a017;
                                                                                                                            letter-spacing: 1px;
                                                                                                                              }}
                                                                                                                                .brand-sub {{ font-size: 12px; color: #8a7a50; margin-top: 2px; }}
                                                                                                                                  .header-right {{ text-align: right; }}
                                                                                                                                    .date-label {{ font-size: 10px; color: #8a7a50; letter-spacing: 2px; }}
                                                                                                                                      .date-value {{ font-size: 18px; color: #d4a017; font-weight: 700; margin-top: 4px; }}
                                                                                                                                        .hero {{
                                                                                                                                            background: #1e1b0e;
                                                                                                                                                border: 1px solid #b8860b55;
                                                                                                                                                    border-radius: 10px;
                                                                                                                                                        padding: 18px 22px;
                                                                                                                                                            margin-bottom: 24px;
                                                                                                                                                              }}
                                                                                                                                                                .hero-label {{ font-size: 10px; color: #8a7a50; letter-spacing: 3px; margin-bottom: 10px; }}
                                                                                                                                                                  .hero-main {{ display:flex; align-items:center; justify-content:space-between; }}
                                                                                                                                                                    .hero-ticker {{ font-size: 30px; font-weight: 700; color: #d4a017; }}
                                                                                                                                                                      .hero-pnl {{ font-size: 36px; font-weight: 700; color: #4ade80; }}
                                                                                                                                                                        .hero-analyst {{ font-size: 13px; color: #8a7a50; margin-top: 8px; }}
                                                                                                                                                                          .section-label {{
                                                                                                                                                                              font-size: 10px; color: #8a7a50;
                                                                                                                                                                                  letter-spacing: 3px;
                                                                                                                                                                                      margin: 20px 0 10px 0;
                                                                                                                                                                                          display: flex; align-items: center; gap: 10px;
                                                                                                                                                                                            }}
                                                                                                                                                                                              .section-label::after {{
                                                                                                                                                                                                  content: '';
                                                                                                                                                                                                      flex: 1;
                                                                                                                                                                                                          height: 1px;
                                                                                                                                                                                                              background: #b8860b33;
                                                                                                                                                                                                                }}
                                                                                                                                                                                                                  .card {{
                                                                                                                                                                                                                      background: #1a1810;
                                                                                                                                                                                                                          border: 1px solid #b8860b33;
                                                                                                                                                                                                                              border-radius: 8px;
                                                                                                                                                                                                                                  margin-bottom: 8px;
                                                                                                                                                                                                                                      overflow: hidden;
                                                                                                                                                                                                                                        }}
                                                                                                                                                                                                                                          .analyst-header {{
                                                                                                                                                                                                                                              display: flex; align-items: center; gap: 10px;
                                                                                                                                                                                                                                                  padding: 12px 16px;
                                                                                                                                                                                                                                                      border-bottom: 1px solid #b8860b22;
                                                                                                                                                                                                                                                        }}
                                                                                                                                                                                                                                                          .analyst-emoji {{ font-size: 20px; }}
                                                                                                                                                                                                                                                            .analyst-name {{ font-size: 16px; font-weight: 700; color: #d4a017; }}
                                                                                                                                                                                                                                                              .trade-row {{
                                                                                                                                                                                                                                                                  display: flex; align-items: center; justify-content: space-between;
                                                                                                                                                                                                                                                                      padding: 9px 16px;
                                                                                                                                                                                                                                                                          border-bottom: 1px solid #b8860b11;
                                                                                                                                                                                                                                                                            }}
                                                                                                                                                                                                                                                                              .trade-row:last-child {{ border-bottom: none; }}
                                                                                                                                                                                                                                                                                .trade-ticker {{ font-size: 14px; color: #c8bfa0; }}
                                                                                                                                                                                                                                                                                  .no-trades {{ padding: 10px 16px; font-size: 13px; color: #5a5040; font-style: italic; }}
                                                                                                                                                                                                                                                                                    .footer {{
                                                                                                                                                                                                                                                                                        display: flex; justify-content: space-between;
                                                                                                                                                                                                                                                                                            margin-top: 24px; padding-top: 16px;
                                                                                                                                                                                                                                                                                                border-top: 1px solid #b8860b22;
                                                                                                                                                                                                                                                                                                    font-size: 11px; color: #5a5040;
                                                                                                                                                                                                                                                                                                      }}
                                                                                                                                                                                                                                                                                                      </style>
                                                                                                                                                                                                                                                                                                      </head>
                                                                                                                                                                                                                                                                                                      <body>
                                                                                                                                                                                                                                                                                                      <div class="wrapper">
                                                                                                                                                                                                                                                                                                        <div class="header">
                                                                                                                                                                                                                                                                                                            <div class="header-left">
                                                                                                                                                                                                                                                                                                                  <div class="logo">🏆</div>
                                                                                                                                                                                                                                                                                                                        <div>
                                                                                                                                                                                                                                                                                                                                <div class="brand-name">FiFi's TQE</div>
                                                                                                                                                                                                                                                                                                                                        <div class="brand-sub">Daily Trade Recap</div>
                                                                                                                                                                                                                                                                                                                                              </div>
                                                                                                                                                                                                                                                                                                                                                  </div>
                                                                                                                                                                                                                                                                                                                                                      <div class="header-right">
                                                                                                                                                                                                                                                                                                                                                            <div class="date-label">DATE</div>
                                                                                                                                                                                                                                                                                                                                                                  <div class="date-value">{date_display}</div>
                                                                                                                                                                                                                                                                                                                                                                      </div>
                                                                                                                                                                                                                                                                                                                                                                        </div>
                                                                                                                                                                                                                                                                                                                                                                          {hero_html}
                                                                                                                                                                                                                                                                                                                                                                            {sections_html}
                                                                                                                                                                                                                                                                                                                                                                              <div class="footer">
                                                                                                                                                                                                                                                                                                                                                                                  <span>𝕏 x.com/badgirlfifi_tqe</span>
                                                                                                                                                                                                                                                                                                                                                                                      <span>▶ @Badgirlfifi_trading</span>
                                                                                                                                                                                                                                                                                                                                                                                        </div>
                                                                                                                                                                                                                                                                                                                                                                                        </div>
                                                                                                                                                                                                                                                                                                                                                                                        </body>
                                                                                                                                                                                                                                                                                                                                                                                        </html>'''

    with sync_playwright() as p:
                browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 800, 'height': 600})
        page.set_content(html, wait_until='networkidle')
        wrapper = page.query_selector('.wrapper')
        img_bytes = wrapper.screenshot()
        browser.close()

    return img_bytes
