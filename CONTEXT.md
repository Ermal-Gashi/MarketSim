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
| Frontend | HTML/CSS/JS — decided, vanilla no framework |
| Repo | Single monorepo, one folder |
| Environment | PyCharm on Windows, PowerShell terminal |
| Project path | `C:\Users\korab\PycharmProjects\MarketSim` |
| Agent 7 | Pure Python simulation layer — no Claude call |

---

## Current Project Structure

```
marketsim/
├── CLAUDE.md                          # Claude Code context
├── CONTEXT.md                         # This file — Claude chat context
├── README.md
├── .env                               # ANTHROPIC_API_KEY
├── .gitignore
├── main.py                            # FastAPI entry point
│
├── backend/
│   ├── requirements.txt
│   ├── routes/
│   │   └── simulate.py                # SSE streaming endpoint — not yet wired
│   ├── agents/
│   │   ├── product_analyst.py         # Agent 1 ✅
│   │   ├── market_data_fetcher.py     # Agent 2 ✅
│   │   ├── cultural_fit_scorer.py     # Agent 3 ✅
│   │   ├── persona_generator.py       # Agent 4 ✅
│   │   ├── obstacle_detector.py       # Agent 5 ✅
│   │   ├── synthesizer.py             # Agent 6 ✅
│   │   └── simulation_layer.py        # Agent 7 — planned, not built yet
│   ├── services/
│   │   ├── claude_client.py           # All Claude calls go through here
│   │   ├── world_bank_client.py       # World Bank API + household consumption
│   │   └── countries_client.py        # REST Countries API wrapper
│   └── data/
│       ├── hofstede.json              # Hofstede cultural dimensions — 112 countries
│       └── business_environment.json  # CPI, Ease of Business, Press Freedom, Political Stability — 102 countries
│
├── frontend/                          # Not built yet — Milestone 2
└── backend/tests/
    ├── test_services.py               # Tests for all services ✅
    └── test_agents.py                 # Tests for all agents ✅
```

---

## Agent Pipeline Summary

| # | Agent | Key Output | Status |
|---|-------|-----------|--------|
| 1 | Product Analyst | Value props, pricing tier, customer profile, optional enrichments | ✅ Complete |
| 2 | Market Data Fetcher | GDP, internet penetration, competitors, infrastructure, regional breakdown | ✅ Complete |
| 3 | Cultural Fit Scorer | Fit score 0-100, Hofstede dimension analysis, sales motion recommendation | ✅ Complete |
| 4 | Persona Generator | 5 archetypes with variance profiles for simulation layer | ✅ Complete |
| 5 | Obstacle Detector | 5 obstacles ordered by severity, business environment data grounded | ✅ Complete |
| 6 | Synthesizer | Go/Cautious Go/No-Go verdict, regional_weights, dot_intensity, radar_scores | ✅ Complete |
| 7 | Simulation Layer | 200 synthetic persona instances with conversion outcomes — pure Python, no Claude | 🔲 Planned |

All agents 1-6 return structured JSON. All Claude calls route through `claude_client.py`. No agent has persistent memory — context passed explicitly each call. Agent 7 uses no Claude call — pure Python logic rolling archetype variance profiles.

---

## External Data Sources

| Source | Purpose | Coverage |
|--------|---------|----------|
| World Bank API | GDP per capita, internet penetration, household consumption | Live API |
| REST Countries API | Country metadata, currency, languages | Live API |
| hofstede.json | Cultural dimension scores (PDI, IDV, MAS, UAI, LTO, IVR) | 112 countries |
| business_environment.json | CPI, Ease of Doing Business, Press Freedom, Political Stability | 102 countries |

Fallback: if APIs return no data, Claude estimates and flags with `data_source: "estimated"`.

---

## Frontend Visual Design Decisions

### Screen 1 — Input Form
- Product description text area
- Current market input
- Target market input
- Run Simulation button

### Screen 2 — Agent Progress
- Horizontal strip at top of page showing 7 agent pills lighting up as each completes
- "View agent network" button that opens a modal
- Modal shows semi-transparent neural network of all 7 agents in a circle
- Animated data packets travel between completed agents in the modal
- Report fades in below the strip as agents complete

### Screen 3 — Report
Two hero visuals:
1. **Animated country dot map** — country silhouette dynamically rendered based on user input. Dots spawn gradually in correct regional distribution from Agent 6 regional_weights. Dots represent synthetic instances of the 5 persona archetypes (Option 1 — honest simulation). High likelihood zones pulse brighter and denser. Dots fade to show abandonment. Verdict overlaid as transparent rectangle with colored corners only (not filled) — green/amber/red corners with single word GO / CAUTION / NO-GO visible through transparent center.
2. **Signal radar chart** — hexagonal spider chart showing 6 key market signals from Agent 6 radar_scores.

Remaining sections (to be designed during Milestone 2):
- Persona archetype cards (tappable, flip to variance profile)
- Obstacle matrix (severity vs time sensitivity scatter plot)
- Market entry roadmap (phased horizontal timeline)
- Critical assumptions
- Recommended first move + wildcard + revisit trigger

---

## Agent 7 — Simulation Layer Design

Agent 7 is pure Python — no Claude API call. It:
- Takes 5 persona archetypes from Agent 4 with their variance_profile objects
- Takes regional_weights and dot_intensity from Agent 6
- Generates ~200 synthetic instances by rolling key_variables randomly per instance
- Assigns each instance: archetype, city (weighted by regional_weights), conversion outcome (converted/evaluating/abandoned) based on tipping_point conditions
- Output feeds the frontend dot map animation

This is not random dot generation — every dot is a rolled variant of a real archetype with documented variance. Defensible methodology.

---

## Milestones

| Milestone | Status | Goal |
|-----------|--------|------|
| 0 — Setup | ✅ Complete | FastAPI runs, all APIs respond, Claude client working |
| 1 — Agent Pipeline | 🔄 In Progress | Agents 1-6 complete and tested. SSE pipeline wiring remaining. Agent 7 planned. |
| 2 — Frontend | 🔲 Not started | HTML/CSS/JS frontend with dot map, radar chart, agent network modal |
| 3 — Polish & Deploy | 🔲 Not started | Live URL, tested, demo ready in under 90 seconds |

---

## Next Steps (in order)

1. Wire all 6 agents into `simulate.py` SSE pipeline — completes Milestone 1
2. Build Agent 7 simulation layer — pure Python
3. Begin Milestone 2 frontend build
4. Design and build dot map hero visual
5. Design and build radar chart hero visual
6. Build agent network modal
7. Connect frontend to backend SSE

---

## Claude Code vs Claude Chat — Role Split

| | Claude Code | Claude Chat (this) |
|--|-------------|-------------------|
| **Does** | Writes and edits code | Plans, advises, reviews, writes prompts |
| **Knows** | CLAUDE.md | This file (CONTEXT.md) |
| **Gets** | Specific build instructions | Strategic and architectural questions |
| **Don't ask it** | What to build or why | To write files directly into the repo |

---

## How to Use This File

Paste the following at the start of a new Claude chat when you need to pick up where we left off:

> "Here is my project context, please read it before we continue: [paste CONTEXT.md contents]"

Update this file whenever a major decision is made or a milestone is completed.

---

## Things We Are NOT Building

- User authentication
- Saved simulation history
- Mobile responsive design
- More than 7 agents
- Any feature not already listed in CLAUDE.md or this file
