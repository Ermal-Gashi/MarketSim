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
├── main.py                            # FastAPI entry point ✅
│
├── backend/
│   ├── requirements.txt
│   ├── routes/
│   │   └── simulate.py                # GET /api/simulate — SSE streaming endpoint ✅
│   ├── agents/
│   │   ├── product_analyst.py         # Agent 1 ✅
│   │   ├── market_data_fetcher.py     # Agent 2 ✅ — min 6 competitors enforced
│   │   ├── cultural_fit_scorer.py     # Agent 3 ✅
│   │   ├── persona_generator.py       # Agent 4 ✅ max_tokens=4000
│   │   ├── obstacle_detector.py       # Agent 5 ✅
│   │   ├── synthesizer.py             # Agent 6 ✅ max_tokens=4000
│   │   └── simulation_layer.py        # Agent 7 ✅ pure Python no Claude call
│   ├── services/
│   │   ├── claude_client.py           # All Claude API calls go through here ✅
│   │   ├── world_bank_client.py       # World Bank API + household consumption ✅
│   │   └── countries_client.py        # REST Countries API wrapper ✅
│   ├── tests/
│   │   ├── test_services.py           # Service tests ✅
│   │   ├── test_agents.py             # Agent tests ✅
│   │   └── test_pipeline.py           # Full SSE pipeline test ✅
│   └── data/
│       ├── hofstede.json              # Hofstede cultural dimensions — 112 countries ✅
│       └── business_environment.json  # CPI, Ease of Business, Press Freedom, Political Stability ✅
│
└── frontend/                          # React + Vite app ✅
    ├── index.html
    ├── vite.config.js                 # Proxy /api → localhost:8000 ✅
    ├── package.json
    ├── tailwind.config.js
    └── src/
        ├── main.jsx                   ✅
        ├── App.jsx                    # Theme toggle, grid bg, section routing ✅
        ├── theme.js                   # Full dark/light theme object ✅
        ├── index.css                  ✅
        ├── hooks/
        │   └── useSimulation.js       # SSE connection + state management ✅
        └── components/
            ├── InputForm.jsx          # Section 1 ✅
            ├── AgentProgressBar.jsx   # Section 2 ✅
            ├── AgentNetworkModal.jsx  # Section 2 ✅
            ├── ReportDashboard.jsx    # Report container — all 4 rows ✅
            ├── HeroMap.jsx            # Row 1 center — D3 dot map + verdict stamp ✅
            ├── PersonaCards.jsx       # Row 1 left — 5 persona cards ✅
            ├── ObstacleCards.jsx      # Row 1 right — 5 obstacle cards ✅
            ├── RadarChart.jsx         # Row 2 center — signal radar ✅
            ├── MarketStats.jsx        # Row 2 left — market snapshot stats ✅
            ├── CulturalFit.jsx        # Row 2 right — cultural fit + Hofstede bars ✅
            ├── EntryRoadmap.jsx       # Row 3 — phased timeline full width ✅
            └── BottomStrip.jsx        # Row 4 — stat chips + first move + wildcard + competitors ✅
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
| 1 | Product Analyst | Product description + current market | Value props, pricing tier, customer profile, optional enrichments | ✅ |
| 2 | Market Data Fetcher | Target market + Agent 1 | GDP, penetration, min 6 competitors, infrastructure, regional breakdown | ✅ |
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
- Every component receives `theme` as a prop — never hardcode hex values in components
- Key accent colors:
  - `theme.accentActive` — teal `#4DBBAA` in both dark and light mode
  - `theme.accentWine` — `#8B3A52` in both modes (errors, cancel button hover)
  - `theme.bgBar` — `rgba(8,8,11,0.96)` dark, `rgba(244,244,240,0.96)` light

---

## Frontend — All Sections Complete ✅

### Section 1 — Input Form ✅
- Engineering grid background (light: warm off-white + gray grid, dark: near-black + dark grid)
- Form card with full border rectangle
- Run Simulation button with wine red corner-only L-shaped lines
- Collapsible "How to get the best results" helper section
- Character counter on textarea
- Pulse animation on button when all fields filled
- Framer Motion fade transition when simulation starts
- Theme toggle button fixed top-right always visible

