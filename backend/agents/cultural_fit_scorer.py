import json
import logging
from pathlib import Path

from backend.services.claude_client import call_claude

logger = logging.getLogger(__name__)

_HOFSTEDE_PATH = Path(__file__).parent.parent / "data" / "hofstede.json"

MANDATORY_FIELDS = [
    "cultural_fit_score",
    "score_label",
    "dimension_analysis",
    "overall_explanation",
]

VALID_SCORE_LABELS = {
    "Excellent Fit", "Good Fit", "Moderate Fit", "Poor Fit", "Very Poor Fit"
}

SYSTEM_PROMPT = """You are a cross-cultural business strategist who combines Hofstede's cultural dimension framework with hands-on experience launching software products in international markets. You receive real Hofstede scores for a target country and a product profile, and you score how well that product will culturally resonate in that market.

Hofstede dimension guide (for your analysis):
- PDI (Power Distance): High = hierarchical, deferential to authority. Low = flat, egalitarian. Affects: who buys, how decisions are made, B2B vs B2C dynamics.
- IDV (Individualism): High = personal achievement, self-service, autonomy. Low = collectivist, group consensus, relationships before transactions.
- MAS (Masculinity): High = performance, competition, results. Low = quality of life, collaboration, work-life balance.
- UAI (Uncertainty Avoidance): High = need for rules, structure, proof, references. Low = tolerant of ambiguity, early adopter friendly.
- LTO (Long-Term Orientation): High = persistence, thrift, investment mindset. Low = short-term results, quick wins, tradition.
- IVR (Indulgence): High = enjoy life, spend freely, leisure. Low = restrained, duty-driven, frugal.

You MUST return a JSON object with EXACTLY these field names:

MANDATORY:
- "cultural_fit_score": integer 0-100 — overall cultural fit of this product in this market
- "score_label": string — MUST be exactly one of: "Excellent Fit", "Good Fit", "Moderate Fit", "Poor Fit", "Very Poor Fit"
- "dimension_analysis": array of EXACTLY 6 objects, one per dimension in this order: PDI, IDV, MAS, UAI, LTO, IVR. Each object must have:
    - "dimension": string — the dimension code (e.g. "PDI")
    - "score": integer — the country's score for this dimension
    - "implication": string — one specific sentence about how this dimension score affects adoption of THIS product in THIS market
- "overall_explanation": string — 2-3 sentences synthesising the fit score and the most decisive cultural factors

OPTIONAL (null if not clearly inferable):
- "messaging_recommendations": array of exactly 3 strings — specific copy or positioning angles tailored to this culture
- "sales_motion_recommendation": string or null — MUST start with one of: "PLG", "sales-led", "community-led", "hybrid" followed by a colon and one sentence explaining why
- "cultural_red_flags": array of strings or null — specific value props or features from this product that will actively repel or create friction in this market
- "cultural_tailwinds": array of strings or null — cultural factors that create genuine pull for this product in this market

Be specific. Reference actual dimension scores. Name real cultural dynamics, not generic platitudes. A score of 76 on UAI means something different for a no-code tool vs. an enterprise ERP.

Respond only with valid JSON. No preamble, no explanation, no markdown fences."""

USER_TEMPLATE = """TARGET MARKET: {country}

HOFSTEDE DIMENSION SCORES (data source: {data_source}):
- PDI (Power Distance):            {PDI}
- IDV (Individualism):             {IDV}
- MAS (Masculinity):               {MAS}
- UAI (Uncertainty Avoidance):     {UAI}
- LTO (Long-Term Orientation):     {LTO}
- IVR (Indulgence):                {IVR}

PRODUCT PROFILE (from Agent 1):
- Product name:     {product_name}
- Category:         {product_category}
- Pricing tier:     {pricing_tier}
- Value props:      {value_props}
- Customer profile: {customer_profile}
- Key differentiator: {differentiator}

MARKET CONTEXT (from Agent 2):
- Market maturity (for this category): {market_maturity}
- Tech adoption profile: {tech_adoption}
- Major local competitors: {competitors}

Score the cultural fit of this product in this market. Be specific to these dimension scores and this product."""


def _load_hofstede(country_name: str) -> tuple[dict, str]:
    """Return (scores_dict, data_source). Falls back to estimation if not found."""
    raw = json.loads(_HOFSTEDE_PATH.read_text(encoding="utf-8"))

    # Try exact match first, then case-insensitive
    entry = raw.get(country_name)
    if entry is None:
        lower = country_name.lower()
        for key, val in raw.items():
            if key.lower() == lower:
                entry = val
                break

    if entry is None:
        logger.warning("Hofstede data not found for '%s' — Claude will estimate", country_name)
        return {d: "unknown (Claude will estimate)" for d in ("PDI","IDV","MAS","UAI","LTO","IVR")}, "estimated"

    return entry, "hofstede.json"


def run(inputs: dict) -> dict:
    agent1 = inputs["agent1_output"]
    agent2 = inputs["agent2_output"]

    country = agent2.get("country_name", inputs.get("target_market", "Unknown"))
    hofstede, data_source = _load_hofstede(country)

    competitors = agent2.get("major_local_competitors") or []
    competitors_str = "; ".join(competitors) if competitors else "none identified"

    user_prompt = USER_TEMPLATE.format(
        country=country,
        data_source=data_source,
        PDI=hofstede.get("PDI", "unknown"),
        IDV=hofstede.get("IDV", "unknown"),
        MAS=hofstede.get("MAS", "unknown"),
        UAI=hofstede.get("UAI", "unknown"),
        LTO=hofstede.get("LTO", "unknown"),
        IVR=hofstede.get("IVR", "unknown"),
        product_name=agent1.get("product_name", "unknown"),
        product_category=agent1.get("product_category", "unknown"),
        pricing_tier=agent1.get("pricing_tier", "unknown"),
        value_props="; ".join(agent1.get("core_value_props", [])),
        customer_profile=agent1.get("current_customer_profile", "unknown"),
        differentiator=agent1.get("key_differentiator") or "not specified",
        market_maturity=agent2.get("market_maturity", "unknown"),
        tech_adoption=agent2.get("tech_adoption_profile") or "not specified",
        competitors=competitors_str,
    )

    result = call_claude(SYSTEM_PROMPT, user_prompt)
    result["data_source"] = data_source

    # --- Validate mandatory fields ---
    missing = [f for f in MANDATORY_FIELDS if f not in result]
    if missing:
        raise ValueError(f"Cultural Fit Scorer missing mandatory fields: {missing}")

    if result.get("score_label") not in VALID_SCORE_LABELS:
        raise ValueError(
            f"Invalid score_label '{result.get('score_label')}'. "
            f"Must be one of: {VALID_SCORE_LABELS}"
        )

    da = result.get("dimension_analysis")
    if not isinstance(da, list) or len(da) != 6:
        raise ValueError(
            f"dimension_analysis must be a list of exactly 6 objects, got {type(da)} len={len(da) if isinstance(da, list) else 'N/A'}"
        )

    logger.info(
        "Cultural Fit Scorer: %s in %s → %s (%s)",
        agent1.get("product_name"), country,
        result.get("cultural_fit_score"), result.get("score_label"),
    )
    return result
