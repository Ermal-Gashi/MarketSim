# MarketSim — Claude Chat Context

Use this file to bring Claude (this chat) up to speed on the project at any point.

---

## What We Are Building
MarketSim is a multi-agent AI system that simulates market entry for any product into a new geographic or demographic market. User inputs a product description, current market, and target market. Seven AI agents run sequentially and stream results to the frontend via SSE. Final output is a full market entry report with a Go/Cautious Go/No-Go verdict, animated country dot map, and signal radar chart.

This is a solo hackathon project that will continue to be developed beyond the hackathon.

---

## Core Advantage
MarketSim does what a user cannot do by asking Claude directly. Native Claude has no access to real-time World Bank data, cannot chain specialized agents that pass structured JSON to each other, cannot stream live progress to a frontend, and cannot combine real economic data with cultural dimension indexes and synthetic persona generation in a single automated pipeline. Every design decision should preserve and strengthen this advantage.

---

## Key Decisions Already Made

| Decision | Choice |
|----------|--------|
| Backend | Python + FastAPI |
| AI Model | `claude-sonnet-4-6` |
| Streaming | Server-Sent Events (SSE) via GET params |
| Frontend | React + Vite + Tailwind CSS + D3 + Recharts + Framer Motion |
| Theme | Light mode default, dark mode toggle — theme system built in theme.js |
| Repo | Single monorepo, one folder |
| Environment | PyCharm on Windows, PowerShell terminal |
| Project path | `C:\Users\korab\PycharmProjects\MarketSim` |
| Agent 7 | Pure Python simulation layer — no Claude call |
| Agent timeouts | 300 seconds for all agents |

---

## Current Project Structure

```
marketsim/
├── CLAUDE.md                          # Claude Code context
├── CONTEXT.md                         # This file — Claude chat context
├── README.md
├── .env                               # ANTHROPIC_API_KEY
├── .gitignore
├── main.py                            # FastAPI entry point ✅
│
├── backend/
│   ├── requirements.txt
│   ├── routes/
│   │   └── simulate.py                # SSE streaming endpoint ✅ wired and tested
│   ├── agents/
│   │   ├── product_analyst.py         # Agent 1 ✅
│   │   ├── market_data_fetcher.py     # Agent 2 ✅
│   │   ├── cultural_fit_scorer.py     # Agent 3 ✅
│   │   ├── persona_generator.py       # Agent 4 ✅ max_tokens=4000
│   │   ├── obstacle_detector.py       # Agent 5 ✅
│   │   ├── synthesizer.py             # Agent 6 ✅ max_tokens=4000
│   │   └── simulation_layer.py        # Agent 7 ✅ pure Python no Claude call
│   ├── services/
│   │   ├── claude_client.py           # All Claude calls go through here ✅
│   │   ├── world_bank_client.py       # World Bank API + household consumption ✅
│   │   └── countries_client.py        # REST Countries API wrapper ✅
│   ├── tests/
│   │   ├── test_services.py           # Service tests ✅
│   │   ├── test_agents.py             # Agent tests ✅
│   │   └── test_pipeline.py           # Full SSE pipeline test ✅ all 7 checks passing
│   └── data/
│       ├── hofstede.json              # Hofstede cultural dimensions — 112 countries ✅
│       └── business_environment.json  # CPI, Ease of Business, Press Freedom, Political Stability ✅
│
└── frontend/                          # React + Vite app — Milestone 2 in progress
    ├── index.html
    ├── vite.config.js                 # Proxy /api → localhost:8000 ✅
    ├── package.json
    ├── tailwind.config.js
    └── src/
        ├── main.jsx                   # ✅
        ├── App.jsx                    # ✅ theme toggle, grid background, Framer Motion fade
        ├── theme.js                   # ✅ full dark/light theme object
        ├── index.css                  # ✅ Tailwind directives
        ├── hooks/
        │   └── useSimulation.js       # ✅ SSE connection, agentStatuses, isComplete, completeReport
        └── components/
            ├── InputForm.jsx          # ✅ Section 1 complete — light/dark themed
            ├── AgentProgressBar.jsx   # 🔲 Section 2 — next to build
            ├── AgentNetworkModal.jsx  # 🔲 Section 2 — next to build
            ├── HeroMap.jsx            # 🔲 Section 3
            ├── RadarChart.jsx         # 🔲 Section 3
            ├── PersonaCards.jsx       # 🔲 Section 4
            ├── ObstacleMatrix.jsx     # 🔲 Section 5
            ├── EntryRoadmap.jsx       # 🔲 Section 6
            └── VerdictSummary.jsx     # 🔲 Section 7
```

---

## Agent Pipeline Summary

| # | Agent | Key Output | Status |
|---|-------|-----------|--------|
| 1 | Product Analyst | Value props, pricing tier, customer profile, optional enrichments | ✅ |
| 2 | Market Data Fetcher | GDP, internet penetration, competitors, infrastructure, regional breakdown | ✅ |
| 3 | Cultural Fit Scorer | Fit score 0-100, Hofstede dimension analysis, sales motion recommendation | ✅ |
| 4 | Persona Generator | 5 archetypes with variance profiles — max_tokens=4000 | ✅ |
| 5 | Obstacle Detector | 5 obstacles ordered by severity, business environment data grounded | ✅ |
| 6 | Synthesizer | Go/Cautious Go/No-Go verdict, regional_weights, dot_intensity, radar_scores | ✅ |
| 7 | Simulation Layer | 200 synthetic persona instances with conversion outcomes — pure Python | ✅ |

