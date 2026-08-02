# Fusion Engine Reference

## Overview

`fusion.py` is the data fusion module that sits between collectors and KML
generation. It takes raw features from primary + secondary sources, deduplicates
by proximity, tags each feature with a confidence level, and returns a clean
merged list plus data quality notes for the right-screen info panel.

## FusionPolicy

```python
@dataclass
class FusionPolicy:
    mode: str = 'union_dedup'       # 'union_dedup' | 'primary_fallback'
    dedup_km: float = 55.0          # Haversine radius for dedup
    primary_label: str = 'Primary'
    secondary_label: str = 'Secondary'
    layer_display: str = 'Layer'
```

## DataQualityNote

```python
@dataclass
class DataQualityNote:
    layer: str                     # 'Earthquakes', 'Weather', etc.
    status: str                    # 'verified' | 'single_source' | 'approximate' | 'unavailable'
    primary_source: str = ''
    secondary_source: str = ''
    total_features: int = 0
    verified_count: int = 0
    single_source_count: int = 0
    approximate_count: int = 0
    message: str = ''
```

## FusionResult

```python
@dataclass
class FusionResult:
    features: list[GeoFeature]      # Clean merged features
    notes: list[DataQualityNote]    # Quality info for right screen
    comparison: Optional[SourceComparison] = None
```

## Layer Fusion Policies (in `fusion.py`)

```python
LAYER_FUSION_POLICIES = {
    'earthquakes': FusionPolicy(
        mode='union_dedup',
        primary_label='USGS', secondary_label='EMSC',
        layer_display='Earthquakes',
    ),
    'weather': FusionPolicy(
        mode='primary_fallback',
        primary_label='NOAA NWS', secondary_label='wttr.in / WMO',
        layer_display='Weather',
    ),
    'disasters': FusionPolicy(
        mode='union_dedup',
        primary_label='GDACS', secondary_label='Wikipedia',
        layer_display='Disasters',
    ),
}
```

## Adding a New Fusion Policy

When adding a new layer with dual sources:

1. Add the policy to `LAYER_FUSION_POLICIES` in `fusion.py`
2. Choose `union_dedup` if both sources report the same kind of events
   (earthquakes from USGS and EMSC).
3. Choose `primary_fallback` if one source is authoritative and the other
   is a global fallback (NOAA NWS → wttr.in).

## Status Determination Logic

```
overlap > 0, s_only == 0     → 'verified' — sources agree
overlap > 0, s_only > 0      → 'approximate' — mixed
primary > 0, secondary == 0  → 'single_source' — only primary
primary == 0, secondary > 0  → 'single_source' — only secondary
p_only > 0, s_only > 0, overlap == 0 → 'approximate' — no overlap
else                          → 'unavailable'
```

## Right-Screen Encoding

The `generate_news_kml()` function in `run.py` renders quality notes above
news headlines:

| Status | Color | Icon |
|--------|-------|------|
| verified | Green (`ff00ff00`) | ✅ |
| approximate / single_source | Yellow (`ff00ccff`) | ⚠️ |
| anything else | Blue (`ff88aacc`) | ℹ️ |

## Confidence Encoding in master.kml

The KML generator (`kml/generator.py`) modulates icon scale by confidence:

```python
dq_scale = 1.0 if dq == 'verified' else 0.8 if dq == 'single_source' else 0.6
final_scale = max(0.3, min(2.0, feature.scale * dq_scale))
```

- verified = full size
- single_source = 80% of normal size
- approximate = 60% of normal size