### Section 2 — Agent Progress ✅
- Fixed top bar: MARKETSIM wordmark left, 7 pills center, View network button moves to top-left when complete
- Center page: large evocative agent name + subtitle + thinking dots while running
- Evocative names: 'Decoding your product DNA' / 'Pulling live market intelligence' / 'Reading the cultural landscape' / 'Building your buyer archetypes' / 'Stress testing the entry path' / 'Weighing all the signals' / 'Simulating 200 potential customers'
- View network button opens AgentNetworkModal — 7 nodes in circle, animated data packets, responds to theme
- Cancel button beside View network — calls reset() and returns to InputForm
- When complete: status text fades out, View network moves to top bar left side

### Section 3 — Report Dashboard ✅ (4 rows)

**Row 1 — Hero — grid 1fr 2.5fr 1fr:**
- Left: PersonaCards — 5 stacked mini cards with avatar block, name+age, city. Click expands overlay. Hovering highlights matching dots on map.
- Center: HeroMap — verdict stamp (pulsating, corner-only rectangle) + D3 country silhouette + 200 animated dots from Agent 7. Dot click shows popup.
- Right: ObstacleCards — 5 stacked mini cards with severity pill + centered title. Subtle severity tint on card background.

**Row 2 — Analytics — grid 1fr 2.5fr 1fr:**
- Left: MarketStats — 5 stat rows (GDP, internet %, population, maturity badge, trend arrow)
- Center: RadarChart — Recharts 6-axis spider, filled polygon + dashed ideal line + score labels on vertices
- Right: CulturalFit — large score number (56px) + score label + 6 Hofstede dimension bars with hover tooltip for implication text

**Row 3 — Entry Roadmap — full width:**
- Horizontal timeline with animated traveling particle along gradient line
- Phase nodes clickable — popup appears above node with phase actions list
- No default selected phase — click to reveal

**Row 4 — Bottom Strip:**
- Top: 4 stat chips (Confidence, Time to revenue, Est. CAC, Sales motion)
- Below: 3 columns
  - Left: First Move card (teal left border, 16px hero text) + Wildcard mini card + Revisit mini card
  - Center: Generate Report button — full border rectangle, pulsating teal glow, no card container behind it
  - Right: Competitors card — each competitor row has colored left border by threat level (wine red=high, amber=medium, gray=low) + company name + description

---

## Report Dashboard Layout Reference

```
Row 1: [Personas 22%] [HeroMap + Verdict 56%] [Obstacles 22%]
Row 2: [MarketStats 22%] [RadarChart 56%] [CulturalFit 22%]
Row 3: [Entry Roadmap — full width]
Row 4: [Stat chips — full width]
       [First Move 33%] [Generate Report 33%] [Competitors 33%]
```

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
- Agent 7 has explicit logging: starting + completed instance count

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
- TEST_MODE constant in App.jsx — set to false for production, true for layout testing

---

## Milestones

### Milestone 0 — Setup ✅
### Milestone 1 — Agent Pipeline + SSE ✅
### Milestone 2 — Frontend ✅ Complete
- Section 1 Input Form ✅
- Section 2 Agent Progress + Modal ✅
- Section 3 Report Dashboard — all 4 rows ✅

### Milestone 3 — Polish & Deploy 🔲
- Fix any remaining bugs from live test runs
- Tested with 3 different product + market combinations
- Deployed backend on Railway or Render
- Deployed frontend on Vercel
- Demo runs end to end in under 90 seconds
- README.md written for GitHub

---

## Known Issues / To Fix
- Agent 7 SSE flush bug — fix applied (asyncio.sleep(0) before final yield) — needs verification
- TEST_MODE must be false before any live run
- Some KPI chips (Time to revenue, Est. CAC) may show — if Agent 6 returns null for optional fields

---

## Do Not Build Without Being Asked
- User authentication
- Saving or history of simulations
- Mobile responsive design
- Any additional agents beyond Agent 7
- PDF generation (Generate Report button is placeholder)
- Any feature not listed in this document
