# MarketSim — Claude Code Context

## What We Are Building
MarketSim is a multi-agent AI system that simulates market entry for any product into a new geographic or demographic market. A user inputs a product description, their current market, and a target market. Six AI agents run sequentially, each passing structured output to the next, and the final report is streamed to the frontend in real time.

This is a solo-built hackathon project. Keep code clean, well-commented, and avoid over-engineering.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI |
| AI | Anthropic Python SDK, model: `claude-sonnet-4-6` |
| Streaming | Server-Sent Events (SSE) via FastAPI StreamingResponse |
| Frontend | To be decided — HTML/CSS or React. Do not build frontend until instructed |
| External APIs | World Bank API, REST Countries API |
| Static Data | Hofstede cultural dimensions (hardcoded JSON file) |
| Environment | python-dotenv for .env management |

---

## Repository Structure

```
marketsim/
│
├── CLAUDE.md                          # This file
├── README.md                          
├── .env                               # API keys — never hardcode
├── .gitignore                         
│
├── backend/
│   ├── main.py                        # FastAPI entry point
│   ├── requirements.txt               
│   │
│   ├── routes/
│   │   └── simulate.py                # POST /api/simulate — SSE streaming endpoint
│   │
│   ├── agents/
│   │   ├── product_analyst.py         # Agent 1
│   │   ├── market_data_fetcher.py     # Agent 2
│   │   ├── cultural_fit_scorer.py     # Agent 3
│   │   ├── persona_generator.py       # Agent 4
│   │   ├── obstacle_detector.py       # Agent 5
│   │   └── synthesizer.py             # Agent 6
│   │
│   ├── services/
│   │   ├── claude_client.py           # All Claude API calls go through here
│   │   ├── world_bank_client.py       # World Bank API wrapper
│   │   └── countries_client.py        # REST Countries API wrapper
│   │
│   └── data/
│       └── hofstede.json              # Hofstede scores for ~50 countries
│
└── frontend/                          # To be built later — do not touch yet
```

---

## Environment Variables

Store in `.env` at root. Never hardcode.

```
ANTHROPIC_API_KEY=your_key_here
```

---

## Agent Pipeline

Agents run sequentially. Each agent receives all previous agent outputs as context. No persistent memory — all context passed explicitly per call. All agents return structured JSON.

| # | Agent | Input | Output |
|---|-------|-------|--------|
| 1 | Product Analyst | Product description + current market | Value props, pricing tier, customer profile |
| 2 | Market Data Fetcher | Target market name | GDP, penetration, competitors, infrastructure |
| 3 | Cultural Fit Scorer | Agent 1 + 2 + Hofstede data | Fit score 0-100 with explanation |
| 4 | Persona Generator | Agent 1 + 2 + 3 | 5 synthetic customer persona cards |
| 5 | Obstacle Detector | Agent 1 + 2 + 3 | Top 5 obstacles with severity |
| 6 | Synthesizer | All agent outputs | Go/Cautious/No-Go verdict + executive summary |

---

## Claude Client Rules

- All Claude calls go through `services/claude_client.py` — never call the SDK directly from agent files
- Model: `claude-sonnet-4-6`
- Max tokens: 2000 per call
- Every agent system prompt must end with: "Respond only with valid JSON. No preamble, no explanation, no markdown fences."
- Strip markdown fences from response before JSON parsing
- Retry once if JSON parsing fails before raising an error

---

## SSE Streaming

The backend streams progress to the frontend as each agent completes. SSE uses GET query params since EventSource does not support POST.

Event format:
```
data: {"agent": 1, "name": "Product Analyst", "status": "running"}
data: {"agent": 1, "name": "Product Analyst", "status": "done", "output": {...}}
...
data: {"agent": 6, "name": "Synthesizer", "status": "done", "output": {...}, "final": true}
```

---

## External Data Sources

| Source | Purpose | Docs |
|--------|---------|------|
| World Bank API | GDP per capita, internet penetration | https://api.worldbank.org/v2/ |
| REST Countries API | Country metadata, currency, languages | https://restcountries.com/v3.1/ |
| hofstede.json | Cultural dimension scores (hardcoded) | /backend/data/hofstede.json |

If an API returns no data for a country, fall back to Claude estimation and flag with `"data_source": "estimated"`.

---

## Error Handling

- Every agent wrapped in try/except
- On failure yield an SSE error event and stop pipeline gracefully
- Never let an unhandled exception crash the stream silently

---

## Coding Conventions

- Each agent file has one public function: `run(inputs: dict) -> dict`
- Use type hints throughout
- No print statements — use Python logging
- Keep agent files under 100 lines
- Prompts defined as constants at top of each agent file
- Never import one agent from another — orchestration only in `simulate.py`

---

## Milestones

### Milestone 0 — Setup
- FastAPI runs on localhost:8000
- `/health` returns `{"status": "ok"}`
- `.env` loads correctly
- Claude API responds to a test call
- World Bank and REST Countries APIs return data

### Milestone 1 — Agent Pipeline
- All 6 agents run and return valid JSON
- Agents chain correctly, each receiving prior outputs
- Full pipeline runs end to end with one hardcoded test input
- SSE streaming works and events appear in browser console

### Milestone 2 — Frontend
- To be scoped and built after Milestone 1 is complete
- Stack and layout will be decided at that point

### Milestone 3 — Polish & Demo Ready
- Tested with 3 different product + market combinations
- Deployed and running on a live URL
- Demo runs end to end in under 90 seconds

---

## Do Not Build Without Being Asked
- Frontend (until Milestone 2 is scoped)
- User authentication
- Saving or history of simulations
- More than 6 agents
- Anything not listed here