All agents return structured JSON. All Claude calls route through `claude_client.py`. No persistent memory — context passed explicitly. Agent 7 is pure Python — no Claude call.

---

## SSE Pipeline
- Endpoint: `GET /api/simulate`
- Query params: `product_description`, `current_market`, `target_market`
- All agent timeouts: 300 seconds
- CORS enabled for all origins
- Full pipeline test passing — all 7 checks green
- Final event contains `complete_report` with all agent outputs

---

## Theme System
- `frontend/src/theme.js` contains `themes.dark` and `themes.light`
- `App.jsx` holds `isDark` state, derives `theme = isDark ? themes.dark : themes.light`
- Theme toggle button fixed top-right — sun icon in dark mode, moon in light mode
- Every component receives `theme` as a prop and uses `theme.*` values for all colors
- Light mode is the default
- Key colors:
  - Accent teal (agents done): `#4DBBAA`
  - Accent wine red (button corners, errors): `#8B3A52`
  - These two accents are identical in both light and dark modes

---

## External Data Sources

| Source | Purpose | Coverage |
|--------|---------|----------|
| World Bank API | GDP per capita, internet penetration, household consumption | Live API |
| REST Countries API | Country metadata, currency, languages | Live API |
| hofstede.json | Cultural dimension scores (PDI, IDV, MAS, UAI, LTO, IVR) | 112 countries |
| business_environment.json | CPI, Ease of Doing Business, Press Freedom, Political Stability | 102 countries |

---

## Frontend — Section 1 Complete ✅

Input form with:
- Engineering grid background (light: warm off-white + gray grid, dark: near-black + dark grid)
- Form card with full border rectangle + subtle shadow in light mode
- Run Simulation button with wine red corner-only L-shaped lines
- Collapsible "How to get the best results" helper section
- Character counter on textarea
- Pulse animation on button when all fields filled
- Framer Motion fade transition when simulation starts
- Theme toggle button top-right

---

## Frontend — Section 2 Plan (next to build)

**Top bar** — slim persistent bar at top of page:
- Left: MarketSim wordmark
- Center: 7 green pill indicators lighting up one by one as agents complete
- Right: "View network" button

**Center of page** — large expressive agent status while simulation runs:
- Big evocative name e.g. "Reading the cultural landscape" (not the technical agent name)
- Subtitle describing what is happening right now
- Animated thinking indicator below

**Evocative agent names (center display):**
1. Product Analyst → "Decoding your product DNA"
2. Market Data Fetcher → "Pulling live market intelligence"
3. Cultural Fit Scorer → "Reading the cultural landscape"
4. Persona Generator → "Building your buyer archetypes"
5. Obstacle Detector → "Stress testing the entry path"
6. Synthesizer → "Weighing all the signals"
7. Simulation Layer → "Simulating 200 potential customers"

**Agent Network Modal:**
- Opens when "View network" button clicked
- Semi-transparent dark overlay (same in both light and dark mode)
- 7 agent nodes in a circle
- Agents light up sequentially as SSE events arrive
- Completed agents send animated light pulses to neighboring nodes
- When all done all connections are fully lit
- Close by clicking outside or X button

**Transition to report:**
- When isComplete=true: status text fades out
- Report sections fade in one by one on the same grid background

---

## Frontend — Section 3-7 Plan (after Section 2)

**Section 3 — Hero Visuals (two side by side):**
- Left: Animated country dot map (D3) — country silhouette, 200 dots from Agent 7, spawn by spawn_delay_ms, color by conversion_outcome, verdict overlay as corner-only rectangle
- Right: Signal radar chart (Recharts) — 6 axes from Agent 6 radar_scores
- Dot popup on click: avatar silhouette, display_name, job_title, outcome_reason, deciding_factor

**Section 4 — Persona Cards:** 5 flippable cards, front shows archetype info, back shows variance profile

**Section 5 — Obstacle Matrix:** Scatter plot severity vs time sensitivity

**Section 6 — Entry Roadmap:** Phased horizontal timeline from Agent 6 market_entry_sequence

**Section 7 — Verdict Summary:** Critical assumptions, recommended first move, wildcard, revisit trigger

---

## Milestones

| Milestone | Status | Goal |
|-----------|--------|------|
| 0 — Setup | ✅ Complete | FastAPI, all APIs, Claude client |
| 1 — Agent Pipeline + SSE | ✅ Complete | All 7 agents, pipeline wired, tests passing |
| 2 — Frontend | 🔄 In Progress | Section 1 done. Section 2 next. |
| 3 — Polish & Deploy | 🔲 Not started | Live URL, tested, demo ready |

---

## Claude Code vs Claude Chat — Role Split

| | Claude Code | Claude Chat (this) |
|--|-------------|-------------------|
| **Does** | Writes and edits code | Plans, advises, reviews, writes prompts |
| **Knows** | CLAUDE.md | This file (CONTEXT.md) |
| **Gets** | Specific build instructions | Strategic and architectural questions |

---

## How to Use This File

Paste at the start of a new Claude chat:
> "Here is my project context, please read it before we continue: [paste CONTEXT.md contents]"

---

## Things We Are NOT Building
- User authentication
- Saved simulation history
- Mobile responsive design
- More than 7 agents
- Any feature not listed in CLAUDE.md or this file
