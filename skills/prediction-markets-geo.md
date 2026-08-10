---
name: prediction-markets-geo
description: Maps Polymarket prediction probabilities onto the physical globe as pulsing geo-forecast rings — what the world's money thinks will happen, rendered as a landscape of implied probability the camera flies through.
version: 1.0.0
tags: [prediction-markets, polymarket, probability, geo-forecast, liquid-galaxy, rings]
related_skills: [economic-markets, armed-conflicts, country-instability-index]
---

# Prediction Markets Geo-Forecast

Turns the LG rig into a global consensus forecast display. Active Polymarket prediction markets on geopolitical and economic events are geolocated to the relevant country or region, and each market's implied probability is rendered as a pulsing probability ring — brighter and faster as probability approaches 50/50 (maximum uncertainty), solid and slow near 0% or 100% (consensus). The camera flies between high-stakes markets while the right-screen balloon explains what's being priced in and how the probability has moved.

**This is not a financial dashboard** — economic-markets already covers stocks, currencies, GDP, and commodities. This is an ambient forecast layer: what do millions of dollars in aggregate bets say about the likelihood of a ceasefire, a rate cut, an election outcome, a border closure? The markets become a distributed sensor network, and the globe becomes the display.

## Why Distinct From the 12 Existing Skills

Economic-markets tracks *what happened* (index levels, inflation prints, GDP releases). Prediction-markets-geo tracks *what people think will happen next* (implied probability of future events). These are fundamentally different signal types. A country can have healthy GDP (low economic-markets stress) while Polymarket gives its leader a 65% chance of being deposed — the two skills disagree by design, and showing both side by side on the LG rig is exactly the kind of cross-stream tension World Monitor's convergence detection was built to surface.

## Trigger Phrases

- "what are prediction markets saying right now" / "show me Polymarket on the globe"
- "where is the world's money betting on conflict" / "geo-forecast on the rig"
- "what are markets pricing in for Ukraine" / "show me the probability landscape"
- "which countries have the most active prediction markets" / "consensus forecast view"

## Data Source

| Source | URL | Auth | Notes |
|--------|-----|------|-------|
| Polymarket CLOB API | `clob.polymarket.com/markets` | **None** (free, no key) | Returns all markets; filter by `active=true`, tags containing geopolitics/politics tags |
| Polymarket Gamma API | `gamma-api.polymarket.com/events` | **None** (free, no key) | Alternative endpoint with better categorization |

**Verified:** `clob.polymarket.com/markets` returns 1000+ markets with question text, token prices (implied probabilities), tags, and volume data. Filtering is done client-side — fetch the full list, filter to geopolitics-relevant tags, geolocate by keyword matching country/leader/region names in the question text.

**Tag filter keywords:** Politics, Elections, conflict, war, sanction, rate cut, central bank, ceasefire, regime, coup, border, invasion, missile, nuclear, OPEC, trade war, tariff, sanction, EU, NATO, UN, BRICS.

**Country resolution:** keyword match question text against a country alias map (same approach as armed-conflicts skill — "Russia" / "Ukraine" / "Iran" / "China" / "Taiwan" / "Israel" / "Gaza" / "North Korea" / "India" / "Pakistan" etc.). Markets that match multiple countries get placed at the midpoint between them.

## KML Generation — Layer by Layer

### Core Layer: Probability Rings

Each market becomes a set of 3 concentric circles centered on the relevant country or region:

- **Ring radius:** 300 km (inner), 500 km (middle), 700 km (outer) — scaled by market 24h volume (higher volume = larger rings, normalized to 1.0–2.0×)
- **Ring color:** 
  - High uncertainty (probability 40–60%) → bright amber `#ffaa00`, fast pulse (2s cycle)
  - Moderate certainty (20–40% or 60–80%) → electric blue `#4488ff`, medium pulse (4s cycle)
  - Consensus (0–20% or 80–100%) → cool white `#ccccff`, slow pulse (6s cycle)
