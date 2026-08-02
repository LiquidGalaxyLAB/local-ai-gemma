# Ships & Maritime — Middle East / Gulf Data

Added July 2026. These coordinates are geofiltered by region bounding box — they only appear when running `--region middle-east` (or a region that contains them).

## Strait of Hormuz Chokepoints

| Name | Lat | Lon | Description |
|------|-----|-----|-------------|
| Strait of Hormuz (West) | 26.500 | 56.000 | Persian Gulf → Gulf of Oman — 21% of global oil |
| Strait of Hormuz (East) | 26.000 | 56.500 | Gulf of Oman approach |
| Strait of Hormuz (North) | 27.000 | 56.000 | Iranian side — Bandar Abbas approach |

## Gulf Ports

| Name | Lat | Lon | Country |
|------|-----|-----|---------|
| Bandar Abbas Port | 27.183 | 56.267 | Iran |
| Ras Tanura (Saudi Aramco) | 26.667 | 50.167 | Saudi Arabia |
| Khor Fakkan Port | 25.000 | 56.367 | UAE |
| Jebel Ali Port | 25.017 | 55.067 | UAE |
| Doha Port | 25.283 | 51.533 | Qatar |
| Shuwaikh Port | 29.350 | 47.917 | Kuwait |
| Salalah Port | 16.933 | 54.017 | Oman |
| Fujairah Port | 25.117 | 56.333 | UAE |

## Middle East Naval Bases

| Name | Lat | Lon | Country |
|------|-----|-----|---------|
| Bandar Abbas Naval Base | 27.150 | 56.200 | Iran |
| Naval Support Activity Bahrain | 26.200 | 50.600 | US/5th Fleet |
| Juffair Naval Base | 26.217 | 50.617 | Bahrain |
| Al Qusah - Ras Al Khair | 27.433 | 49.467 | Saudi Arabia |
| Duqm Naval Base | 19.650 | 57.683 | Oman |

## Usage

```bash
cd /home/nara/wm-collector
python3 run.py --region middle-east --layers ships --single-source --data-only
```
