---
name: live-aviation
description: Live Aviation Watch — 100 aircraft with heading-rotated icons at actual altitude on Liquid Galaxy. Uses OpenSky Network ADS-B data. Focus on major flight corridors.
tags: [liquid-galaxy, aviation, flights, air-traffic]
---

# Live Aviation Watch

Tracks live aircraft globally via OpenSky Network ADS-B transponder data. 100 aircraft displayed with heading-rotated icons at actual flight altitude.

## Data Source

| Layer | Source | Type |
|-------|--------|------|
| Air Traffic | OpenSky Network | Live (5 min refresh) |
| Airports | Static config (35 major) | Static |

## Deploy

```bash
cd /home/nara/wm-collector && python3 run.py --region europe --layers air-traffic --single-source --data-only
```

## Regions

| Region | Command |
|--------|---------|
| Europe | `--region europe` |
| Middle East | `--region middle-east` |
| World | `--region world` |

## What You See

- ✈️ 100 aircraft with icons rotated by heading direction
- 📏 Aircraft at actual altitude (relativeToGround)
- 🏗 Major airports as reference points
- Right-screen panel with key airports + corridor info + TTS
