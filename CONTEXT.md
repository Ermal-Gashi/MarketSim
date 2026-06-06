# MarketSim — Claude Chat Context

Use this file to bring Claude (this chat) up to speed on the project at any point.

---

## What We Are Building
MarketSim is a multi-agent AI system that simulates market entry for any product into a new geographic or demographic market. User inputs a product description, current market, and target market. Six AI agents run sequentially and stream results to the frontend via SSE. Final output is a full market entry report with a Go/Cautious/No-Go verdict.

This is a solo hackathon project that will continue to be developed beyond the hackathon.

---

## Key Decisions Already Made

| Decision | Choice |
|----------|--------|
| Backend | Python + FastAPI |
| AI Model | `claude-sonnet-4-6` |
| Streaming | Server-Sent Events (SSE) via GET params |
| Frontend | To be decided at Milestone 2 — HTML/CSS or React |
| Repo | Single monorepo, one folder |
| Environment | PyCharm on Windows, PowerShell terminal |
| Project path | `C:\Users\korab\PycharmProjects\MarketSim` |

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
│   │   └── simulate.py                # SSE streaming endpoint
│   ├── agents/
│   │   ├── product_analyst.py         # Agent 1
│   │   ├── market_data_fetcher.py     # Agent 2
│   │   ├── cultural_fit_scorer.py     # Agent 3
│   │   ├── persona_generator.py       # Agent 4
│   │   ├── obstacle_detector.py       # Agent 5
│   │   └── synthesizer.py             # Agent 6
│   ├── services/
│   │   ├── claude_client.py           # All Claude calls go through here
│   │   ├── world_bank_client.py       # World Bank API wrapper
│   │   └── countries_client.py        # REST Countries API wrapper
│   └── data/
│       └── hofstede.json              # Hardcoded Hofstede cultural dimensions
│
└── frontend/                          # Not built yet — decided at Milestone 2
```

---

## Agent Pipeline Summary

| # | Agent | Key Output |
|---|-------|-----------|
| 1 | Product Analyst | Value props, pricing tier, customer profile |
| 2 | Market Data Fetcher | GDP, internet penetration, competitors, infrastructure |
| 3 | Cultural Fit Scorer | Fit score 0-100 with Hofstede-grounded explanation |
| 4 | Persona Generator | 5 synthetic customer persona cards |
| 5 | Obstacle Detector | Top 5 obstacles with severity ratings |
| 6 | Synthesizer | Go/Cautious/No-Go verdict + executive summary |

All agents return structured JSON. All Claude calls route through `claude_client.py`. No agent has persistent memory — context passed explicitly each call.

---

## External Data Sources

| Source | Purpose |
|--------|---------|
| World Bank API | GDP per capita, internet penetration |
| REST Countries API | Country metadata, currency, languages |
| hofstede.json | Cultural dimension scores — hardcoded for ~50 countries |

Fallback: if APIs return no data, Claude estimates and flags with `data_source: "estimated"`.

---

## Milestones

| Milestone | Status | Goal |
|-----------|--------|------|
| 0 — Setup | In progress | Directories created, FastAPI runs, APIs respond |
| 1 — Agent Pipeline | Not started | All 6 agents chain and stream via SSE |
| 2 — Frontend | Not started | To be scoped after Milestone 1 |
| 3 — Polish & Deploy | Not started | Live URL, tested, demo ready in under 90 seconds |

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
- More than 6 agents
- Any feature not already listed in CLAUDE.md
