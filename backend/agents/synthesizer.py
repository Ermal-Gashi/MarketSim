import logging

from backend.services.claude_client import call_claude

logger = logging.getLogger(__name__)

RADAR_KEYS = {"Market growth", "Cultural fit", "Internet penetration",
              "Political stability", "Ease of business", "Corruption index"}

VALID_VERDICTS = {"Go", "Cautious Go", "No-Go"}

MANDATORY_FIELDS = [
    "verdict", "verdict_reason", "confidence_score", "executive_summary",
    "signal_scorecard", "critical_assumptions", "recommended_first_move",
    "regional_weights", "dot_intensity", "radar_scores",
]

SYSTEM_PROMPT = """You are a senior market entry partner at a top-tier strategy firm. You have read every intelligence report in this brief — product analysis, economic data, cultural scoring, buyer personas, obstacles, and governance indicators. You must now make a single, committed recommendation.

ANTI-HEDGING RULES — violating any of these makes your output worthless:
1. "Cautious Go" is NOT a safe default. It must be justified by specific, named conflicting evidence — one strong signal pulling toward Go and one strong signal pulling toward No-Go. If you cannot name both, choose Go or No-Go.
2. If the cultural fit score is above 65 AND no Critical severity obstacle exists, your default position is Go unless you can name a specific overriding factor.
3. If any Critical obstacle cannot be resolved within 60 days with the resources a typical early-stage company has, your default position is No-Go.
4. The confidence_score must be honest — 45 is acceptable, 50 as a hedge is not. Score it like a portfolio manager marking a position.
5. verdict_reason must name the single most important factor that determined the verdict. One sentence. No hedging words ("may", "could", "potentially", "might").

You MUST return a JSON object with EXACTLY these field names:

MANDATORY:
- "verdict": string — MUST be exactly one of: "Go", "Cautious Go", "No-Go"
- "verdict_reason": string — one sharp sentence naming the decisive factor. No hedge words.
- "confidence_score": integer 0-100 — your conviction in this verdict
- "executive_summary": string — 3-4 sentences covering the full picture: market opportunity, key risk, cultural posture, and recommended stance
- "signal_scorecard": array of objects, each with:
    - "signal": string — a specific named signal from the data (e.g. "UAI score 76 requires reference-first sales motion")
    - "direction": string — MUST be exactly one of: "positive", "neutral", "negative"
    - "weight": string — MUST be exactly one of: "High", "Medium", "Low"
- "critical_assumptions": array of EXACTLY 3 objects, each with:
    - "assumption": string — a specific thing that must be true for the verdict to hold
    - "consequence_if_false": string — what happens to the verdict if this assumption is wrong
- "recommended_first_move": string — the single most important action to take in the next 30 days. Specific, not generic.
- "regional_weights": object — keys are region/city names from the market data, integer values that MUST sum to exactly 100. Based on regional breakdown and persona city concentration. This feeds a dot map.
- "dot_intensity": object — SAME keys as regional_weights, integer values 0-100 showing estimated conversion likelihood intensity per region. These do NOT need to sum to 100. This feeds a dot pulse animation.
- "radar_scores": object — MUST have EXACTLY these 6 keys with integer scores 0-100:
    - "Market growth": score reflecting market growth trajectory for this category
    - "Cultural fit": the cultural fit score from Agent 3
    - "Internet penetration": normalized from the percentage (e.g. 84% = 84)
    - "Political stability": the normalized political stability score (0-100)
    - "Ease of business": the ease of doing business score (0-100)
    - "Corruption index": the CPI score (0-100)

OPTIONAL (null if not clearly applicable):
- "time_to_first_revenue": string or null — realistic estimate given the sales cycle lengths from persona data
- "estimated_cac": string or null — rough customer acquisition cost estimate given the sales motion required
- "biggest_wildcard": string or null — the single factor most likely to make this verdict wrong in either direction
- "revisit_trigger": string or null — the specific event or metric that should trigger a verdict re-evaluation
- "market_entry_sequence": array or null — ordered phases, each with:
    - "phase_name": string
    - "timeframe": string
    - "actions": array of strings (3-5 specific actions per phase)

Respond only with valid JSON. No preamble, no explanation, no markdown fences."""

USER_TEMPLATE = """PRODUCT: {product_name} ({product_category}) — {pricing_tier} tier
MARKET: {country}

GOVERNANCE SCORES:
- Cultural Fit Score (Agent 3): {fit_score}/100 ({score_label})
- CPI (Corruption, 0-100): {cpi}
- Ease of Doing Business (0-100): {edb}
- Press Freedom (0-100): {pfi}
- Political Stability (0-100): {ps}
- Internet Penetration: {internet}%
- GDP per Capita: USD {gdp}
- Household Consumption per Capita: USD {consumption}

PRODUCT PROFILE (Agent 1):
- Value props: {value_props}
- Business model: {business_model}
- Key differentiator: {differentiator}
- Current customer: {customer_profile}

MARKET DATA (Agent 2):
- Market maturity: {market_maturity}
- Payment infrastructure: {payment_infra}
- Competitors: {competitors}
- Regional breakdown: {regional_breakdown}
- Tech adoption: {tech_adoption}

CULTURAL ANALYSIS (Agent 3):
- Score: {fit_score}/100 ({score_label})
- Explanation: {fit_explanation}
- Dimensions:
{dimension_summary}
- Tailwinds: {tailwinds}
- Red flags: {red_flags}
- Sales motion: {sales_motion}

PERSONAS (Agent 4) — {persona_count} personas across cities: {persona_cities}
Likelihood breakdown: {likelihood_summary}

OBSTACLES (Agent 5):
{obstacle_summary}

Now synthesise all of this into a single committed verdict. Apply the anti-hedging rules strictly. The regional_weights and dot_intensity must reflect the actual persona city distribution and conversion likelihoods from the data above."""


