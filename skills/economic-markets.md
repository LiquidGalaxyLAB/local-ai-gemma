---
name: economic-markets
description: Monitor global financial trends on Liquid Galaxy via Finnhub and FRED APIs — stock indices, economic indicators, trade volumes mapped to regions with KML overlays and right-screen data panels.
tags: [economics, markets, finance, liquid-galaxy, data]
related_skills: [lg-use-cases, lg-data-visualization]
---

# Economic Markets

Taps into Finnhub and FRED (Federal Reserve Economic Data) to monitor financial trends, stock market fluctuations, and key economic indicators on the Liquid Galaxy.

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| **Finnhub** | Stock indices (S&P 500, FTSE, Nikkei, Sensex), forex, crypto | Free API key |
| **FRED** | GDP, inflation, unemployment, interest rates by country | Free API key |
| **World Bank API** | Trade volumes, economic indicators by region | Free, no key |

## Planned Visuals

| Indicator | KML Visualization |
|-----------|-------------------|
| Stock indices | Color-coded country markers (green=up, red=down) with % change labels |
| GDP growth | Extruded 3D columns by country height = GDP, color = growth rate |
| Inflation heat map | Country polygons colored by inflation rate (green < 3%, yellow 3-6%, red > 6%) |
| Trade flows | LineString arrows between major trading partners, width = volume |

## Screen Layout

- lg1 (center): Global economic heat map (GDP/inflation by country)
- lg2 (left): Stock market watch — index values with direction arrows
- lg3 (right): Data panel with top 10 economic indicators, key rates

## Collector (needs building)

```python
# /home/nara/wm-collector/collectors/economic_markets.py
# @register_layer('economic-markets')
# Fetches Finnhub quotes + FRED series → generates KML placemarks + polygons
```

## Deploy

```bash
cd /home/nara/wm-collector && python3 run.py --region world --layers economic-markets
```
