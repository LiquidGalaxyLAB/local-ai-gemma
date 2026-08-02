# Dual-Source Comparison — Reference

## Architecture

Every live-data layer collects from TWO independent APIs. The framework
compares results using proximity matching and injects a disclaimer into
the KML when sources diverge.

```
Primary API  ──► fetch(region) ──┐
                                 ├──► compare_layers() ──► KML + disclaimer (if needed)
Secondary API ──► fetch(region) ──┘
```

## Source Pairings

| Layer | Primary | Secondary | Why This Pair |
|-------|---------|-----------|---------------|
| earthquakes | USGS GeoJSON | EMSC seismicportal.eu | USGS has better global coverage; EMSC catches smaller/faster European/Med events |
| weather | NOAA NWS | wttr.in / WMO | NWS is US-only; wttr.in is global with WMO weather codes |
| disasters | GDACS JSON | Wikipedia Current Events | GDACS can be stale/rate-limited; Wikipedia editors report disasters in real time |

## Proximity Matching Algorithm

```python
def compare_layers(primary, secondary):
    MATCH_DEGREES = 0.5  # ≈55km at equator
    for pi, pf in enumerate(primary):
        for si, sf in enumerate(secondary):
            dlat = abs(pf.lat - sf.lat)
            dlon = abs(pf.lon - sf.lon)
            if dlat < MATCH_DEGREES and dlon < MATCH_DEGREES:
                # Match found
```

Threshold was chosen empirically: USGS and EMSC frequently place the same
earthquake 0.1-0.3° apart. 0.5° catches real matches while distinguishing
separate events in different cities/provinces.

## Status Levels

| Status | Criterion | Meaning |
|--------|-----------|---------|
| good | Overlap ≥ 80% of secondary | Sources agree — clean display |
| partial | Overlap 50-80% | Some variance — disclaimer injected |
| mismatch | Overlap < 50% | Significant divergence — strong disclaimer |
| no-secondary | v2 returned 0 items | Only primary available — logged |

## KML Disclaimer Output

When sources diverge, the generator creates:

1. A `<Style id="s_disclaimer">` with a caution.png icon (yellow, scale 1.6)
2. A `<Folder name="⚠ Data Accuracy">` containing a single Placemark:
   - Name: "⚠ Data may be approximate"
   - Description: HTML balloon listing which layers diverge
   - Footer: "Not 100% accurate — cross-reference with official channels
     for critical decisions."

The style is declared before the folder (KML requires forward declaration).

## Example Terminal Output

```
📡 Earthquakes... 7
📡 EMSC Earthquakes (v2)... 2
   🔴 7 (USGS) vs 2 (EMSC) — 0 overlap, 7 unique to primary, 2 unique to v2.
       Significant data divergence — cross-check recommended.
📡 wttr.in Weather (v2)... 1
   🔴 0 (NOAA) vs 1 (wttr.in) — weather sources diverge
```

## Adding a New v2 Collector

1. Create `collectors/<layer>_v2.py` with a class decorated with `@register_layer('<layer>-v2')`
2. Add `'<layer>': '<layer>-v2'` to `DUAL_SOURCE_MAP` in `framework.py`
3. Import the module in `run.py`
4. No other wiring needed — `run_dual_source_collection()` auto-discovers v2 via the map

## Flags

- `--single-source` — skip all v2 collection (original behavior)
- `--no-disclaimers` — keep v2 collection but suppress KML disclaimer overlay
