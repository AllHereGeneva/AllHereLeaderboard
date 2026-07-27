# All Here — World CMI Leaderboard

A self-contained web section that shows the **Concentration & Mindfulness Index (CMI)**
of meditators worldwide: an immersive, full-viewport vector world map with clustered
pins for the top ~50, and a ranked Top 20 list floating over it as a glass panel.
Interactive (hover, pan/zoom, cluster-to-segment), mobile-optimised (the panel becomes
a bottom sheet), and styled to the All Here charter (May 2026).

No build step, no external map API, no framework — plain HTML/CSS/JS.

The section fills the browser viewport (`height: 100dvh`). To embed it shorter than
full-screen, wrap it in a container and override `.ahl__wrap { height: <your height>; }`.

---

## Files

```
index.html                     Demo page (also the reference for embedding)
assets/
  leaderboard.css              All styles, scoped under .ahl
  leaderboard.js               All logic (vanilla, no deps)
  data/
    cmi-sample.json            SAMPLE scores — replace with the real feed
    world-land.json            Vector world map (continent polygons)
    gazetteer.json             City → lat/lon fallback (top 3000 cities)
build/                         Scripts used to regenerate the data assets
```

---

## The data contract (what the real file must look like)

The page fetches one JSON file (`dataUrl`). Structure:

```json
{
  "meta": {
    "title": "World CMI Leaderboard",
    "subtitle": "Concentration & Mindfulness Index — meditators worldwide",
    "unit": "CMI",
    "scaleMax": 1000,
    "updated": "2026-07-18"
  },
  "entries": [
    {
      "city": "Sheffield", "country": "United Kingdom", "cmi": 415, "date": "2026-07-13",
      "lat": 53.3811, "lon": -1.4701,
      "labels": ["Tokyo QM", "VIP", "Top Performer"],
      "vip": {
        "name": "Hisami Tsurumori",
        "photo": "",
        "tag": "Tokyo 2025 Top Performer",
        "bio": "Originally from Japan, now in Sheffield, Hisami has practised Samatha meditation in the Theravada tradition for 16+ years."
      }
    },
    { "city": "Tokyo", "country": "Japan", "cmi": 393, "date": "2026-06-21", "labels": ["Tokyo QM"] }
  ]
}
```

Per entry:

| Field         | Required | Notes |
| ------------- | -------- | ----- |
| `city`        | yes      | Shown on the map/list. No name is shown unless a `vip` object is present. |
| `country`     | yes      | Full name (e.g. `"United States"`). |
| `cmi`         | yes      | The score. Ranking is computed client-side (highest = rank 1). |
| `date`        | yes      | ISO `YYYY-MM-DD`. |
| `lat`, `lon`  | **recommended** | Exact map position. See below. |
| `countryCode` | optional | ISO-2 (e.g. `"CH"`) — helps the fallback geocoder disambiguate. |
| `labels`      | optional | `string[]` of participant labels (e.g. `["Tokyo QM","VIP","Top Performer"]`). The bottom-left **Filter** lists every distinct label found in the feed; toggling one (or several — OR logic) pops matching pins with a gold glow, dims the rest, and highlights matching standings rows. |
| `vip`         | optional | Object `{ name, photo, bio, tag }` for a featured participant. `name` (wide-grotesk caps) and `bio` (2–4 sentences) are shown; `photo` is an image URL (leave empty/omit for a gold monogram fallback — do **not** hotlink third-party images); `tag` is an optional gold chip (e.g. `"Tokyo 2025 Top Performer"`). VIP pins get a gold ring + star badge (podium colours still apply to the top 3) and, when clicked as a single pin, open a glass profile card (click-away / × / Esc to close; centered modal on mobile). VIP duplicates in a shared city are pulled clear of the city's count-megapin so their card stays reachable. |

