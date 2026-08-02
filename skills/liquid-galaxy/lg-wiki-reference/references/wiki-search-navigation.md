# LG Wiki Search & Navigation

The SPA at lg-wiki-coral.vercel.app uses Next.js client-side routing. Direct URL navigation to secondary pages fails (404). Sidebar link clicks via `browser_click` may silently redirect to `/docs/arc` instead of the target page.

## Reliable Navigation: Search

The **search box** is the most reliable way to find pages. It filters the sidebar to matching results, and clicking a result navigates to the correct `/docs/dynamic#<hash>` URL.

### Steps

1. Navigate to the homepage or `/docs/arc`
2. Click the "Documentation" nav link to expand the full sidebar
3. Type the search term into the searchbox (`ref` changes per session — find it as `searchbox "Search..."`)
4. Press Enter
5. Sidebar collapses to matching results — click the desired link

### Example: Finding Balloon Pages

```
browser_navigate(url="https://lg-wiki-coral.vercel.app/")
browser_click(ref="@e3")           # Documentation
browser_type(ref="@e16", text="balloon")  # Search
browser_press(key="Enter")
# Sidebar now shows: "How To Pin A Place With A KML Balloon?" + 
#   "How To Send A Simple Balloon Including Some Data On The Right-Most Screen?"
browser_click(ref="<ref>")         # Click desired result
```

## Direct URL Navigation (Fragile)

Pages accessed directly by URL often fail with "Unexpected Application Error! / 404 Not Found". The only reliably working direct routes are:

| Route | Content |
|-------|---------|
| `/docs/arc` | Architecture (master-slave, UDP, SSH) |
| `/docs/rig` | Rig Installation (Ubuntu + LG setup) |
| `/docs/control` | Control Commands |

## Hash-Based Routes (via SPA Only)

All secondary pages use `/docs/dynamic#<hash>` pattern. These **only work when navigated from within the SPA** (via sidebar click or search result). Direct `browser_navigate` to `/docs/dynamic#<hash>` renders a blank page.

## Getting Page Content When SPA Won't Navigate

When sidebar clicks silently redirect to `/docs/arc`, use this JS to extract the target page's content after manually setting the URL hash:

```javascript
// Set hash after clicking Documentation
window.location.hash = '<hash_id>';
// Then query content area:
const els = document.querySelectorAll('h1, h2, h3, h4, p, pre, code, li, strong');
let txt = '';
els.forEach(el => {
  const r = el.getBoundingClientRect();
  if (r.left > 200 && r.top > 50 && el.innerText.trim().length > 3) {
    txt += el.innerText.trim() + '\n';
  }
});
```
