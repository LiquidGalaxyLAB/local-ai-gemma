---
name: economic-markets
description: "Monitor global financial trends on Liquid Galaxy via Finnhub, FRED, and Yahoo Finance."
version: 2.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [markets, finance, economics, gdp, stock, currency, kml, liquid-galaxy]
    related_skills: [energy-monitor, lg-data-visualization, lg-kml-tours]
---

# Economic Markets Monitor

Turns the LG rig into a global trading floor and macroeconomic command center. Covers equity markets, macro indicators, currencies, commodities, and economic stress signals across 5 layers. Data that normally lives in spreadsheets and terminals gets geographic form and physical scale — inflation becomes 3D columns, market crashes look like crashes, currency flows become visible tension between nations.

**5 layers, each toggleable:** (1) Global Equity Markets, (2) Macroeconomic Indicators, (3) Currency Strength & Forex, (4) Commodity Prices, (5) Economic Stress & Crisis Signals.

**Key dependency stance:** Python + `wm-collector` framework. Free APIs (Finnhub, FRED, IMF, World Bank, Yahoo Finance, Alpha Vantage). VM-safe KML. Rightmost screen = floor(N/2)+1.

## When to Use

Trigger phrases:
- "show me global markets on the rig" / "what's the S&P doing today"
- "how is inflation looking globally" / "show me GDP by country on the rig"
- "which economies are in recession right now" / "economic watch on the rig"
- "show me currency strength globally" / "which stock markets are up today"
- "show me commodity prices on the rig" / "how is the dollar doing"
- "show me yield curves" / "which countries have the highest debt"
- "show me the Fed's latest decision" / "full markets picture"

**Extract 3 anchors:** data category / geographic scope / time horizon.

## Data Sources (from World Monitor source code — verified free)

| Source | URL | Auth | WM File |
|--------|-----|------|---------|
| Finnhub (equities/forex/commodities) | `finnhub.io/api/v1/quote` | Free API key (`FINNHUB_API_KEY`) | `scripts/seed-market-quotes.mjs` |
| FRED (macroeconomic data) | `fred.stlouisfed.org/docs/api/api_key.html` | Free API key (`FRED_API_KEY`) | `scripts/seed-fred.mjs` |
| Yahoo Finance (quotes/commodities) | `query1.finance.yahoo.com/v8/finance/chart/` | None (public) | `scripts/seed-commodity-quotes.mjs` |
| Alpha Vantage (fallback quotes) | `alphavantage.co` | Free tier | `.env.example` |
| IMF SDMX API (WEO, debt, reserves) | `portal.api.imf.org` | Free key (`IMF_API_KEY`) | `.env.example` |
| World Bank Open Data | `api.worldbank.org/v2` | None (open) | `.env.example` |
| WTO trade statistics | WTO API | Free | `.env.example` |

## How to Run

```bash
cd /home/nara/wm-collector
python3 markets_run.py --layer=equities --region=global
python3 markets_run.py --layer=macro --region=europe
python3 markets_run.py --layer=currencies
python3 markets_run.py --layer=commodities
python3 markets_run.py --layer=stress
python3 markets_run.py --layer=all              # Full economic stack
```

## Quick Reference

| Layer | Data Source | Update Cadence | Key Endpoint |
|-------|------------|----------------|--------------|
| Equity Markets | Finnhub + Yahoo Finance | 15 sec (live) | `finnhub.io/api/v1/quote` |
| Macro Indicators | FRED + World Bank + IMF | Monthly/quarterly | `fred.stlouisfed.org` |
| Currency Strength | Finnhub forex + Yahoo | 15 sec (live) | `finnhub.io/api/v1/forex` |
| Commodity Prices | Yahoo Finance futures | 15 sec (live) | `query1.finance.yahoo.com` |
| Economic Stress | Composite from all above | Computed on pull | Aggregated from all layers |

## Procedure

