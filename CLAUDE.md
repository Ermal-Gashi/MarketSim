# MarketSim — Claude Code Context

## What We Are Building
MarketSim is a multi-agent AI system that simulates market entry for any product into a new geographic or demographic market. A user inputs a product description, their current market, and a target market. Seven AI agents run sequentially, each passing structured output to the next, and the final report is streamed to the frontend in real time via SSE.

This is a solo-built hackathon project. Keep code clean, well-commented, and avoid over-engineering.

---

## Core Advantage
MarketSim does what a user cannot do by asking Claude directly. Native Claude has no access to real-time World Bank data, cannot chain specialized agents that pass structured JSON to each other, cannot stream live progress to a frontend, and cannot combine real economic data with cultural dimension indexes and synthetic persona generation in a single automated pipeline. Every design decision should preserve and strengthen this advantage.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI |
| AI | Anthropic Python SDK, model: `claude-sonnet-4-6` |
| Streaming | Server-Sent Events (SSE) via FastAPI StreamingResponse |
| Frontend | React + Vite, Tailwind CSS, D3 (dot map + country silhouette), Recharts (radar chart), Framer Motion (animations) |
| External APIs | World Bank API, REST Countries API |
| Static Data | Hofstede cultural dimensions, Business Environment indexes |
| Environment | python-dotenv for .env management |

---

## Repository Structure

```
marketsim/
│
├── CLAUDE.md                          # This file
├── CONTEXT.md                         # Claude chat context
├── README.md
├── .env                               # API keys — never hardcode
├── .gitignore
├── main.py                            # FastAPI entry point
│
├── backend/
│   ├── requirements.txt
│   ├── routes/
│   │   └── simulate.py                # GET /api/simulate — SSE streaming endpoint ✅
│   ├── agents/
│   │   ├── product_analyst.py         # Agent 1 ✅
│   │   ├── market_data_fetcher.py     # Agent 2 ✅
│   │   ├── cultural_fit_scorer.py     # Agent 3 ✅
│   │   ├── persona_generator.py       # Agent 4 ✅
│   │   ├── obstacle_detector.py       # Agent 5 ✅
│   │   ├── synthesizer.py             # Agent 6 ✅
│   │   └── simulation_layer.py        # Agent 7 ✅
│   ├── services/
│   │   ├── claude_client.py           # All Claude API calls go through here ✅
│   │   ├── world_bank_client.py       # World Bank API wrapper ✅
│   │   └── countries_client.py        # REST Countries API wrapper ✅
│   ├── tests/
│   │   ├── test_services.py           # Service tests ✅
│   │   ├── test_agents.py             # Agent tests ✅
│   │   └── test_pipeline.py           # Full SSE pipeline test ✅
│   └── data/
│       ├── hofstede.json              # Hofstede cultural dimensions — 112 countries ✅
│       └── business_environment.json  # CPI, Ease of Business, Press Freedom, Political Stability ✅
│
└── frontend/                          # React + Vite app — Milestone 2 in progress
    ├── index.html
    ├── vite.config.js
    ├── package.json
    ├── tailwind.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx                    # Theme toggle, grid background, section routing ✅
        ├── theme.js                   # Full dark/light theme object ✅
        ├── index.css
        ├── hooks/
        │   └── useSimulation.js       # SSE connection + state management ✅
        └── components/
            ├── InputForm.jsx          # Section 1 ✅ complete
            ├── AgentProgressBar.jsx   # Section 2 ✅ complete
            ├── AgentNetworkModal.jsx  # Section 2 ✅ complete
            ├── ReportDashboard.jsx    # Section 3 — main report container 🔲
            ├── HeroMap.jsx            # Row 1 center — animated country dot map 🔲
            ├── PersonaCards.jsx       # Row 1 left — 5 persona cards 🔲
            ├── ObstacleCards.jsx      # Row 1 right — 5 obstacle cards 🔲
            ├── RadarChart.jsx         # Row 2 center — signal radar 🔲
            ├── MarketStats.jsx        # Row 2 left — market snapshot stats 🔲
            ├── CulturalFit.jsx        # Row 2 right — cultural fit + Hofstede bars 🔲
            ├── EntryRoadmap.jsx       # Row 3 — phased timeline full width 🔲
            └── BottomStrip.jsx        # Row 4 — exec summary + first move + competitors 🔲
```

---

## Environment Variables

Store in `.env` at root. Never hardcode.

```
ANTHROPIC_API_KEY=your_key_here
```

---

## Agent Pipeline — All Complete ✅