def _fmt_list(items) -> str:
    if not items:
        return "none specified"
    if isinstance(items, list):
        return "; ".join(str(i) for i in items)
    return str(items)


def _fmt_dimensions(dimension_analysis: list) -> str:
    return "\n".join(
        f"  [{d.get('dimension')} = {d.get('score')}] {d.get('implication')}"
        for d in dimension_analysis
    )


def _fmt_obstacles(obstacles: list) -> str:
    lines = []
    for o in obstacles:
        lines.append(
            f"  [{o.get('severity')}] [{o.get('category')}] {o.get('title')}: "
            f"{o.get('description', '')[:200]}"
        )
    return "\n".join(lines)


def _fmt_likelihood_summary(personas: list) -> str:
    counts = {"High": 0, "Medium": 0, "Low": 0}
    for p in personas:
        l = p.get("likelihood_to_convert", "")
        if l in counts:
            counts[l] += 1
    return f"High={counts['High']}, Medium={counts['Medium']}, Low={counts['Low']}"


def run(inputs: dict) -> dict:
    agent1 = inputs["agent1_output"]
    agent2 = inputs["agent2_output"]
    agent3 = inputs["agent3_output"]
    agent4 = inputs["agent4_output"]
    agent5 = inputs["agent5_output"]

    country = agent2.get("country_name", "Unknown")
    personas = agent4.get("personas", [])
    obstacles = agent5.get("obstacles", [])

    # Pull governance scores — may come pre-loaded or need to be passed
    biz_env = inputs.get("biz_env", {})
    cpi = biz_env.get("cpi", "unavailable")
    edb = biz_env.get("ease_of_business", "unavailable")
    pfi = biz_env.get("press_freedom", "unavailable")
    ps = biz_env.get("political_stability", "unavailable")
    consumption = inputs.get("household_consumption_usd", "unavailable")

    persona_cities = ", ".join(
        f"{p.get('city')} ({p.get('likelihood_to_convert')})"
        for p in personas
    )

    user_prompt = USER_TEMPLATE.format(
        product_name=agent1.get("product_name", "unknown"),
        product_category=agent1.get("product_category", "unknown"),
        pricing_tier=agent1.get("pricing_tier", "unknown"),
        country=country,
        fit_score=agent3.get("cultural_fit_score", "unknown"),
        score_label=agent3.get("score_label", "unknown"),
        cpi=cpi,
        edb=edb,
        pfi=pfi,
        ps=ps,
        internet=agent2.get("internet_penetration_pct", "unknown"),
        gdp=agent2.get("gdp_per_capita_usd", "unknown"),
        consumption=consumption,
        value_props=_fmt_list(agent1.get("core_value_props")),
        business_model=agent1.get("business_model") or "not specified",
        differentiator=agent1.get("key_differentiator") or "not specified",
        customer_profile=agent1.get("current_customer_profile", "unknown"),
        market_maturity=agent2.get("market_maturity", "unknown"),
        payment_infra=agent2.get("payment_infrastructure") or "not specified",
        competitors=_fmt_list(agent2.get("major_local_competitors")),
        regional_breakdown=agent2.get("regional_breakdown") or "not specified",
        tech_adoption=agent2.get("tech_adoption_profile") or "not specified",
        fit_explanation=agent3.get("overall_explanation", "not available"),
        dimension_summary=_fmt_dimensions(agent3.get("dimension_analysis", [])),
        tailwinds=_fmt_list(agent3.get("cultural_tailwinds")),
        red_flags=_fmt_list(agent3.get("cultural_red_flags")),
        sales_motion=agent3.get("sales_motion_recommendation") or "not specified",
        persona_count=len(personas),
        persona_cities=persona_cities,
        likelihood_summary=_fmt_likelihood_summary(personas),
        obstacle_summary=_fmt_obstacles(obstacles),
    )

    result = call_claude(SYSTEM_PROMPT, user_prompt, max_tokens=4000)

    # ── Validation ────────────────────────────────────────────────────────
    missing = [f for f in MANDATORY_FIELDS if f not in result]
    if missing:
        raise ValueError(f"Synthesizer missing mandatory fields: {missing}")

    if result["verdict"] not in VALID_VERDICTS:
        raise ValueError(
            f"Invalid verdict '{result['verdict']}'. Must be one of: {VALID_VERDICTS}"
        )

    rw = result.get("regional_weights", {})
    if not isinstance(rw, dict) or not rw:
        raise ValueError("regional_weights must be a non-empty dict")
    rw_sum = sum(rw.values())
    if rw_sum != 100:
        raise ValueError(f"regional_weights values must sum to 100, got {rw_sum}")

    rs = result.get("radar_scores", {})
    if set(rs.keys()) != RADAR_KEYS:
        missing_keys = RADAR_KEYS - set(rs.keys())
        extra_keys = set(rs.keys()) - RADAR_KEYS
        raise ValueError(
            f"radar_scores must have exactly these keys: {RADAR_KEYS}. "
            f"Missing: {missing_keys}. Extra: {extra_keys}"
        )

    ca = result.get("critical_assumptions", [])
    if not isinstance(ca, list) or len(ca) != 3:
        raise ValueError(
            f"critical_assumptions must be a list of exactly 3 items, got "
            f"{len(ca) if isinstance(ca, list) else type(ca)}"
        )

    logger.info(
        "Synthesizer: %s in %s — verdict=%s confidence=%s",
        agent1.get("product_name"), country,
        result.get("verdict"), result.get("confidence_score"),
    )
    return result
