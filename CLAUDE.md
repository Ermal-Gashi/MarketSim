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
└── frontend/                          # React + Vite app — Milestone 2
    ├── index.html
    ├── vite.config.js
    ├── package.json
    ├── tailwind.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── components/
        │   ├── InputForm.jsx           # Section 1
        │   ├── AgentProgressBar.jsx    # Section 2 — top strip
        │   ├── AgentNetworkModal.jsx   # Section 2 — neural network modal
        │   ├── HeroMap.jsx             # Section 3 — animated country dot map
        │   ├── RadarChart.jsx          # Section 3 — signal radar chart
        │   ├── PersonaCards.jsx        # Section 4 — flippable persona cards
        │   ├── ObstacleMatrix.jsx      # Section 5 — severity scatter plot
        │   ├── EntryRoadmap.jsx        # Section 6 — phased timeline
        │   └── VerdictSummary.jsx      # Section 7 — assumptions + first move
        ├── hooks/
        │   └── useSimulation.js        # SSE connection + state management
        └── styles/
            └── index.css
```

---

## Environment Variables

Store in `.env` at root. Never hardcode.

```
ANTHROPIC_API_KEY=your_key_here
```

---

## Agent Pipeline — All Complete ✅

Agents run sequentially. Each agent receives all previous agent outputs as context. No persistent memory — all context passed explicitly per call. All agents return structured JSON.

| # | Agent | Input | Output | Status |
|---|-------|-------|--------|--------|
| 1 | Product Analyst | Product description + current market | Value props, pricing tier, customer profile, optional enrichments | ✅ |
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
All agent timeouts: 300 seconds
CORS: enabled for all origins

Event format:
```
data: {"agent": N, "name": "Agent Name", "status": "running"}
data: {"agent": N, "name": "Agent Name", "status": "done", "output": {...}}
data: {"agent": 7, "name": "Simulation Layer", "status": "done", "output": {...}, "final": true, "complete_report": {...}}
```

Final event `complete_report` contains: product_description, current_market, target_market, agent1_output through agent7_output.

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

## Frontend — Milestone 2

### Overview
The frontend is a single scrollable page divided into clearly defined sections. It is built with React + Vite. Do not use any other framework. Styling is done exclusively with Tailwind CSS utility classes — do not write custom CSS files unless absolutely necessary for animations. The page has a dark theme.

### Page Structure — One Scrollable Page with 7 Sections

```
Section 1 — Input Form        (full screen, centered)
Section 2 — Agent Progress    (sticky top bar + modal button)
Section 3 — Hero Visuals      (dot map + radar chart side by side)
Section 4 — Persona Cards     (horizontal scroll of 5 flippable cards)
Section 5 — Obstacle Matrix   (severity vs time sensitivity scatter plot)
Section 6 — Entry Roadmap     (phased horizontal timeline)
Section 7 — Verdict Summary   (assumptions + first move + wildcard)
```

Sections 2-7 are hidden until the simulation completes. They fade in as agents complete.

### Section 1 — Input Form
- Full screen centered layout
- MarketSim logo/wordmark at top
- Three inputs: product description (textarea), current market (text input), target market (text input)
- Large "Run Simulation" button
- On submit: hide Section 1, show Section 2, open SSE connection via useSimulation hook

### Section 2 — Agent Progress
- Sticky horizontal bar at the top of the page visible throughout scrolling
- Shows 7 small agent pills in a row — dim when waiting, pulsing green when running, solid green when done
- "View agent network" button on the right of the bar
- Clicking the button opens the Agent Network Modal
- Agent Network Modal: semi-transparent dark overlay, 7 agent nodes arranged in a circle connected by lines, animated data packets travel between completed nodes, agents activate sequentially as SSE events arrive, close by clicking outside or X button

### Section 3 — Hero Visuals (two side by side)

**Left — Animated Country Dot Map (D3)**
- Render the country silhouette from GeoJSON using D3-geo
- Country data loaded from a public GeoJSON source or bundled file
- 200 dots from Agent 7 instances spawn gradually using spawn_delay_ms
- Dot color by conversion_outcome: converted=green, evaluating=amber, abandoned=red/dim
- Dot size and pulse_intensity controls brightness and animation
- Verdict overlay: transparent rectangle with colored corners only (not filled) — corners drawn in green/amber/red matching verdict, single word GO / CAUTIOUS / NO-GO in center
- Clicking a dot shows a popup with: avatar silhouette (based on avatar_style), display_name, job_title, archetype_label, conversion_outcome badge, outcome_reason, deciding_factor

**Right — Signal Radar Chart (Recharts)**
- Hexagonal radar/spider chart
- 6 axes from Agent 6 radar_scores: Market growth, Cultural fit, Internet penetration, Political stability, Ease of business, Corruption index
- Filled polygon showing scores, dashed outline showing ideal (80 on all axes)
- Color coded fill — green if average above 60, amber if 40-60, red if below 40

### Section 4 — Persona Cards
- 5 cards in a horizontal scrollable row
- Each card shows front face by default: avatar initial circle, name+age, job title, city, likelihood badge (green/amber/red)
- Click/tap card to flip to back face showing variance profile: conversion range, key variables, tipping points
- Cards animate in one by one when Section 3 is visible

### Section 5 — Obstacle Matrix
- Scatter plot with severity on Y axis and time sensitivity on X axis
- 5 dots — one per obstacle — sized by severity (Critical=largest)
- Color coded: Critical=red, High=orange, Medium=amber, Low=green
- Hover/click shows obstacle title, description, mitigation

### Section 6 — Entry Roadmap
- Horizontal timeline with 3-4 phases from Agent 6 market_entry_sequence
- Each phase has: phase number circle, phase name, timeframe, list of actions
- Phases connected by a line — color progresses from red (legal/compliance) to green (scale)
- Animate in left to right when section scrolls into view

### Section 7 — Verdict Summary
- Three critical assumptions as numbered cards each with assumption text and consequence_if_false
- Recommended first move as a highlighted call-to-action card
- Biggest wildcard and revisit trigger as smaller info cards side by side
- Time to first revenue and estimated CAC as stat callouts

### useSimulation Hook
- Opens EventSource connection to `/api/simulate` with query params
- Parses each SSE event and updates state
- Exposes: agentStatuses (array of 7), isRunning, isComplete, completeReport, error
- On final event sets isComplete=true and stores completeReport
- On error event sets error message and stops

### Coding Conventions — Frontend
- One component per file
- Props typed with PropTypes
- No inline styles — Tailwind classes only
- All D3 code inside useEffect with proper cleanup
- All chart data derived from completeReport in the component, not in the hook
- Console.log allowed during development for debugging SSE events

---

## Milestones

### Milestone 0 — Setup ✅
### Milestone 1 — Agent Pipeline + SSE ✅
### Milestone 2 — Frontend 🔲
Build order:
1. Scaffold React + Vite + Tailwind
2. useSimulation hook
3. Section 1 — Input Form
4. Section 2 — Agent Progress bar + modal
5. Section 3 — Dot map + radar chart
6. Section 4 — Persona cards
7. Section 5 — Obstacle matrix
8. Section 6 — Entry roadmap
9. Section 7 — Verdict summary

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
