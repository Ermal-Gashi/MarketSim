import json
import logging
from pathlib import Path

from backend.services.claude_client import call_claude
from backend.services.world_bank_client import get_household_consumption

logger = logging.getLogger(__name__)

_BIZ_ENV_PATH = Path(__file__).parent.parent / "data" / "business_environment.json"

VALID_CATEGORIES = {"Competitive", "Cultural", "Regulatory", "Economic", "Operational"}
VALID_SEVERITIES = {"Critical", "High", "Medium", "Low"}

MANDATORY_OBSTACLE_FIELDS = [
    "title",
    "category",
    "description",
    "severity",
    "affected_personas",
    "mitigation",
]

SYSTEM_PROMPT = """You are a seasoned market entry consultant who has closed deals and watched companies fail across emerging and developed markets worldwide. You have just reviewed a full intelligence brief on a specific product entering a specific country — product analysis, economic data, cultural fit scoring, buyer personas, and governance indicators.

Your job is to identify the 5 specific obstacles that will ACTUALLY kill or cripple this market entry. Not generic risks — every obstacle must be grounded in the data provided and tied to a named mechanism of failure.

MANDATORY DATA REFERENCES — you must explicitly use these in your analysis:
- Reference the CPI score (0-100) when discussing corruption, procurement opacity, or partner risk
- Reference the Ease of Doing Business score (0-100) when discussing operational setup, entity formation, or banking
- Reference the Press Freedom score (0-100) when discussing data risk, communications, or reputational exposure
- Reference the Political Stability score (0-100) when discussing macro market risk or investment horizon
- Reference household consumption per capita (USD) when discussing pricing sensitivity and willingness to pay
- Reference specific Hofstede dimension scores (e.g. "UAI of 76 means...") when discussing cultural obstacles
- Reference specific competitor names from the market data when discussing competitive obstacles
- Reference specific persona archetype names from Agent 4 when listing affected_personas

OUTPUT FORMAT — you MUST return a JSON object with EXACTLY one key: "obstacles" containing an array of EXACTLY 5 obstacle objects.

Order them from most severe to least: Critical first, then High, Medium, Low.

Each obstacle object MUST have these exact field names:
- "title": string — short, specific name for this obstacle (e.g. "LGPD Compliance Gate", "Runrun.it Price War", "AI Authority Conflict")
- "category": string — MUST be exactly one of: "Competitive", "Cultural", "Regulatory", "Economic", "Operational"
- "description": string — 2-3 sentences, specific and grounded in the data provided. Name the mechanism of failure. Do not be generic.
- "severity": string — MUST be exactly one of: "Critical", "High", "Medium", "Low"
- "affected_personas": array of strings — use the exact archetype_name values from the personas provided (e.g. "The Skeptical CTO")
- "mitigation": string — one concrete, actionable thing to do. Not "consider exploring" — tell them what to actually do.

Each obstacle SHOULD also include these optional fields (null if not clearly applicable):
- "time_sensitivity": string or null — when does this obstacle hit? Day-one, at scale, at renewal? Be specific.
- "cost_to_fix": string or null — rough effort or spend required (e.g. "Low — copy change only", "High — requires local legal entity and DPO appointment", "Medium — 3-6 months of localization work")
- "early_warning_signal": string or null — the leading indicator you would watch to know this obstacle is materializing before it kills you

Severity guide:
- Critical: Will stop market entry completely if not resolved before launch
- High: Will significantly limit growth ceiling or cause major pipeline loss
- Medium: Will create friction and slow growth but can be worked around
- Low: Worth monitoring; manageable with minor adjustments

Be specific. Be brutal. A market entry consultant who says "there may be some regulatory complexity" is useless. Name the law, the score, the competitor, the persona.

Respond only with valid JSON. No preamble, no explanation, no markdown fences."""

USER_TEMPLATE = """TARGET COUNTRY: {country}

GOVERNANCE & BUSINESS ENVIRONMENT DATA:
- CPI (Corruption Perceptions Index, 0-100 higher=cleaner): {cpi}
- Ease of Doing Business (0-100, higher=easier): {edb}
- Press Freedom Index (0-100, higher=freer): {pfi}
- Political Stability (0-100, higher=more stable): {ps}
- Household Consumption per Capita (USD, constant 2015): {consumption}

PRODUCT PROFILE (Agent 1):
- Product: {product_name} ({product_category})
- Pricing tier: {pricing_tier}
- Value props: {value_props}
- Business model: {business_model}
- Key differentiator: {differentiator}

MARKET DATA (Agent 2):
- GDP per capita: USD {gdp}
- Internet penetration: {internet}%
- Market maturity: {market_maturity}
- Languages: {languages}
- Payment infrastructure: {payment_infra}
- Major local competitors: {competitors}
- Regulatory notes: {regulatory_notes}
- Tech adoption profile: {tech_adoption}

CULTURAL FIT ANALYSIS (Agent 3):
- Fit score: {fit_score}/100 ({score_label})
- Dimension scores:
{dimension_summary}
- Cultural red flags: {red_flags}
- Cultural tailwinds: {tailwinds}
- Sales motion recommendation: {sales_motion}

BUYER PERSONAS (Agent 4) — use these exact archetype names in affected_personas:
{persona_summary}

Now identify the 5 specific obstacles that will actually determine whether this market entry succeeds or fails. Order by severity: Critical first."""


