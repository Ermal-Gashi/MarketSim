# MarketSim — Claude Chat Context

Use this file to bring Claude (this chat) up to speed on the project at any point.

---

## What We Are Building
MarketSim is a multi-agent AI system that simulates market entry for any product into a new geographic or demographic market. User inputs a product description, current market, and target market. Seven AI agents run sequentially and stream results to the frontend via SSE. Final output is a full market entry report with a Go/Cautious Go/No-Go verdict, animated country dot map, signal radar chart, and full market intelligence dashboard.

This is a solo hackathon project that will continue to be developed beyond the hackathon.

---

## Core Advantage
MarketSim does what a user cannot do by asking Claude directly. Native Claude has no access to real-time World Bank data, cannot chain specialized agents that pass structured JSON to each other, cannot stream live progress to a frontend, and cannot combine real economic data with cultural dimension indexes and synthetic persona generation in a single automated pipeline.

---

## Key Decisions Already Made

| Decision | Choice |
|----------|--------|
| Backend | Python + FastAPI |
| AI Model | `claude-sonnet-4-6` |
| Streaming | Server-Sent Events (SSE) via GET params |
| Frontend | React + Vite + Tailwind CSS + D3 + Recharts + Framer Motion |
| Theme | Light mode default, dark mode toggle — theme.js system |
| Repo | Single monorepo |
| Environment | PyCharm on Windows, PowerShell terminal |
| Project path | `C:\Users\korab\PycharmProjects\MarketSim` |
| Agent 7 | Pure Python simulation layer — no Claude call |
| Agent timeouts | 600 seconds for all agents |
| TEST_MODE | Boolean in App.jsx — must be false for live runs |

---

## Current Project Structure

```
marketsim/
├── CLAUDE.md                          # Claude Code context ✅ updated
├── CONTEXT.md                         # This file ✅ updated
├── README.md
├── .env                               # ANTHROPIC_API_KEY
├── .gitignore
├── main.py                            # FastAPI entry point ✅
│
├── backend/
│   ├── requirements.txt
│   ├── routes/
│   │   └── simulate.py                # SSE streaming endpoint ✅ Agent 7 flush fix applied
│   ├── agents/
│   │   ├── product_analyst.py         # Agent 1 ✅
│   │   ├── market_data_fetcher.py     # Agent 2 ✅ min 6 competitors enforced
│   │   ├── cultural_fit_scorer.py     # Agent 3 ✅
│   │   ├── persona_generator.py       # Agent 4 ✅ max_tokens=4000
│   │   ├── obstacle_detector.py       # Agent 5 ✅
│   │   ├── synthesizer.py             # Agent 6 ✅ max_tokens=4000
│   │   └── simulation_layer.py        # Agent 7 ✅ pure Python no Claude call
│   ├── services/
│   │   ├── claude_client.py           # ✅
│   │   ├── world_bank_client.py       # ✅
│   │   └── countries_client.py        # ✅
│   ├── tests/
│   │   ├── test_services.py           # ✅
│   │   ├── test_agents.py             # ✅
│   │   └── test_pipeline.py           # ✅ all 7 checks passing
│   └── data/
│       ├── hofstede.json              # 112 countries ✅
│       └── business_environment.json  # 102 countries ✅
│
└── frontend/                          # React + Vite ✅ all sections built
    └── src/
        ├── App.jsx                    # ✅ TEST_MODE, theme toggle, routing
        ├── theme.js                   # ✅ dark/light theme object
        ├── hooks/
        │   └── useSimulation.js       # ✅ SSE, agentStatuses, completeReport
        └── components/
            ├── InputForm.jsx          # Section 1 ✅
            ├── AgentProgressBar.jsx   # Section 2 ✅
            ├── AgentNetworkModal.jsx  # Section 2 ✅
            ├── ReportDashboard.jsx    # Report container ✅
            ├── HeroMap.jsx            # Row 1 center ✅
            ├── PersonaCards.jsx       # Row 1 left ✅
            ├── ObstacleCards.jsx      # Row 1 right ✅
            ├── RadarChart.jsx         # Row 2 center ✅
            ├── MarketStats.jsx        # Row 2 left ✅
            ├── CulturalFit.jsx        # Row 2 right ✅
            ├── EntryRoadmap.jsx       # Row 3 ✅
            └── BottomStrip.jsx        # Row 4 ✅
```

---

## Agent Pipeline — All Complete ✅

