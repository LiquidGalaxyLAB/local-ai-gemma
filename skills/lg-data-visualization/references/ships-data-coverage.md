# Ships & Maritime Data — Middle East + US East Coast

The ships collector (`collectors/ships.py`) contains static config data for naval bases, ports, and chokepoints. Expanded July 2026 to cover Middle East (Strait of Hormuz) and US East Coast.

## Coverage

| Region | Naval Bases | Ports | Chokepoints |
|--------|-------------|-------|-------------|
| India | 8 (INS Mumbai, Kadamba, Vishakhapatnam, Kochi, etc.) | 11 (Mumbai, JNPT, Chennai, Kolkata, etc.) | 6 (Malacca, Six/Nine/Eight Degree, Bab-el-Mandeb, Sunda) |
| Middle East | 5 (Bandar Abbas, NSA Bahrain, Juffair, Ras Al Khair, Duqm) | 8 (Bandar Abbas, Ras Tanura, Khor Fakkan, Jebel Ali, Doha, Shuwaikh, Salalah, Fujairah) | 3 (Hormuz West/East/North) |
| US East Coast | 3 (Norfolk NS, New London Sub Base, USCG NY) | 9 (NY/NJ, Newark, Baltimore, Boston, Philadelphia, Savannah, Norfolk, Charleston, Miami) | — |

## Future Expansion

Next priority layers:
- Mediterranean ports (Gibraltar, Suez, Marseille, Genoa, Piraeus)
- South China Sea (Singapore, Shanghai, Hong Kong, Manila)
- West Coast US (LA, Long Beach, Oakland, Seattle, San Diego)
- Chokepoints: Suez Canal, Panama Canal, Dover Strait, Bosphorus, Cape of Good Hope

## Adding New Entries

Add to the appropriate list in `collectors/ships.py`. Each entry is a dict with `name`, `lat`, `lon`, and optional `country`/`desc`/`type`. The collector automatically filters by region bounding box.
