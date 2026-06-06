import logging

from backend.services.claude_client import call_claude

logger = logging.getLogger(__name__)

MANDATORY_PERSONA_FIELDS = [
    "archetype_name",
    "name",
    "age",
    "job_title",
    "city",
    "company_size",
    "why_they_buy",
    "what_stops_them",
    "how_they_discover",
    "likelihood_to_convert",
    "variance_profile",
]

VARIANCE_PROFILE_FIELDS = [
    "conversion_range",
    "key_variables",
    "tipping_point_to_high",
    "tipping_point_to_low",
]

VALID_LIKELIHOOD = {"High", "Medium", "Low"}

SYSTEM_PROMPT = """You are a behavioral economist and ethnographic researcher who specialises in building buyer archetypes for products entering new international markets. You have just received rich economic, cultural, and competitive intelligence about a target market from a multi-agent analysis pipeline.

Your job is to construct 5 highly realistic, deeply grounded buyer personas for this specific product in this specific market. These are NOT generic marketing personas — every detail must be rooted in the cultural dimensions, regional breakdown, competitive landscape, and market maturity data you have been given.

DIVERSITY RULES — you must follow all of these without exception:
1. The 5 personas must span at least 3 different cities drawn from the regional breakdown in the market data
2. likelihood_to_convert distribution: at least 1 "High", at least 2 "Medium", at least 1 "Low"
3. Include both decision makers (budget authority) and champions (influence without signing power)
4. Age range across all 5 personas must span at least 15 years
5. No two personas may share the same job title

GROUNDING RULES:
- Names must be realistic and culturally appropriate for the target market
- Cities must come from the regional breakdown provided, not invented
- why_they_buy must reference specific value props from the product data
- what_stops_them must be anchored in specific Hofstede dimension findings or market barriers identified
- how_they_discover must reflect real channels that exist and are used in this market

CONCISENESS RULES — strictly enforced to keep the response within token limits:
- "why_they_buy": maximum 2 sentences
- "what_stops_them": maximum 2 sentences
- "conversation_starter": maximum 2 sentences
- All other string fields: be specific but tight — one punchy sentence is better than three vague ones

You MUST return a JSON object with EXACTLY one key: "personas" — containing an array of EXACTLY 5 persona objects.

Each persona object MUST have these exact field names:
- "archetype_name": string — a punchy label capturing their mindset (e.g. "The Skeptical CTO", "The Overwhelmed Team Lead")
- "name": string — a realistic local first + last name
- "age": integer
- "job_title": string — specific role, no two personas may share this
- "city": string — must come from the regional breakdown data
- "company_size": string — e.g. "20-50 employees", "200-500 employees"
- "why_they_buy": string — their specific motivation, tied to the product's value props and their cultural/professional context
- "what_stops_them": string — the specific friction point, grounded in cultural dimension analysis or market barriers
- "how_they_discover": string — the realistic channel or moment where they find this product in this market
- "likelihood_to_convert": string — MUST be exactly one of: "High", "Medium", "Low"
- "variance_profile": object with EXACTLY these fields:
    - "conversion_range": string — e.g. "Low to High" — full range possible for this archetype
    - "key_variables": array of 3-5 strings — the specific factors that push this archetype toward or away from converting
    - "tipping_point_to_high": string — the exact condition that makes this archetype a High converter
    - "tipping_point_to_low": string — the exact condition that kills the deal for this archetype

Each persona SHOULD also include these optional fields (set to null if cannot be reasonably inferred):
- "conversation_starter": string or null — the exact opening line a salesperson should use with this person in this market
- "deal_breaker": string or null — the single thing that kills the deal instantly
- "influencers": array of strings or null — specific roles that must also be convinced before they sign
- "time_to_close": string or null — realistic sales cycle estimate for this archetype in this market

Be specific. Be opinionated. Make each persona feel like a real person you have interviewed.

Respond only with valid JSON. No preamble, no explanation, no markdown fences."""