| # | Agent | Key Output | Status |
|---|-------|-----------|--------|
| 1 | Product Analyst | Value props, pricing tier, customer profile | ✅ |
| 2 | Market Data Fetcher | GDP, internet %, min 6 competitors, regional breakdown | ✅ |
| 3 | Cultural Fit Scorer | Fit score 0-100, Hofstede dimension analysis | ✅ |
| 4 | Persona Generator | 5 archetypes with variance profiles | ✅ |
| 5 | Obstacle Detector | 5 obstacles ordered by severity | ✅ |
| 6 | Synthesizer | Verdict, regional_weights, dot_intensity, radar_scores | ✅ |
| 7 | Simulation Layer | 200 synthetic persona instances — pure Python | ✅ |

---

## SSE Pipeline ✅
- Endpoint: `GET /api/simulate`
- All agent timeouts: 600 seconds
- Agent 7 SSE flush fix: `asyncio.sleep(0)` before final yield
- Final event contains `complete_report` with all agent outputs

---

## Theme System ✅
- Light mode default, dark mode toggle fixed top-right
- `theme.accentActive` = `#4DBBAA` teal in both modes
- `theme.accentWine` = `#8B3A52` wine red in both modes
- All components receive `theme` as prop — no hardcoded hex values

---

## Frontend — Complete ✅

### Section 1 — Input Form ✅
- Engineering grid background (light warm off-white, dark near-black)
- Form card with full border rectangle
- Run Simulation button with wine red corner L-lines
- Collapsible helper section, character counter, pulse animation

### Section 2 — Agent Progress ✅
- Fixed top bar: MARKETSIM + 7 pills + View network (moves to left when complete)
- Center: large evocative agent names cycling with thinking dots
- Cancel button beside View network
- AgentNetworkModal: 7 nodes in circle, animated data packets, theme-responsive
- Transition: status fades out → ReportDashboard fades in

### Section 3 — Report Dashboard ✅ (4 rows)

**Row 1 — Hero grid (22% / 56% / 22%):**
- Left: PersonaCards — 5 mini cards, avatar block, name+city, hover highlights map dots
- Center: HeroMap — pulsating verdict stamp + D3 country silhouette + 200 animated dots
- Right: ObstacleCards — 5 mini cards, severity pill, centered title, threat-colored left border

**Row 2 — Analytics grid (22% / 56% / 22%):**
- Left: MarketStats — 5 stat rows (GDP, internet %, population, maturity badge, trend arrow)
- Center: RadarChart — Recharts 6-axis spider, filled polygon + dashed ideal + vertex score labels
- Right: CulturalFit — 56px score number + score label + 6 Hofstede bars with hover tooltip

**Row 3 — Entry Roadmap full width:**
- Horizontal timeline, gradient connecting line, animated traveling particle
- Phase nodes clickable — popup above node shows actions list

**Row 4 — Bottom Strip:**
- Top: 4 stat chips (Confidence, Time to revenue, Est. CAC, Sales motion)
- Left col: First Move card (teal left border, 16px text) + Wildcard mini card + Revisit mini card
- Center col: Generate Report button (full pulsating teal border, no card container)
- Right col: Competitors — rows with threat-colored left border + name + description

---

## Milestones

| Milestone | Status |
|-----------|--------|
| 0 — Setup | ✅ Complete |
| 1 — Agent Pipeline + SSE | ✅ Complete |
| 2 — Frontend | ✅ Complete |
| 3 — Polish & Deploy | 🔲 Next |

---

## Next Steps (Milestone 3)
1. Verify Agent 7 SSE flush fix works in live test (Pakistan dating app test running)
2. Test with 3 different product + market combinations
3. Fix any remaining bugs from live tests
4. Deploy backend on Railway or Render
5. Deploy frontend on Vercel
6. Write README.md
7. Demo runs end to end under 90 seconds

---

## Known Issues
- Agent 7 SSE flush bug — fix applied, awaiting verification
- KPI chips Time to revenue and Est. CAC may show — if Agent 6 returns null for optional fields
- TEST_MODE must be false before any live run

---

## Claude Code vs Claude Chat — Role Split

| | Claude Code | Claude Chat (this) |
|--|-------------|-------------------|
| Does | Writes and edits code | Plans, advises, reviews, writes prompts |
| Knows | CLAUDE.md | This file (CONTEXT.md) |

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
- PDF generation (Generate Report button is placeholder for now)
- Any feature not listed in CLAUDE.md