You can add more fields later (they're ignored until we wire them up).

### About coordinates — please include `lat`/`lon`

Placing a pin needs a coordinate. The page resolves it in this order:

1. Explicit `lat` + `lon` on the entry — **always correct, always preferred.**
2. `city` + `country` looked up in the bundled gazetteer (top 3000 world cities).
3. `city` alone (most-populous match) — last resort, can be ambiguous.

Client-side geocoding from a city *name* is inherently unreliable (many cities
share a name; "Bali" is also a town in Italy). Since the leaderboard is a curated
top ~50, adding `lat`/`lon` to the export is cheap and removes all ambiguity — it's
the recommended path. Entries that can't be located are still listed in the ranking;
they're just skipped on the map (and logged to the browser console).

> If your export can't include coordinates, send me the city list and I'll geocode
> it once into a lookup table we ship with the page.

---

## Configuration

```js
AHLeaderboard.init(document.getElementById('cmi-leaderboard'), {
  dataUrl:      'https://.../cmi-live.json',   // your hosted feed
  landUrl:      'assets/data/world-land.json',
  gazetteerUrl: 'assets/data/gazetteer.json',
  listTop:   20,   // rows in the ranked list
  mapTop:    50,   // top entries plotted on the map
  scaleMax:  1000, // CMI scale (also read from meta.scaleMax)
  clusterPx: 30    // screen distance below which pins merge
});
```

The data feed can live anywhere (S3, Cloudflare R2, a published Google Sheet
exported as JSON, the WordPress uploads folder…). Update the file → the page
reflects it on next load. Make sure the host sends permissive CORS headers if the
JSON is on a different domain than the page.

---

## Deploying updates — bump the asset version

Browsers cache `leaderboard.css` / `leaderboard.js` aggressively (only the data
JSON is fetched with `cache: 'no-store'`). So after a deploy, visitors can keep
running **stale code** until a hard refresh — which shows up as "my fix isn't
live" bugs. To force fresh assets, the demo appends a version query:

```html
<link rel="stylesheet" href="assets/leaderboard.css?v=3da4b710">
<script src="assets/leaderboard.js?v=3da4b710"></script>
```

**Run `python3 build/bump-version.py` before every deploy** (and whenever you
change `leaderboard.css`/`leaderboard.js` locally). It hashes the content of
both files and rewrites the `?v=` query in `index.html` to match — no more
manual incrementing, no more forgetting. Match the same value in any
WordPress/embed snippet you maintain by hand. Changing the query string makes
the browser treat it as a new URL and re-download it.

---

## Embedding in WordPress (staging.allherelounge.com)

The whole widget lives inside one element: `<section class="ahl">`. All CSS is
scoped under `.ahl`, so it won't collide with the theme.

**Option A — Custom HTML block (simplest).** Upload the `assets/` folder somewhere
public (e.g. `wp-content/uploads/leaderboard/`), then drop a *Custom HTML* block
onto the page:

```html
<link rel="stylesheet" href="/wp-content/uploads/leaderboard/leaderboard.css?v=5">
<section class="ahl" id="cmi-leaderboard"></section>
<script src="/wp-content/uploads/leaderboard/leaderboard.js?v=5"></script>
<script>
  AHLeaderboard.init(document.getElementById('cmi-leaderboard'), {
    dataUrl:      '/wp-content/uploads/leaderboard/data/cmi-live.json',
    landUrl:      '/wp-content/uploads/leaderboard/data/world-land.json',
    gazetteerUrl: '/wp-content/uploads/leaderboard/data/gazetteer.json'
  });
</script>
```

**Option B — enqueue in the theme.** `wp_enqueue_style`/`wp_enqueue_script` the two
asset files and add the `<section>` + init snippet to a page template or shortcode.

**Option C — iframe.** Host `index.html` standalone and embed it with an `<iframe>`
if you'd rather keep it fully isolated from the theme.

The display language is English (matches the site). Font stack uses **Grotzec**
(inherited from the theme when embedded) with **Barlow Condensed** as the web
fallback, and **Montserrat** for body — same as the charter.

---

## Regenerating the data assets

The `build/` scripts are one-off generators (run with Python 3):

- `build-world-land.py` — turns a Natural Earth land GeoJSON into the vector continent polygons.
- `build-gazetteer.py` — builds the city→lat/lon table from GeoNames `cities15000`
  + `countryInfo.txt`.
- `build-sample-data.py` — produces the sample dataset (for local preview only).
- `bump-version.py` — cache-busts `leaderboard.css`/`.js` (see "Deploying updates" above).

Source data (not committed): `ne_110m_land.geojson`, `cities15000.txt`,
`countryInfo.txt` — download URLs are noted at the top of each script.

---

## Local preview

```bash
cd AllHereLeaderboard
python3 -m http.server 8777
# open http://localhost:8777/index.html
```

(A server is needed because the page uses `fetch` — opening the file directly
with `file://` won't load the JSON.)