| # | Agent | Input | Output | Status |
|---|-------|-------|--------|--------|
| 1 | Product Analyst | Product description + current market | Value props, pricing tier, customer profile | ✅ |
| 2 | Market Data Fetcher | Target market + Agent 1 | GDP, penetration, competitors, infrastructure, regional breakdown | ✅ |
| 3 | Cultural Fit Scorer | Agent 1 + 2 + Hofstede data | Fit score 0-100, dimension analysis, sales motion recommendation | ✅ |
| 4 | Persona Generator | Agent 1 + 2 + 3 | 5 archetypes with variance profiles — max_tokens=4000 | ✅ |
| 5 | Obstacle Detector | Agent 1 + 2 + 3 + 4 + business environment data | 5 obstacles ordered by severity | ✅ |
| 6 | Synthesizer | All agent outputs | Go/Cautious Go/No-Go verdict, regional_weights, dot_intensity, radar_scores | ✅ |
| 7 | Simulation Layer | Agent 4 + Agent 6 | 200 synthetic persona instances — pure Python, no Claude call | ✅ |

---

## Agent 7 — Simulation Layer

Agent 7 is pure Python — no Claude API call. It takes the 5 persona archetypes from Agent 4 with their variance_profile objects, rolls key variables randomly per instance using Agent 6 regional_weights for geographic distribution, and generates approximately 200 synthetic customer instances. Each instance has: archetype, city, lat/lng with jitter, conversion_outcome (converted/evaluating/abandoned), confidence_score, pulse_intensity, spawn_delay_ms, display_name, job_title, avatar_style, outcome_reason, deciding_factor. Output feeds the frontend dot map animation.

---

## SSE Pipeline — Complete ✅

Endpoint: `GET /api/simulate`
Query params: `product_description`, `current_market`, `target_market`
All agent timeouts: 600 seconds
CORS: enabled for all origins

Event format:
```
data: {"agent": N, "name": "Agent Name", "status": "running"}
data: {"agent": N, "name": "Agent Name", "status": "done", "output": {...}}
data: {"agent": 7, "name": "Simulation Layer", "status": "done", "output": {...}, "final": true, "complete_report": {...}}
```

Final event `complete_report` contains: product_description, current_market, target_market, agent1_output through agent7_output.

---

## Theme System ✅

- `frontend/src/theme.js` contains `themes.dark` and `themes.light`
- `App.jsx` holds `isDark` state, derives `theme = isDark ? themes.dark : themes.light`
- Theme toggle button fixed top-right always visible — sun icon in dark mode, moon in light mode
- Light mode is the default
- Every component receives `theme` as a prop
- Key accent colors:
  - `theme.accentActive` — teal `#4DBBAA` in dark mode, burgundy `#8B3A52` in light mode
  - `theme.accentWine` — `#8B3A52` in both modes (errors, cancel button hover)
  - `theme.bgBar` — `rgba(8,8,11,0.96)` dark, `rgba(244,244,240,0.96)` light

---

## Report Dashboard Layout — Section 3 🔲

The report fades in after simulation completes. It is a single scrollable page with 4 rows. All data comes from `completeReport` passed as a prop.

### Row 1 — Hero (three columns, same height)
```
┌──────────────┬─────────────────────┬──────────────┐
│  PERSONAS    │   VERDICT STAMP     │  OBSTACLES   │
│  (25% width) │   + Country map     │  (25% width) │
│              │   (50% width)       │              │
│  5 stacked   │   dots animating    │  5 stacked   │
│  mini cards  │   from Agent 7      │  mini cards  │
│              │                     │              │
│  Click to    │   Verdict overlay:  │  Color coded │
│  expand full │   corner-only rect  │  by severity │
│  detail      │   GO/CAUTION/NO-GO  │              │
└──────────────┴─────────────────────┴──────────────┘
```

**Center column — HeroMap.jsx:**
- Verdict stamp centered above the map — large bold text (GO / CAUTIOUS GO / NO-GO) inside a transparent rectangle with thick colored corner lines only. Green=Go, Amber=Cautious Go, Red=No-Go. No filled background — just the corners drawn.
- D3 country silhouette below the stamp, rendered from GeoJSON
- 200 dots spawning gradually using spawn_delay_ms from Agent 7 instances
- Dot colors: converted=`#4DBBAA` teal, evaluating=amber, abandoned=dim red
- Clicking a dot shows popup: avatar silhouette, display_name, job_title, outcome_reason, deciding_factor

**Left column — PersonaCards.jsx:**
- 5 mini cards stacked vertically
- Each shows: initials circle, name+age, job title (truncated), city, likelihood badge
- Likelihood badge colors: High=`theme.accentActive`, Medium=amber, Low=wine red
- Click to expand full detail overlay showing full persona info and variance profile

**Right column — ObstacleCards.jsx:**
- 5 mini cards stacked vertically
- Each shows: severity badge, obstacle title, one-line description
- Severity colors: Critical=red, High=orange, Medium=amber, Low=green
- Click to expand showing full description and mitigation

---