1. **Extract data category + scope from user request.** If "economic watch" → full 5-layer stack. If S&P query → Layer 1, global equities, zoom US. If inflation → Layer 2 with choropleth. If dollar strength → Layer 3 currencies.
2. **Build KML layers** using `markets_visuals.py`:
   - Layer 1: 3D extruded equity columns at each exchange's home country, height = index level vs 52-week range, color = today's change (deep green +1%, flashing red -3%+), width = market cap, glow-pulse on top-3 live exchanges, balloon with index/change/YTD/52wk range/top headline
   - Layer 2: macro choropleth world map (green-to-red by indicator), 3D indicator columns at capitals, US state-level sub-layer (FRED deep data), yield curve LineStrings (normal=upward green, inverted=downward red), recession hatched polygons with duration/depth/sectors/response
   - Layer 3: currency strength choropleth (blue-green=strengthening vs USD, amber-red=weakening, dark red pulse=5%+ freefall), major pair LineString connections (arrow=stronger, thickness=volume), EM volatility alert rings, PPP purchasing-power columns ($100 buys X)
   - Layer 4: commodity producer icons at top-5 producing countries (green=above 12mo avg, red=below), OPEC+ quota vs production paired columns, agricultural supply-stress polygon overlays with import-dependency arcs
   - Layer 5: sovereign debt spread polygon fills (green→red by spread vs US Treasury), banking stress flags (10%+ underperformance), capital flight arrows (currency↓ + bond yield↑ + stocks↓), NY Fed recession probability front-and-center
3. **Generate financial panel PNG** — use Pillow via `gen_markets_png.py` (dark background, gold accent bar, global indices + NIFTY sectors, sentiment footer). SCP to lg1 + sudo-cp to `/var/www/html/kml/markets_panel.png`. Write `slave_2.kml` with `<ScreenOverlay>` pointing to `http://lg1:81/kml/markets_panel.png` — anchored bottom-left, native size.
4. **Deploy** via scp to lg1 → sudo cp to master.kml + slave_2.kml + markets_panel.png. `sudo touch` all three to force ETag change. 3s refresh — **no relaunch**.
5. **Camera:** Near-global for full stack (10s — all equity columns + pins) → zoom NIFTY/India region → pull back. Total tour 60-90s.

## Layer 1 — Key Indices Tracked

| Index | Symbol | Exchange | Country |
|-------|--------|----------|---------|
| S&P 500 | SPY | NYSE | USA |
| NASDAQ | QQQ | NASDAQ | USA |
| FTSE 100 | UKX | London | UK |
| DAX | DAX | Frankfurt | Germany |
| Nikkei 225 | N225 | Tokyo | Japan |
| Hang Seng | HSI | Hong Kong | China/HK |
| Shanghai Comp | 000001.SS | Shanghai | China |
| Sensex | BSE-SENSEX | Mumbai | India |

## FRED Series — Most Useful for LG

| Series ID | Description | Cadence |
|-----------|-------------|---------|
| GDP | US GDP quarterly | Quarterly |
| CPIAUCSL | CPI all items | Monthly |
| UNRATE | Unemployment rate | Monthly |
| DGS10 | 10Y Treasury yield | Daily |
| T10Y2Y | 10Y-2Y spread (recession signal) | Daily |
| M2SL | M2 money supply | Monthly |

## Rightmost Screen — ScreenOverlay PNG Panel (THE pattern)

**Do NOT use `gx:balloonVisibility` or `<BalloonStyle>` on NetworkLink-loaded slave KMLs.** Earth 7.3.3 on VM silently drops `xmlns:gx` namespace declarations from NetworkLink-loaded KML, which means `gx:balloonVisibility` never fires and balloons never auto-open. Do NOT use HTML ScreenOverlays either — Earth renders them as a gray box with an X.