- **Ring opacity:** outer ring 20%, middle 35%, inner 50% — fading outward gives a sonar-ping effect
- **Altitude:** 15–25 km above the country (rings float above terrain so they're visible from global zoom)

The pulsing is achieved by generating 3 KML states at different opacity levels and cycling them via NetworkLink refresh (3s cycle = each state gets one refresh tick, creating a 9-second full pulse cycle for high-uncertainty markets).

```xml
<Style id="ring_amber_inner">
  <LineStyle><color>ffaa00ff</color><width>3</width></LineStyle>
  <PolyStyle><color>00ffaa00</color><fill>0</fill></PolyStyle>
</Style>
```

### Marker Layer: Country-Level Aggregate Dots

Each country with active markets gets a single aggregate marker at the country centroid:

- **Color:** warm gold `#ffcc00` — distinct from the red/orange of conflict skills and the green/blue of economic skills
- **Size:** number of active markets mapped to icon scale (1–5 markets = 0.8, 6–10 = 1.2, 11+ = 1.6)
- **Icon:** paddle icon — consistent with LG VM rules
- **Label:** "🇮🇷 7 markets · avg 54% uncertainty" — flag + count + average probability

### Text Label Layer

1-line labels at icon_offset for the top 10 markets by volume. Format: "60% — Iran strikes ceasefire by 2026" (probability + truncated question). Scale 1.8, white, placed at [lon+2.0, lat+0.5] offset.

## Camera Design

The camera treats probability as geography — flying from high-uncertainty to high-uncertainty market like a pilot navigating by signal strength:

1. **Opening:** Global altitude (~10,000 km), all rings visible. The viewer sees clusters of amber (uncertainty hot zones) amid cooler white rings (consensus). Hold 8 seconds.

2. **Uncertainty fly-down sequence:** Camera descends to the top 6 high-uncertainty markets (probability closest to 50%) in descending volume order:
   - Fly to each location at 800 km range, 50° tilt
   - Dwell 6 seconds — amber rings pulse in the foreground
   - Right-screen panel updates with market question, current probability, 7-day probability chart, volume, and "What This Means" context line
   - No TTS on individual markets (too many short stops) — instead, right-screen text carries the explanation
   
3. **Consensus contrast pass:** Camera flies to 3 high-consensus markets (probability > 90% or < 10%) — these are interesting in a different way: "the market is nearly certain." Dwell 4 seconds each, showing white slow-pulse rings.

4. **Final pull-back:** Global altitude, all rings visible. Hold 5 seconds.

Total tour: ~100 seconds.

## Right-Screen Balloon Design

Visual identity: **trading terminal aesthetic** — distinct from every other skill:

- **Background:** Charcoal `#1a1a2e` with a thin amber `#ffaa00` border (2px). The amber border is the key differentiator — no other skill uses it.
- **Header:** "PREDICTION MARKETS — Geo-Forecast" in monospace amber font, right-aligned. UTC timestamp below.
- **Body — market detail card layout:**
  - Question text (large, white, 2–3 lines max)
  - Probability bar: horizontal bar, amber fill proportional to probability, labeled "63% Yes" at the current fill point
  - 7-day trend: small inline sparkline showing probability movement over the past week (Pillow line-drawing on the PNG)
  - 24h volume: "$2.4M in positions"
  - Geopolitical context: 1-line "What this means" — e.g., "Markets see 63% chance of ceasefire holding through Q1 2027"
- **Footer:** "Data: Polymarket CLOB API · Markets with <$50k 24h vol excluded · Implied probability from last trade price"

Generated as PNG via Pillow (`gen_polymarket_panel.py`), deployed to rightmost screen.

## What Nara Says Back

> "Prediction markets geo-forecast deployed. I'm tracking 34 active geopolitical markets across 18 countries. The highest uncertainty cluster is around Iran — 7 markets averaging 54% implied probability, with $12M in aggregate positions. The Middle East and Taiwan Strait are showing the most amber rings. The camera is flying to the top uncertainty zones now."

## The One Rule

**The market is not the oracle — it's a sensor.** The probability rings do not predict the future; they measure what informed money currently believes. The skill's job is to show where the world's aggregate judgment is uncertain (amber, fast-pulsing) versus where it has reached consensus (white, slow-pulsing), and let the viewer draw their own conclusions. Never present a Polymarket probability as a fact about what will happen — always frame it as "markets currently price X at Y%."

## Files

| File | Purpose |
|------|---------|
| `/home/nara/wm-collector/collectors/prediction_markets.py` | Main script — fetches Polymarket CLOB API, filters geopolitics markets, geolocates, builds KML, deploys, runs camera tour |
| `/home/nara/wm-collector/gen_polymarket_panel.py` | Right-screen PNG panel generator (Pillow, amber theme) |
| `references/prediction-markets-geo/country-alias-map.json` | Country name → aliases + centroid for geolocation |

## Manual Run

```bash
cd /home/nara/wm-collector && python3 collectors/prediction_markets.py
```

## Cron (Auto-Refresh)

```bash
cronjob action=create name=prediction-markets schedule=2h \
  prompt="cd /home/nara/wm-collector && python3 collectors/prediction_markets.py" \
  skills=prediction-markets-geo
```
