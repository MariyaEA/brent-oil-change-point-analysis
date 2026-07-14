"""Generate deterministic dashboard screenshots from repository data.

This helper renders a static preview with the same data and visual hierarchy as
React dashboard. It is used only to commit screenshots for the project report;
the interactive application remains in dashboard/frontend.
"""

from __future__ import annotations

import json
from pathlib import Path
import html

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "dashboard"


def _svg_chart(prices: pd.DataFrame, cp_date: pd.Timestamp, event_date: pd.Timestamp) -> str:
    width, height = 900, 355
    pad_l, pad_r, pad_t, pad_b = 58, 22, 20, 42
    x0, x1 = prices["Date"].min().value, prices["Date"].max().value
    y0, y1 = prices["Price"].min(), prices["Price"].max()

    def sx(date: pd.Timestamp) -> float:
        return pad_l + (date.value - x0) / (x1 - x0) * (width - pad_l - pad_r)

    def sy(value: float) -> float:
        return pad_t + (y1 - value) / (y1 - y0) * (height - pad_t - pad_b)

    points = " ".join(f"{sx(r.Date):.1f},{sy(r.Price):.1f}" for r in prices.itertuples())
    grid = []
    labels = []
    for i in range(5):
        value = y0 + i * (y1 - y0) / 4
        y = sy(value)
        grid.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width-pad_r}" y2="{y:.1f}" class="grid"/>')
        labels.append(f'<text x="{pad_l-10}" y="{y+4:.1f}" text-anchor="end" class="axis">${value:.0f}</text>')
    for date in pd.date_range(prices["Date"].min(), prices["Date"].max(), periods=5):
        x = sx(date)
        labels.append(f'<text x="{x:.1f}" y="{height-12}" text-anchor="middle" class="axis">{date.strftime("%b %y")}</text>')

    cp_x, event_x = sx(cp_date), sx(event_date)
    return f'''<svg viewBox="0 0 {width} {height}" role="img" aria-label="Brent price chart">
      {''.join(grid)}
      <polyline points="{points}" fill="none" stroke="#8bbcff" stroke-width="2.4" stroke-linejoin="round"/>
      <line x1="{cp_x:.1f}" y1="{pad_t}" x2="{cp_x:.1f}" y2="{height-pad_b}" stroke="#f49b45" stroke-width="2.2" stroke-dasharray="7 5"/>
      <line x1="{event_x:.1f}" y1="{pad_t}" x2="{event_x:.1f}" y2="{height-pad_b}" stroke="#59d0b3" stroke-width="2" stroke-dasharray="3 5"/>
      <text x="{cp_x+8:.1f}" y="{pad_t+15}" class="cp-label">Detected shift</text>
      {''.join(labels)}
    </svg>'''