**THE pattern (verified working on this rig):**
1. Generate a dark-themed PNG panel using Pillow (example: `/home/nara/wm-collector/gen_markets_png.py`)
2. SCP it to lg1 → sudo-cp to `/var/www/html/kml/markets_panel.png`
3. Write a `slave_2.kml` with `<ScreenOverlay>` pointing to the PNG:
```xml
<ScreenOverlay>
  <Icon><href>http://lg1:81/kml/markets_panel.png</href></Icon>
  <overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>
  <screenXY x="0.02" y="0.98" xunits="fraction" yunits="fraction"/>
  <size x="0" y="0" xunits="pixels" yunits="pixels"/>
</ScreenOverlay>
```
4. `sudo touch` both files to force ETag change → 3s refresh picks it up
5. Panel renders always-visible, no click needed, no xmlns:gx required

**PNG panel specs:** 520×560px, RGBA with transparency, dark background (#0d0d0d), gold accent bar (#d4a017), DejaVu Sans fonts at 14-22pt, per-index rows with colored change indicators, NIFTY sector breakdown, sentiment footer. Update cadence: regenerate + redeploy PNG only (master.kml unchanged for static indices).

**Financial terminal (dark charcoal, thin gold border):**

```
┌──────────────────────────────────────────┐
│ ECONOMIC MARKETS MONITOR  ⏱ 14:45 UTC   │
│ ASIA ●CLOSED  EUROPE ●OPEN  US ●PRE     │
├──────────────────────────────────────────┤
│ S&P 500  5,847  +0.8%                    │
│ WTI Crude  $85.40  -1.2%                │
│ DXY       104.7  +0.3%                   │
│ US 10Y    4.28%  +4bp                    │
│ SENTIMENT: RISK-ON  🟢                   │
├──────────────────────────────────────────┤
│ 📅 14:30 USD — CPI MoM — Fcst 0.2%      │
│ 📅 16:00 EUR — ECB Rate Decision        │
│ 📅 18:00 JPY — GDP QoQ — Fcst 0.5%      │
└──────────────────────────────────────────┘
```

## The One Rule

Every number must have a place. Every place must have a number. A struggling economy must show in its columns, its polygon color, its stress indicators, and its balloon simultaneously — reinforcing the same signal across every visual channel.

## Verification

- lg2 fetches `slave_2.kml` (200) + `markets_panel.png` (200/304) every 3s — confirmed via `sudo grep markets_panel /var/log/apache2/other_vhosts_access.log`
- `curl -sI http://lg1:81/kml/markets_panel.png` returns 200 with image/png Content-Type
- Master KML has 20+ styleUrl references (pins + columns per region)
- Yahoo Finance tickers resolve correctly — test with `curl "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?range=1d"`
- Panel PNG renders as a dark card on the rightmost screen (bottom-left, 520×560px, always visible)

## Files

- `scripts/markets_visuals.py` — Economic KML generators (equity columns, macro choropleth, currency arcs, commodity pins, stress overlays)
- `scripts/markets_run.py` — CLI entry point
- `/home/nara/wm-collector/markets_today.py` — Proven deploy script (live Yahoo Finance data → master.kml pins/columns + ScreenOverlay PNG → slave_2.kml)
- `/home/nara/wm-collector/gen_markets_png.py` — Pillow-based PNG panel generator for rightmost screen (520×560px, dark theme, gold accent, global indices + NIFTY sector breakdown)
- `/home/nara/wm-collector/collectors/markets_*.py` — Per-layer collectors
- Related: `energy-monitor` (commodities overlap — coordinate), `lg-data-visualization` (framework)
- `/home/nara/wm-collector/collectors/markets_*.py` — Per-layer collectors
- Related: `energy-monitor` (commodities overlap — coordinate), `lg-data-visualization` (framework), `lg-ssh-control` (KML deploy pattern, multi-VM NAT slave sync)

## How to get free API keys

| Source | Registration | Free Tier |
|--------|-------------|-----------|
| Finnhub | `finnhub.io` | 60 req/min |
| FRED | `fred.stlouisfed.org/docs/api/api_key.html` | 120 req/min |
| Alpha Vantage | `alphavantage.co` | 25 req/day |
| IMF | `portal.api.imf.org` | Unlimited |
| World Bank | No key needed | Open API |
| Yahoo Finance | No key needed | Public |
