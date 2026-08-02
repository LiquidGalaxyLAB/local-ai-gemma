# Military Bases — Static Config Data Source

## Approach

Military bases are **static config data**, not a live API. They change slowly (years/decades), so hardcoding the list is more reliable than polling an API. Reference: World Monitor's `build-military-bases-final.mjs` pattern.

## Coverage (This Rig)

37 major strategic bases worldwide in `/home/nara/wm-collector/collectors/military_bases.py`:

**US bases (16):** Camp Humphreys (SK), Osan AB (SK), Kunsan AB (SK), Andersen AFB (Guam), Camp Foster (Okinawa), Yokota AB (Japan), Kadena AB (Okinawa), Naval Base Guam, Diego Garcia, Camp Lemonnier (Djibouti), Al Udeid AB (Qatar), NSA Bahrain, Camp Arifjan (Kuwait), Ramstein AB (Germany), Lakenheath RAF (UK), NSA Naples (Italy)

**Russian bases (7):** Hmeimim AB (Syria), Tartus Naval (Syria), Kaliningrad HQ, Sevastopol (Crimea), Severomorsk, Petropavlovsk-Kamchatsky, Vladivostok

**Chinese bases (6):** Subic Bay access (Philippines), Ream Naval (Cambodia), Hainan, Dalian, Djibouti (PLA), Woody Island (Paracels), Mischief Reef (Spratlys)

**UK/French/India (6):** RAF Akrotiri (Cyprus), Mount Pleasant (Falklands), Toulon (France), Camp Djibouti (France), Mumbai Naval (India), INS Kadamba/Karwar (India)

## Operator Color Scheme

| Operator | ABGR Color | Visual |
|----------|-----------|--------|
| USA | `ff0044ff` (blue) | 🔵 |
| Russia | `ff0044ff` (red) | 🔴 |
| China | `ff000099` (dark red) | 🔴 |
| UK | `ff0044ff` (blue) | 🔵 |
| France | `ff0044ff` (blue) | 🔵 |
| India | `ff008800` (green) | 🟢 |

## Adding New Bases

Edit `/home/nara/wm-collector/collectors/military_bases.py` — add to the `MILITARY_BASES` list:

```python
{"name": "Base Name", "lat": 12.34, "lon": 56.78, "country": "Country", "operator": "USA", "type": "airforce"},
```

Types: `navy` (scale 1.0), `airforce` (0.9), `army` (0.8), `marine` (0.8)