def build_html() -> str:
    prices = pd.read_csv(ROOT / "data" / "raw" / "BrentOilPrices.csv")
    # The project loader handles both source formats; this compact preview parser mirrors it.
    prices["Date"] = pd.to_datetime(prices["Date"], format="mixed")
    prices = prices.loc[prices["Date"].between("2013-01-01", "2016-12-31")].copy()
    prices = prices.iloc[::3].reset_index(drop=True)
    events = pd.read_csv(ROOT / "data" / "events" / "oil_market_events.csv")
    events["event_date"] = pd.to_datetime(events["event_date"])
    events = events.loc[events["event_date"].between("2013-01-01", "2016-12-31")]
    windows = pd.read_csv(ROOT / "reports" / "event_window_summary.csv")
    windows = windows.reindex(windows["pre_to_post_change_pct"].abs().sort_values(ascending=False).index).head(6)
    model = json.loads((ROOT / "reports" / "model" / "change_point_results.json").read_text())

    cp_date = pd.Timestamp(model["change_point_date"])
    event_date = pd.Timestamp(model["nearest_event"]["event_date"])
    chart = _svg_chart(prices, cp_date, event_date)

    event_rows = "".join(
        f'''<div class="event-row"><span class="dot"></span><time>{row.event_date.strftime('%b %Y')}</time><div><strong>{html.escape(row.event_name)}</strong><small>{html.escape(row.category)} · {html.escape(row.hypothesized_short_term_pressure)}</small></div><b>↗</b></div>'''
        for row in events.itertuples()
    )
    table_rows = "".join(
        f'''<tr><td><strong>{html.escape(row.event_name)}</strong><small>{row.event_date}</small></td><td>{html.escape(row.category)}</td><td class="{'neg' if row.pre_to_post_change_pct < 0 else 'pos'}">{row.pre_to_post_change_pct:+.1f}%</td></tr>'''
        for row in windows.itertuples()
    )

    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box}} body{{margin:0;background:#07111f;color:#ecf3ff;font-family:Arial,sans-serif;background-image:radial-gradient(circle at 82% 0,#12365a 0,transparent 34%)}} .top{{height:76px;padding:0 4vw;display:flex;align-items:center;border-bottom:1px solid #203047;background:#07111fe8}} .logo{{width:42px;height:42px;border-radius:12px;background:#59d0b3;color:#07111f;font-weight:800;display:grid;place-items:center}} .brand{{margin-left:12px}} .brand small,.kicker{{color:#59d0b3;font-size:10px;letter-spacing:.12em;text-transform:uppercase;font-weight:700}} .brand h1{{font-size:17px;margin:3px 0 0}} .status{{margin-left:auto;border:1px solid #29405b;border-radius:99px;padding:9px 14px;color:#9adfce;font-size:12px}} main{{width:92vw;max-width:1450px;margin:auto;padding:34px 0}} .hero{{padding:32px 40px;border:1px solid #24384f;border-radius:24px;background:linear-gradient(120deg,#102c49e8,#08192bee);position:relative;overflow:hidden}} .hero h2{{font-size:48px;line-height:1.08;margin:15px 0 10px;max-width:930px;letter-spacing:-.035em}} .hero p{{color:#a9b9cc;max-width:800px;line-height:1.6;font-size:14px}} .tag{{display:inline-block;border:1px solid #385578;border-radius:99px;padding:7px 12px;color:#b6d4ff;font-size:10px;text-transform:uppercase;letter-spacing:.08em}} .stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}} .card,.panel{{border:1px solid #20354d;background:#0e1e32e8;border-radius:18px}} .card{{padding:19px}} .card small{{color:#8fa4bf}} .card strong{{font-size:24px;display:block;margin:6px 0}} .card span{{color:#7186a0;font-size:10px}} .filters{{padding:20px;display:flex;gap:12px;align-items:end;margin-bottom:18px}} label{{color:#8fa4bf;font-size:10px;flex:1}} input,select{{display:block;margin-top:6px;width:100%;padding:10px;border-radius:9px;border:1px solid #2a4059;background:#081524;color:#dce9f8}} button{{padding:11px 18px;border:0;border-radius:10px;background:#59d0b3;color:#07111f;font-weight:700}} .grid2{{display:grid;grid-template-columns:2.1fr .9fr;gap:18px}} .panel{{padding:20px}} .title{{display:flex;justify-content:space-between;margin-bottom:15px}} .title h3{{font-size:20px;margin:4px 0}} .title span{{color:#738ba8}} .legend{{font-size:10px;color:#8fa4bf;margin-bottom:8px}} .legend i{{display:inline-block;width:18px;height:2px;margin:0 6px 2px 15px}} svg{{width:100%;height:auto}} .grid{{stroke:#8398b2;stroke-opacity:.15}} .axis{{fill:#71869f;font-size:10px}} .cp-label{{fill:#f49b45;font-size:10px}} .datebox{{padding:14px;border:1px solid #294865;background:#0d2840;border-radius:12px}} .datebox small,.impact small{{color:#8fa4bf;text-transform:uppercase;font-size:9px}} .datebox strong{{display:block;margin-top:5px;font-size:18px}} .impact{{margin:12px 0;padding:16px;border:1px solid #754b2b;background:#3b281f;border-radius:12px}} .impact strong{{font-size:34px;color:#ffc487;display:block;margin:5px 0}} dl div{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #20354d;font-size:10px}} dt{{color:#8fa4bf}} dd{{margin:0;text-align:right;max-width:60%}} .guard{{padding:12px;background:#102f2d;border-radius:10px;color:#9fd4c8;font-size:10px;line-height:1.5}} .lower{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}} .event-row{{display:grid;grid-template-columns:18px 62px 1fr 18px;gap:8px;align-items:center;padding:14px 5px;border-bottom:1px solid #20354d}} .event-row .dot{{width:7px;height:7px;background:#59d0b3;border-radius:50%}} .event-row time{{color:#8fa4bf;font-size:9px}} .event-row strong{{font-size:11px;display:block}} .event-row small{{color:#70859d;font-size:9px;display:block;margin-top:4px}} table{{width:100%;border-collapse:collapse;font-size:10px}} th,td{{padding:11px 6px;border-bottom:1px solid #20354d;text-align:left}} th{{color:#8fa4bf;font-size:8px;text-transform:uppercase}} td strong{{display:block}} td small{{display:block;color:#70859d;margin-top:3px}} .neg{{color:#ff9da7;font-weight:700}} .pos{{color:#77dfc6;font-weight:700}} footer{{padding:20px 4vw;border-top:1px solid #203047;color:#657b95;font-size:10px;display:flex;justify-content:space-between}}
    @media(max-width:700px){{.top{{padding:0 3vw}} .status{{font-size:0;padding:10px}} main{{width:94vw;padding-top:18px}} .hero{{padding:25px 20px}} .hero h2{{font-size:34px}} .stats{{grid-template-columns:1fr 1fr}} .filters{{display:grid;grid-template-columns:1fr 1fr}} .grid2,.lower{{grid-template-columns:1fr}} .card strong{{font-size:20px}} footer{{flex-direction:column;gap:6px}}}}
    </style></head><body>
    <header class="top"><div class="logo">BE</div><div class="brand"><small>Birhan Energies</small><h1>Brent Market Intelligence</h1></div><div class="status">● Live analysis</div></header>
    <main><section class="hero"><span class="tag">Change point analysis · 1987–2022</span><h2>See when the oil market changed—and what happened nearby.</h2><p>Explore Brent price regimes, Bayesian model output, and researched geopolitical, OPEC, sanctions, and economic events. Date alignment is presented as evidence for investigation, not proof of causality.</p></section>
    <section class="stats"><div class="card"><small>Daily observations</small><strong>9,011</strong><span>20 May 1987 to 14 Nov 2022</span></div><div class="card"><small>Modeled level shift</small><strong>{model['percent_change']:.1f}%</strong><span>2014 event-centered window</span></div><div class="card"><small>Maximum R-hat</small><strong>{model['maximum_r_hat']:.4f}</strong><span>Convergence close to 1.00</span></div><div class="card"><small>Average historical price</small><strong>$48.42</strong><span>Nominal USD per barrel</span></div></section>
    <section class="filters panel"><label>Start date<input value="2013-01-01"></label><label>End date<input value="2016-12-31"></label><label>Resolution<select><option>Daily</option></select></label><label>Event category<select><option>All categories</option></select></label><button>Apply filters</button></section>
    <section class="grid2"><div class="panel"><div class="title"><div><span class="kicker">Historical prices and event overlay</span><h3>Brent price regimes</h3></div><span>↗</span></div><div class="legend"><i style="background:#8bbcff;margin-left:0"></i>Brent price<i style="background:#f49b45"></i>Bayesian change point<i style="background:#59d0b3"></i>Researched event</div>{chart}</div>
    <div class="panel"><div class="title"><div><span class="kicker">Bayesian model output</span><h3>Detected structural break</h3></div><span>✓</span></div><div class="datebox"><small>Posterior median</small><strong>1 December 2014</strong></div><div class="impact"><small>Estimated mean-price shift</small><strong>{model['percent_change']:.1f}%</strong><span>${model['mu_before_mean']:.2f} → ${model['mu_after_mean']:.2f} per barrel</span></div><dl><div><dt>94% date interval</dt><dd>{model['change_point_date_hdi_low']} – {model['change_point_date_hdi_high']}</dd></div><div><dt>Maximum R-hat</dt><dd>{model['maximum_r_hat']:.4f}</dd></div><div><dt>Nearest event</dt><dd>{html.escape(model['nearest_event']['event_name'])}</dd></div><div><dt>Calendar distance</dt><dd>{abs(model['nearest_event']['distance_days'])} days</dd></div></dl><div class="guard">Temporal proximity supports an event-association hypothesis; it does not establish that the event caused the structural break.</div></div></section>
    <section class="lower"><div class="panel"><div class="title"><div><span class="kicker">Research catalogue</span><h3>Events in the selected period</h3></div><span>◎</span></div>{event_rows}</div><div class="panel"><div class="title"><div><span class="kicker">Descriptive association only</span><h3>Largest event-window movements</h3></div><span>▥</span></div><table><thead><tr><th>Event</th><th>Category</th><th>5-day move</th></tr></thead><tbody>{table_rows}</tbody></table></div></section></main><footer><span>Birhan Energies · Decision intelligence prototype</span><span>Analysis by Mariamawit Ewnetu Alemu</span></footer>
    </body></html>'''


def main() -> None:
    from playwright.sync_api import sync_playwright

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    page_html = build_html()
    (OUT_DIR / "dashboard_preview.html").write_text(page_html, encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        desktop = browser.new_page(viewport={"width": 1440, "height": 1100})
        desktop.set_content(page_html, wait_until="load")
        desktop.screenshot(path=str(OUT_DIR / "dashboard_desktop.png"), full_page=True)

        mobile = browser.new_page(viewport={"width": 430, "height": 1000})
        mobile.set_content(page_html, wait_until="load")
        mobile.screenshot(path=str(OUT_DIR / "dashboard_mobile.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
