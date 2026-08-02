# Nara — Liquid Galaxy Hermes Agent

**22 skills · 21 domain layers · 12 data sources · 15+ proven demos**

AI agent (Hermes profile: `liquid-galaxy-agent`) operating a 3-screen Liquid Galaxy rig.
Turns the rig into a multi-domain intelligence platform — history, maritime, energy, cyber,
economics, aviation, news, weather, conflict monitoring, and infrastructure awareness.

**Credentials:** `lg` / `lg` · **LG IP:** 192.168.1.12 · **Internal:** 10.0.2.x NAT

---

## Skill Catalog (22 skills in `skills/liquid-galaxy/`)

### Core LG Infrastructure
| Skill | What It Does |
|-------|-------------|
| `lg-ssh-control` | SSH, Earth launch/flags, KML deploy, slave sync, root formula |
| `lg-kml-tours` | KML generation, camera, card balloons, multi-shape rule |
| `lg-data-visualization` | Collector framework, dual-source fusion, 8 regions, 12 layers |
| `lg-wiki-reference` | LG Wiki mirror, screen placement, dynamic KML refs |
| `lg-user-guide` | Rig operation docs |
| `lg-use-cases` | 13 LG use-case scenarios |
| `lg-orbit-workflow` | Smooth orbit via Pi SSH |
| `lg-installation-setup` | Fresh LG install procedures |
| `lg-vm-network-setup` | NAT network topology |
| `liquid-galaxy-control` | Relaunch, shutdown, power |

### Domain Awareness Skills
| Skill | Layers | Data Sources |
|-------|--------|-------------|
| `news-storyteller` | RSS news aggregation, card balloons | BBC, Google News |
| `history-educator` | Phased history tours, parchment balloon | Research + KML |
| `geography-educator` | Educational KML + text panels | Pre-built generators |
| `armed-conflicts` | Conflict zones | ACLED, OSINT |
| `maritime-awareness` ⭐ | 5 layers — AIS, trade routes, chokepoints, tankers, cables | AISStream, NGA, TeleGeography |
| `energy-monitor` ⭐ | 5 layers — pipelines, infrastructure, shortages, renewables, mining | EIA, GIE, IEA, OWID |
| `cyber-infrastructure` ⭐ | 3 layers — outages, GPS jamming, cyber threats | Cloudflare, GPSJam, GreyNoise |
| `economic-markets` ⭐ | 5 layers — equities, macro, currencies, commodities, stress | Finnhub, FRED, Yahoo |
| `aviation-watch` ⭐ | 4 layers — military flights, delays, NOTAMs, airport status | OpenSky, ADSB-X, FAA |
| `weather-monitor` | Live weather visualization | wttr.in, NOAA |

⭐ = New skills created during this session

---

## Key Technical Discoveries

### VM Earth 7.3.3 Rules
- **NO CDATA** → silently drops entire Placemark
- **NO xmlns:gx** → silently rejected on NetworkLink KML
- **Google CDN paddle icons** only reliable icon source
- **`gx:balloonVisibility` fails** on slave_2.kml (gx namespace dropped)
- **ScreenOverlay → PNG** via Pillow = only reliable rightmost-screen pattern
- **`--no_system_check --no_signin`** mandatory for NetworkLink HTTP

### Rightmost Screen Evolution
1. `<BalloonStyle>` + `gx:balloonVisibility` → failed
2. HTML `<ScreenOverlay>` → gray box with X  
3. **ScreenOverlay → PNG (Pillow)** — proven, always visible

### Slave Sync
- `refreshInterval` needed on BOTH Solo KML AND Master KML NetworkLinks
- `##LG_PHPIFACE##` must resolve to correct internal IP
- Double-slash URLs break silently
- Each VM launches Earth as display owner

### Root Formula
```
Rightmost screen = floor(N/2) + 1   (N=3 → lg2 → slave_2.kml)
Leftmost screen  = floor(N/2) + 2   (N=3 → lg3 → slave_3.kml)
```

## Data Sources (from World Monitor — all free)
OpenSky, ADS-B Exchange, AISStream, NGA MSI, TeleGeography, Cloudflare Radar, GPSJam.org,
Finnhub, FRED, Yahoo Finance, IMF, EIA, GIE AGSI+, IEA, Our World in Data, wttr.in

## Proven Demos (15+ on rig)
Canada aviation (571 aircraft), Spain wildfires, Pune weather, Russia-Ukraine blockages,
Russian pipelines, Middle East solar, India mining, India undersea cables,
Mongol Empire, Takshashila University, Spain news, Canada news, Pune news, Global markets
