It documents everything you’ve already built, without changing design or logic, and clearly explains:

• Architecture
• API endpoints
• UI pages
• Max-Change logic
• Chart support
• Deployment
• Known limitations
• Future roadmap


📊 GEX Dashboard – Documentation
Overview

This project is a real-time GEX (Gamma Exposure) visualization platform for SPX that combines:

Options-derived market structure

Strike-level OI & volume visualization

Max-change detection

Landscape (flow) view

Dashboard view

Chart view with TradingView integration

It is designed to be:

Fast

API-efficient

Read-only (safe)

Extendable for AI later

📁 Project Structure
ironcondor/
├── gex_web.py              # Backend API (FastAPI)
├── static/
│   ├── index.html          # Dashboard UI
│   ├── landscape.html      # Strike ladder / flow view
│   └── chart.html          # TradingView + GEX overlay
├── data/
│   └── cache/              # In-memory / rolling cache
├── logs/
│   └── gex_mvp.log
└── README.md

🚀 How the App Runs
Start Server
fuser -k 8787/tcp || true
nohup python -m uvicorn gex_web:app \
  --host 0.0.0.0 \
  --port 8787 \
  > /tmp/gex_mvp.log 2>&1 &

Access Pages
Page	URL
Dashboard	/static/index.html
Landscape	/landscape
Chart	/chart
API Root	/api/mvp
🔌 Core API
GET /api/mvp

Main data engine powering all pages.

Query Params
Param	Description
symbol	$SPX
strike_count	Number of strikes
expiry	Explicit expiry
Example
curl "http://localhost:8787/api/mvp?symbol=$SPX&strike_count=60&expiry=2025-12-26"

Response Structure
{
  "symbol": "SPX",
  "expiry": "2025-12-26",
  "spot": 6935.26,
  "expected_move": 14.20,
  "em_lower": 6921.06,
  "em_upper": 6949.46,
  "zero_gamma": 6935,
  "call_wall": 6950,
  "put_wall": 6850,
  "histogram": [...],
  "summary": {...},
  "maxchange": {
    "1m": { "strike": 6965, "delta": -7107 },
    "5m": { "strike": 6965, "delta": -7107 },
    "15m": {}
  }
}

📊 Dashboard (index.html)
Purpose

Main control panel for:

Strike histogram

GEX visualization

Max change detection

Expiry selection

Features

✅ Strike histogram
✅ Volume + OI overlays
✅ Spot highlight
✅ Call / Put walls
✅ Expected Move
✅ Zero gamma
✅ Auto refresh
✅ Max Change detection (1m / 5m / 15m)
✅ Mobile responsive

Max Change Logic

Tracks delta change per strike

Computes largest absolute change per window

Exposed via:

maxchange["1m" | "5m" | "15m"]

Color Legend
Color	Meaning
Green	Call dominant
Red	Put dominant
Neon Yellow	Max change
Dark	Volume
Light	OI
🧭 Landscape View (/landscape)
Purpose

Flow-based visualization of:

Strike dominance

Dealer positioning

Vol/OI pressure

Features

Net OI bars

Volume overlay

Spot line

Upper/lower bands

Expiry selector

Unusual flow table

Zero gamma region

Used for intraday bias & structure awareness.

📈 Chart View (/chart)
Purpose

TradingView-powered chart + GEX overlays

Current Capabilities

✅ SPX chart (via FOREXCOM:SPX500)
✅ 5-minute timeframe
✅ Fullscreen
✅ Linked to backend API
✅ Side panel with:

Spot

EM range

Walls

Max change

Zero gamma

Why TradingView?

Reliable candle feed

Zoom/pan support

Mobile-friendly

No rate limits

⚠️ TradingView widget cannot be overlaid directly with strike-level data (iframe limitation)

🔄 Max Change Engine
What It Does

Tracks largest delta movement per strike over time

How It Works

Every API call stores snapshot

Rolling history per expiry

Delta difference computed

Largest absolute change reported

Output
"maxchange": {
  "1m": { "strike": 6965, "delta": -7107 },
  "5m": { "strike": 6965, "delta": -7107 }
}

📱 Mobile Support

✔ Responsive layout
✔ Touch-friendly
✔ Auto column stacking
✔ Chart full-screen compatible

⚠️ Design Constraints (Intentional)
Feature	Status
TradingView overlay drawing	❌ Not possible
SPX native candles	❌ TradingView restriction
Greeks from Schwab	⚠ Depends on API
AI signals	⏳ Deferred
Alerts	⏳ Planned
🧠 Design Philosophy

No predictions

No signals

No trade advice

Only structure & flow

Human decision layer stays in control

🛣 Roadmap
Phase 1 (Done)

✔ GEX engine
✔ Landscape
✔ Dashboard
✔ Max change
✔ Chart page

Phase 2 (Planned)

⬜ Unusual volume detection
⬜ Strike clustering
⬜ Heatmap overlay
⬜ Alert rules

Phase 3 (Optional)

⬜ AI explanation layer
⬜ Narrative summary
⬜ Historical replay

🧩 Summary

This system now provides:

✔ Institutional-style GEX visibility
✔ Strike-level pressure mapping
✔ Real-time flow shifts
✔ Clean, fast UI
✔ Expandable architecture

You now have a foundation comparable to GEXBot / SpotGamma — with full control.

## Smoke testing a running server
Use `smoke_test.py` to check a deployed instance (local or remote) without shipping data. Example:

```
python smoke_test.py --base-url http://localhost:8787 --symbol $SPX --strike-count 60
```

The script verifies:
- `/` serves the dashboard HTML
- `/api/expiries` returns expiry keys for the symbol
- `/api/mvp` returns live snapshot fields (spot, live flag)

Use `--base-url` to point at your own server (e.g., `https://your-host.example.com`).