### Row 2 — Analytics (three columns, same height)
```
┌──────────────┬─────────────────────┬──────────────┐
│  MARKET DATA │   SIGNAL RADAR      │ CULTURAL FIT │
│  (25% width) │   (50% width)       │ (25% width)  │
│              │                     │              │
│  GDP         │   6-axis spider     │ Score number │
│  Internet %  │   chart from        │ + label      │
│  Population  │   Agent 6           │ + 6 Hofstede │
│  Maturity    │   radar_scores      │ dimension    │
│  Trend arrow │                     │ bars         │
└──────────────┴─────────────────────┴──────────────┘
```

**Left column — MarketStats.jsx:**
Data from agent2_output: gdp_per_capita_usd, internet_penetration_pct, population, market_maturity, market_trend
Show as clean stat rows with label + value + trend indicator

**Center column — RadarChart.jsx:**
- Recharts RadarChart
- 6 axes from agent6_output.radar_scores: Market growth, Cultural fit, Internet penetration, Political stability, Ease of business, Corruption index
- Filled polygon in theme.accentActive color at 30% opacity
- Dashed outline showing ideal score (80 on all axes) in theme.borderStrong
- Score labels on each axis

**Right column — CulturalFit.jsx:**
- Large score number (e.g. 52) with score_label below it (e.g. "Moderate Fit")
- 6 horizontal bars for each Hofstede dimension from agent3_output.dimension_analysis
- Each bar shows: dimension name, score number, filled bar proportional to score
- Bar color matches score: above 70=warm, 40-70=neutral, below 40=cool

---

### Row 3 — Entry Roadmap (full width)
```
[ Phase 1 ] ──→ [ Phase 2 ] ──→ [ Phase 3 ] ──→ [ Phase 4 ]
```
- Data from agent6_output.market_entry_sequence
- Each phase: number circle, phase_name, timeframe, list of actions
- Connected by a line that progresses from red (urgent/legal) to green (scale)
- Animate left to right when row scrolls into view using Framer Motion

---

### Row 4 — Bottom Strip (three columns)
```
┌─────────────────┬──────────────────┬──────────────┐
│ Executive       │ Recommended      │ Competitors  │
│ summary +       │ first move       │ list from    │
│ assumptions     │ + wildcard       │ Agent 2      │
└─────────────────┴──────────────────┴──────────────┘
```

**Left — executive_summary from agent6_output + critical_assumptions (3 numbered cards)**
**Center — recommended_first_move as highlighted CTA card + biggest_wildcard below it**
**Right — major_local_competitors list from agent2_output, each as a simple row**

---

## External Data Sources

| Source | Purpose | Coverage |
|--------|---------|----------|
| World Bank API | GDP per capita, internet penetration, household consumption | Live API |
| REST Countries API | Country metadata, currency, languages | Live API |
| hofstede.json | Cultural dimension scores (PDI, IDV, MAS, UAI, LTO, IVR) | 112 countries |
| business_environment.json | CPI, Ease of Doing Business, Press Freedom, Political Stability | 102 countries |

---

## Claude Client Rules

- All Claude calls go through `services/claude_client.py`
- Model: `claude-sonnet-4-6`
- Default max_tokens: 2000. Agent 4 and Agent 6 use max_tokens=4000
- Every agent system prompt must end with: "Respond only with valid JSON. No preamble, no explanation, no markdown fences."
- Strip markdown fences from response before JSON parsing
- Retry once if JSON parsing fails before raising an error

---

## Error Handling

- Every agent wrapped in try/except in simulate.py
- On failure yield an SSE error event and stop pipeline gracefully
- Never let an unhandled exception crash the stream silently

---

## Coding Conventions — Backend

- Each agent file has one public function: `run(inputs: dict) -> dict`
- Use type hints throughout
- No print statements — use Python logging
- Prompts defined as constants at top of each agent file
- Never import one agent from another — orchestration only in `simulate.py`

---

## Coding Conventions — Frontend

- One component per file
- Props typed with PropTypes
- All colors from theme object — never hardcode hex values in components
- All D3 code inside useEffect with proper cleanup
- All chart data derived from completeReport in the component, not in the hook
- Console.log allowed during development

---

## Milestones

### Milestone 0 — Setup ✅
### Milestone 1 — Agent Pipeline + SSE ✅
### Milestone 2 — Frontend 🔄 In Progress
- Section 1 Input Form ✅
- Section 2 Agent Progress + Modal ✅
- Section 3 Report Dashboard 🔲 — next to build
  - Build order: ReportDashboard container → HeroMap → PersonaCards → ObstacleCards → RadarChart → MarketStats → CulturalFit → EntryRoadmap → BottomStrip

### Milestone 3 — Polish & Deploy 🔲
- Tested with 3 different product + market combinations
- Deployed backend on Railway or Render
- Deployed frontend on Vercel
- Demo runs end to end in under 90 seconds

---

## Do Not Build Without Being Asked
- User authentication
- Saving or history of simulations
- Mobile responsive design
- Any additional agents beyond Agent 7
- Any feature not listed in this document
