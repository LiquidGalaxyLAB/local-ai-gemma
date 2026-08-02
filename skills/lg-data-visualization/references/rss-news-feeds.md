# RSS News Feeds — News Data Source

**Why RSS instead of GDELT:** GDELT Project API rate-limits aggressively (429 errors after 3-4 rapid requests). RSS feeds from major news orgs are free, reliable, require no API keys, and return well-structured headline + summary + link data.

**Feed sources used in `collectors/news.py`:**

| Feed | URL | Coverage |
|------|-----|----------|
| BBC World | `feeds.bbci.co.uk/news/world/rss.xml` | Global |
| BBC Middle East | `feeds.bbci.co.uk/news/world/middle_east/rss.xml` | Middle East |
| Al Jazeera | `www.aljazeera.com/xml/rss/all.xml` | Global + MENA |
| France24 | `www.france24.com/en/rss` | Global |
| DW News | `rss.dw.com/rdf/rss-en-world` | Global |
| AP News | `https://simplefeed.vercel.app/api?url=https%3A%2F%2Fapnews.com%2Fhub%2Fworld-news%2Ffeed` | Global |
| NPR World | `feeds.npr.org/1004/rss.xml` | Global |

**Data extraction from RSS entries:**
```python
feed = feedparser.parse(feed_url)
for entry in feed.entries:
    title = entry.get('title', '')
    link = entry.get('link', '')
    summary = entry.get('summary', entry.get('description', ''))
    published = entry.get('published', entry.get('updated', ''))
```

**Geo-positioning (no lat/lon in RSS):**
RSS feeds do not include geographic coordinates. Articles are fanned out around the region center point using a spiral pattern:
- Increment angle by 38-40° per article
- Distance increases in rings (3°, 6°, 9°, ... from center)
- Clamped to region bounding box edges

**Topic classification (keyword-based):**
```python
TOPIC_KEYWORDS = {
    'conflict': ['war', 'military', 'attack', 'strike', 'missile', ...],
    'disaster': ['earthquake', 'flood', 'hurricane', 'wildfire', ...],
    'economy':  ['economy', 'trade', 'market', 'inflation', ...],
    'energy':   ['oil', 'gas', 'pipeline', 'opec', ...],
    ...
}
```
Each article gets an emoji icon based on the first matching keyword group.

**Implementation notes:**
- Fetch top 10 entries per feed (most recent)
- Deduplicate by normalized title prefix (first 60 chars)
- Accept articles whose headline mentions region-specific terms
- Cap at 50 articles total to keep KML readable
- Sort newest-first
- 300ms delay between feeds to avoid hammering servers

**Pitfalls:**
- No geographic coordinates → articles spread around region center, not at real locations
- Topic classification is keyword-only, no NLP — may misclassify
- Some feeds may be slow or temporarily unreachable (feedparser handles gracefully)
- RSS does not provide article body text, only summary/description