def _load_biz_env(country_name: str) -> dict:
    raw = json.loads(_BIZ_ENV_PATH.read_text(encoding="utf-8"))
    entry = raw.get(country_name)
    if entry is None:
        lower = country_name.lower()
        for k, v in raw.items():
            if k.lower() == lower:
                entry = v
                break
    return entry or {"cpi": None, "ease_of_business": None, "press_freedom": None, "political_stability": None}


def _fmt_list(items) -> str:
    if not items:
        return "none specified"
    if isinstance(items, list):
        return "; ".join(str(i) for i in items)
    return str(items)


def _fmt_dimensions(dimension_analysis: list) -> str:
    lines = []
    for d in dimension_analysis:
        lines.append(f"  [{d.get('dimension')} = {d.get('score')}] {d.get('implication')}")
    return "\n".join(lines)


def _fmt_personas(personas: list) -> str:
    lines = []
    for p in personas:
        lines.append(
            f"  - \"{p.get('archetype_name')}\" — {p.get('job_title')}, "
            f"{p.get('city')}, likelihood={p.get('likelihood_to_convert')}"
        )
    return "\n".join(lines)


def run(inputs: dict) -> dict:
    agent1 = inputs["agent1_output"]
    agent2 = inputs["agent2_output"]
    agent3 = inputs["agent3_output"]
    agent4 = inputs["agent4_output"]

    country = agent2.get("country_name", "Unknown")
    country_code = inputs.get("country_code", country[:2].upper())

    # Load business environment data
    biz_env = _load_biz_env(country)

    # Fetch household consumption from World Bank
    consumption_data = get_household_consumption(country_code)
    consumption = consumption_data.get("household_consumption_usd")
    consumption_str = f"USD {consumption:,.0f}" if consumption else "unavailable"

    personas = agent4.get("personas", [])

    user_prompt = USER_TEMPLATE.format(
        country=country,
        cpi=biz_env.get("cpi") if biz_env.get("cpi") is not None else "unavailable",
        edb=biz_env.get("ease_of_business") if biz_env.get("ease_of_business") is not None else "unavailable",
        pfi=biz_env.get("press_freedom") if biz_env.get("press_freedom") is not None else "unavailable",
        ps=biz_env.get("political_stability") if biz_env.get("political_stability") is not None else "unavailable",
        consumption=consumption_str,
        product_name=agent1.get("product_name", "unknown"),
        product_category=agent1.get("product_category", "unknown"),
        pricing_tier=agent1.get("pricing_tier", "unknown"),
        value_props=_fmt_list(agent1.get("core_value_props")),
        business_model=agent1.get("business_model") or "not specified",
        differentiator=agent1.get("key_differentiator") or "not specified",
        gdp=agent2.get("gdp_per_capita_usd", "unknown"),
        internet=agent2.get("internet_penetration_pct", "unknown"),
        market_maturity=agent2.get("market_maturity", "unknown"),
        languages=_fmt_list(agent2.get("languages")),
        payment_infra=agent2.get("payment_infrastructure") or "not specified",
        competitors=_fmt_list(agent2.get("major_local_competitors")),
        regulatory_notes=agent2.get("regulatory_notes") or "not specified",
        tech_adoption=agent2.get("tech_adoption_profile") or "not specified",
        fit_score=agent3.get("cultural_fit_score", "unknown"),
        score_label=agent3.get("score_label", "unknown"),
        dimension_summary=_fmt_dimensions(agent3.get("dimension_analysis", [])),
        red_flags=_fmt_list(agent3.get("cultural_red_flags")),
        tailwinds=_fmt_list(agent3.get("cultural_tailwinds")),
        sales_motion=agent3.get("sales_motion_recommendation") or "not specified",
        persona_summary=_fmt_personas(personas),
    )

    result = call_claude(SYSTEM_PROMPT, user_prompt, max_tokens=4000)

    # Validate
    obstacles = result.get("obstacles")
    if not isinstance(obstacles, list) or len(obstacles) != 5:
        raise ValueError(
            f"Obstacle Detector must return exactly 5 obstacles, got "
            f"{len(obstacles) if isinstance(obstacles, list) else type(obstacles)}"
        )

    for i, obs in enumerate(obstacles):
        missing = [f for f in MANDATORY_OBSTACLE_FIELDS if f not in obs]
        if missing:
            raise ValueError(f"Obstacle {i+1} missing mandatory fields: {missing}")

        if obs.get("category") not in VALID_CATEGORIES:
            raise ValueError(
                f"Obstacle {i+1} invalid category '{obs.get('category')}'. "
                f"Must be one of: {VALID_CATEGORIES}"
            )
        if obs.get("severity") not in VALID_SEVERITIES:
            raise ValueError(
                f"Obstacle {i+1} invalid severity '{obs.get('severity')}'. "
                f"Must be one of: {VALID_SEVERITIES}"
            )

    logger.info("Obstacle Detector: identified %d obstacles for %s", len(obstacles), country)
    return result