USER_TEMPLATE = """TARGET MARKET: {country}

PRODUCT (Agent 1):
- Name: {product_name}
- Category: {product_category}
- Pricing tier: {pricing_tier}
- Core value props: {value_props}
- Current customer profile: {customer_profile}
- Key differentiator: {differentiator}
- Business model: {business_model}

MARKET DATA (Agent 2):
- GDP per capita: USD {gdp}
- Internet penetration: {internet}%
- Population: {population}
- Market maturity (for this category): {market_maturity}
- Languages: {languages}
- Major local competitors: {competitors}
- Regional breakdown / best beachheads: {regional_breakdown}
- Tech adoption profile: {tech_adoption}

CULTURAL FIT ANALYSIS (Agent 3):
- Cultural fit score: {fit_score}/100 ({score_label})
- Overall explanation: {explanation}
- Key dimension findings:
{dimension_summary}
- Cultural tailwinds: {tailwinds}
- Cultural red flags: {red_flags}
- Messaging recommendations: {messaging}

Now build 5 deeply grounded, diverse personas for this product in this market. Follow all diversity and grounding rules exactly."""


def _fmt_dimensions(dimension_analysis: list) -> str:
    lines = []
    for d in dimension_analysis:
        lines.append(f"  [{d.get('dimension')} {d.get('score')}] {d.get('implication')}")
    return "\n".join(lines)


def _fmt_list(items) -> str:
    if not items:
        return "none specified"
    if isinstance(items, list):
        return "; ".join(str(i) for i in items)
    return str(items)


def run(inputs: dict) -> dict:
    agent1 = inputs["agent1_output"]
    agent2 = inputs["agent2_output"]
    agent3 = inputs["agent3_output"]

    country = agent2.get("country_name", "Unknown")

    user_prompt = USER_TEMPLATE.format(
        country=country,
        product_name=agent1.get("product_name", "unknown"),
        product_category=agent1.get("product_category", "unknown"),
        pricing_tier=agent1.get("pricing_tier", "unknown"),
        value_props=_fmt_list(agent1.get("core_value_props")),
        customer_profile=agent1.get("current_customer_profile", "unknown"),
        differentiator=agent1.get("key_differentiator") or "not specified",
        business_model=agent1.get("business_model") or "not specified",
        gdp=agent2.get("gdp_per_capita_usd", "unknown"),
        internet=agent2.get("internet_penetration_pct", "unknown"),
        population=agent2.get("population", "unknown"),
        market_maturity=agent2.get("market_maturity", "unknown"),
        languages=_fmt_list(agent2.get("languages")),
        competitors=_fmt_list(agent2.get("major_local_competitors")),
        regional_breakdown=agent2.get("regional_breakdown") or "not specified",
        tech_adoption=agent2.get("tech_adoption_profile") or "not specified",
        fit_score=agent3.get("cultural_fit_score", "unknown"),
        score_label=agent3.get("score_label", "unknown"),
        explanation=agent3.get("overall_explanation", "not available"),
        dimension_summary=_fmt_dimensions(agent3.get("dimension_analysis", [])),
        tailwinds=_fmt_list(agent3.get("cultural_tailwinds")),
        red_flags=_fmt_list(agent3.get("cultural_red_flags")),
        messaging=_fmt_list(agent3.get("messaging_recommendations")),
    )

    result = call_claude(SYSTEM_PROMPT, user_prompt, max_tokens=4000)

    # --- Validate ---
    personas = result.get("personas")
    if not isinstance(personas, list) or len(personas) != 5:
        raise ValueError(
            f"Persona Generator must return exactly 5 personas, got "
            f"{len(personas) if isinstance(personas, list) else type(personas)}"
        )

    for i, persona in enumerate(personas):
        missing = [f for f in MANDATORY_PERSONA_FIELDS if f not in persona]
        if missing:
            raise ValueError(f"Persona {i+1} missing mandatory fields: {missing}")

        likelihood = persona.get("likelihood_to_convert")
        if likelihood not in VALID_LIKELIHOOD:
            raise ValueError(
                f"Persona {i+1} has invalid likelihood_to_convert '{likelihood}'. "
                f"Must be one of: {VALID_LIKELIHOOD}"
            )

        vp = persona.get("variance_profile")
        if not isinstance(vp, dict):
            raise ValueError(f"Persona {i+1} variance_profile must be an object, got {type(vp)}")
        missing_vp = [f for f in VARIANCE_PROFILE_FIELDS if f not in vp]
        if missing_vp:
            raise ValueError(f"Persona {i+1} variance_profile missing fields: {missing_vp}")

    logger.info("Persona Generator: built %d personas for %s", len(personas), country)
    return result
