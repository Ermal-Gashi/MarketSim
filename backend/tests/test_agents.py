"""
Run with:
    .venv\\Scripts\\python -m backend.tests.test_agents
"""
import json
import sys

from dotenv import load_dotenv

load_dotenv()

AGENT1_INPUT = {
    "product_description": (
        "A project management tool for remote teams that integrates with Slack "
        "and automates task assignment"
    ),
    "current_market": "United States",
}

MANDATORY_FIELDS = {
    "product_name": str,
    "core_value_props": list,
    "pricing_tier": str,
    "product_category": str,
    "current_customer_profile": str,
}

OPTIONAL_FIELDS = ["key_differentiator", "business_model", "maturity_stage"]

VALID_PRICING_TIERS = {"free", "low", "mid", "high", "enterprise"}
VALID_MATURITY_STAGES = {"idea", "early", "growth", "mature", None}


def check_agent1() -> bool:
    from backend.agents.product_analyst import run

    print("\n--- Agent 1: Product Analyst ---")
    print(f"Input:\n{json.dumps(AGENT1_INPUT, indent=2)}\n")

    try:
        result = run(AGENT1_INPUT)
    except ValueError as exc:
        print(f"[FAIL] Validation error: {exc}")
        return False
    except Exception as exc:
        print(f"[FAIL] run() raised {type(exc).__name__}: {exc}")
        return False

    errors = []

    # --- Mandatory field checks ---
    for field, expected_type in MANDATORY_FIELDS.items():
        if field not in result:
            errors.append(f"missing mandatory field '{field}'")
        elif not isinstance(result[field], expected_type):
            errors.append(
                f"'{field}' should be {expected_type.__name__}, got {type(result[field]).__name__}"
            )

    if "core_value_props" in result and isinstance(result["core_value_props"], list):
        if len(result["core_value_props"]) != 3:
            errors.append(
                f"'core_value_props' must have exactly 3 items, got {len(result['core_value_props'])}"
            )

    if "pricing_tier" in result and result["pricing_tier"] not in VALID_PRICING_TIERS:
        errors.append(
            f"'pricing_tier' must be one of {VALID_PRICING_TIERS}, got '{result['pricing_tier']}'"
        )

    if "maturity_stage" in result and result["maturity_stage"] not in VALID_MATURITY_STAGES:
        errors.append(
            f"'maturity_stage' must be one of {VALID_MATURITY_STAGES}, got '{result['maturity_stage']}'"
        )

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return False

    # --- Print mandatory results ---
    print("Mandatory fields:")
    for field in MANDATORY_FIELDS:
        print(f"  {field}: {result[field]}")

    # --- Print optional results ---
    print("\nOptional fields:")
    for field in OPTIONAL_FIELDS:
        value = result.get(field, "(not returned)")
        print(f"  {field}: {value}")

    print("\n[PASS] Agent 1 returned valid output with all mandatory fields.")
    return True


# Hardcoded Agent 1 output for a project management SaaS tool
AGENT1_OUTPUT_STUB = {
    "product_name": "TaskFlow",
    "core_value_props": [
        "Automates task assignment based on team member workload and skills, cutting PM overhead by 40%",
        "Native Slack integration means zero context switching — updates surface where the team already lives",
        "Real-time workload visibility across distributed time zones prevents burnout and deadline slippage",
    ],
    "pricing_tier": "mid",
    "product_category": "productivity",
    "current_customer_profile": (
        "Engineering and ops managers at 20-200 person remote-first companies who are drowning in "
        "Slack threads and missed deadlines caused by manual task delegation."
    ),
    "key_differentiator": "AI-driven auto-assignment that learns team capacity over time",
    "business_model": "SaaS subscription",
    "maturity_stage": "early",
}

AGENT2_MANDATORY_FIELDS = {
    "country_name": str,
    "gdp_per_capita_usd": (int, float),
    "internet_penetration_pct": (int, float),
    "population": (int, float),
    "currency": str,
    "languages": list,
    "market_maturity": str,
    "payment_infrastructure": str,
    "major_local_competitors": list,
    "regulatory_notes": str,
}

AGENT2_OPTIONAL_FIELDS = [
    "regional_breakdown",
    "market_trend",
    "market_trend_explanation",
    "tech_adoption_profile",
]

VALID_MARKET_MATURITY = {"emerging", "developing", "mature"}
VALID_MARKET_TREND = {"growing", "stable", "contracting", None}


def check_agent2() -> bool:
    from backend.agents.market_data_fetcher import run

    agent2_input = {
        "target_market": "Brazil",
        "agent1_output": AGENT1_OUTPUT_STUB,
    }

    print("\n--- Agent 2: Market Data Fetcher ---")
    print(f"Input: target_market=Brazil, agent1_output=<TaskFlow stub>\n")

    try:
        result = run(agent2_input)
    except ValueError as exc:
        print(f"[FAIL] Validation error: {exc}")
        return False
    except Exception as exc:
        print(f"[FAIL] run() raised {type(exc).__name__}: {exc}")
        return False

    errors = []

    for field, expected_type in AGENT2_MANDATORY_FIELDS.items():
        if field not in result:
            errors.append(f"missing mandatory field '{field}'")
        elif result[field] is None:
            errors.append(f"'{field}' is null but is mandatory")
        elif not isinstance(result[field], expected_type):
            errors.append(
                f"'{field}' should be {expected_type}, got {type(result[field]).__name__}"
            )

    if "market_maturity" in result and result["market_maturity"] not in VALID_MARKET_MATURITY:
        errors.append(
            f"'market_maturity' must be one of {VALID_MARKET_MATURITY}, got '{result['market_maturity']}'"
        )

    if "market_trend" in result and result["market_trend"] not in VALID_MARKET_TREND:
        errors.append(
            f"'market_trend' must be one of {VALID_MARKET_TREND}, got '{result['market_trend']}'"
        )

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return False

    print("Mandatory fields:")
    for field in AGENT2_MANDATORY_FIELDS:
        print(f"  {field}: {result[field]}")

    print("\nOptional fields:")
    for field in AGENT2_OPTIONAL_FIELDS:
        print(f"  {field}: {result.get(field)}")

    print("\n[PASS] Agent 2 returned valid output with all mandatory fields.")
    return True


# Hardcoded Agent 2 output stub for Brazil / TaskFlow
AGENT2_OUTPUT_STUB = {
    "country_name": "Brazil",
    "gdp_per_capita_usd": 10310.55,
    "internet_penetration_pct": 84.46,
    "population": 213421037,
    "currency": "BRL - Brazilian Real",
    "languages": ["Portuguese"],
    "market_maturity": "developing",
    "payment_infrastructure": (
        "Dominated by Pix (instant payment system) and boleto bancário. "
        "Credit card penetration is moderate (~45%). PayPal and Stripe have limited reach. "
        "SaaS billing requires local payment gateway support (e.g. Iugu, Pagar.me)."
    ),
    "major_local_competitors": ["Trello (localised)", "Monday.com BR", "Asana", "Runrun.it", "Moskit CRM"],
    "regulatory_notes": (
        "LGPD (Lei Geral de Proteção de Dados) is Brazil's GDPR equivalent — full compliance required. "
        "Foreign companies must appoint a local data protection officer. "
        "Marco Civil da Internet governs data localisation for some categories."
    ),
    "regional_breakdown": "São Paulo and Rio de Janeiro are the primary beachheads for B2B SaaS.",
    "market_trend": "growing",
    "market_trend_explanation": "Brazil's SaaS market is growing at ~25% YoY driven by SME digitisation.",
    "tech_adoption_profile": (
        "Mid-tier adopter. Urban tech hubs (SP, RJ) adopt quickly; "
        "SMEs outside major cities lag 12-18 months behind."
    ),
    "data_source": "world_bank + rest_countries",
}

AGENT3_MANDATORY_FIELDS = {
    "cultural_fit_score": int,
    "score_label": str,
    "dimension_analysis": list,
    "overall_explanation": str,
}

AGENT3_OPTIONAL_FIELDS = [
    "messaging_recommendations",
    "sales_motion_recommendation",
    "cultural_red_flags",
    "cultural_tailwinds",
]

VALID_SCORE_LABELS = {
    "Excellent Fit", "Good Fit", "Moderate Fit", "Poor Fit", "Very Poor Fit"
}


def check_agent3() -> bool:
    from backend.agents.cultural_fit_scorer import run

    agent3_input = {
        "target_market": "Brazil",
        "agent1_output": AGENT1_OUTPUT_STUB,
        "agent2_output": AGENT2_OUTPUT_STUB,
    }

    print("\n--- Agent 3: Cultural Fit Scorer ---")
    print("Input: target_market=Brazil, agent1=TaskFlow stub, agent2=Brazil stub\n")

    try:
        result = run(agent3_input)
    except ValueError as exc:
        print(f"[FAIL] Validation error: {exc}")
        return False
    except Exception as exc:
        print(f"[FAIL] run() raised {type(exc).__name__}: {exc}")
        return False

    errors = []

    for field, expected_type in AGENT3_MANDATORY_FIELDS.items():
        if field not in result:
            errors.append(f"missing mandatory field '{field}'")
        elif result[field] is None:
            errors.append(f"'{field}' is null but is mandatory")
        elif not isinstance(result[field], expected_type):
            errors.append(
                f"'{field}' should be {expected_type.__name__}, got {type(result[field]).__name__}"
            )

    if "score_label" in result and result["score_label"] not in VALID_SCORE_LABELS:
        errors.append(f"'score_label' invalid: '{result['score_label']}'")

    da = result.get("dimension_analysis")
    if isinstance(da, list):
        if len(da) != 6:
            errors.append(f"'dimension_analysis' must have 6 items, got {len(da)}")
        else:
            for i, obj in enumerate(da):
                for key in ("dimension", "score", "implication"):
                    if key not in obj:
                        errors.append(f"dimension_analysis[{i}] missing key '{key}'")

    if isinstance(result.get("cultural_fit_score"), int):
        score = result["cultural_fit_score"]
        if not (0 <= score <= 100):
            errors.append(f"'cultural_fit_score' must be 0-100, got {score}")

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return False

    print("Mandatory fields:")
    print(f"  cultural_fit_score: {result['cultural_fit_score']}")
    print(f"  score_label:        {result['score_label']}")
    print(f"  overall_explanation: {result['overall_explanation']}")
    print(f"  data_source:        {result.get('data_source')}")
    print(f"  dimension_analysis:")
    for dim in result["dimension_analysis"]:
        print(f"    [{dim.get('dimension')} {dim.get('score')}] {dim.get('implication')}")

    print("\nOptional fields:")
    for field in AGENT3_OPTIONAL_FIELDS:
        val = result.get(field)
        if isinstance(val, list):
            print(f"  {field}:")
            for item in val:
                print(f"    - {item}")
        else:
            print(f"  {field}: {val}")

    print("\n[PASS] Agent 3 returned valid output with all mandatory fields.")
    return True


# Hardcoded Agent 3 output stub for Brazil / TaskFlow
AGENT3_OUTPUT_STUB = {
    "cultural_fit_score": 62,
    "score_label": "Moderate Fit",
    "dimension_analysis": [
        {
            "dimension": "PDI",
            "score": 69,
            "implication": (
                "High power distance means task assignment authority must come from the top; "
                "bottom-up adoption will stall without executive sponsorship."
            ),
        },
        {
            "dimension": "IDV",
            "score": 38,
            "implication": (
                "Collectivist culture values group harmony — the team collaboration angle resonates, "
                "but self-serve PLG will underperform; peer referrals and group demos work better."
            ),
        },
        {
            "dimension": "MAS",
            "score": 49,
            "implication": (
                "Balanced masculinity means neither pure performance metrics nor pure work-life-balance "
                "messaging will dominate; blend efficiency gains with reducing team stress."
            ),
        },
        {
            "dimension": "UAI",
            "score": 76,
            "implication": (
                "High uncertainty avoidance creates demand for proof — case studies, free trials, "
                "and local references are essential before any commitment."
            ),
        },
        {
            "dimension": "LTO",
            "score": 44,
            "implication": (
                "Moderate long-term orientation means ROI arguments should emphasise near-term "
                "productivity gains rather than multi-year strategic transformation."
            ),
        },
        {
            "dimension": "IVR",
            "score": 59,
            "implication": (
                "Moderately indulgent culture appreciates polished UX and enjoyable onboarding; "
                "a clunky interface will be disproportionately penalised."
            ),
        },
    ],
    "overall_explanation": (
        "Brazil presents a moderate cultural fit for TaskFlow. The collectivist orientation "
        "supports team-based collaboration tools, but high uncertainty avoidance and power distance "
        "will require a sales-led motion with local social proof to unlock enterprise deals. "
        "PLG alone will not be sufficient in this market."
    ),
    "messaging_recommendations": [
        "Lead with 'your team, always in sync' — emphasise collective harmony over individual productivity",
        "Use Brazilian customer logos and Portuguese-language case studies in every sales touchpoint",
        "Frame auto-assignment as 'fair workload distribution' not 'AI taking over' to reduce UAI friction",
    ],
    "sales_motion_recommendation": (
        "sales-led: Brazil's high PDI and UAI mean deals require executive buy-in and "
        "hands-on demos before any trial commitment."
    ),
    "cultural_red_flags": [
        "English-only onboarding will immediately disqualify TaskFlow for mid-market Brazilian buyers",
        "Positioning around 'AI replacing managers' will trigger resistance in high-PDI organisations",
    ],
    "cultural_tailwinds": [
        "Brazil's booming remote-work culture post-2020 creates genuine pull for async coordination tools",
        "WhatsApp-native workforce means Slack-integrated tools have a familiar integration story",
        "Growing SME digitalisation wave funded by Sebrae programmes creates an educated buyer pool",
    ],
    "data_source": "hofstede.json",
}

AGENT4_OPTIONAL_FIELDS = [
    "conversation_starter",
    "deal_breaker",
    "influencers",
    "time_to_close",
]

VALID_LIKELIHOOD = {"High", "Medium", "Low"}
VARIANCE_PROFILE_FIELDS = ["conversion_range", "key_variables", "tipping_point_to_high", "tipping_point_to_low"]
MANDATORY_PERSONA_FIELDS = [
    "archetype_name", "name", "age", "job_title", "city",
    "company_size", "why_they_buy", "what_stops_them",
    "how_they_discover", "likelihood_to_convert", "variance_profile",
]


def check_agent4() -> bool:
    from backend.agents.persona_generator import run

    agent4_input = {
        "agent1_output": AGENT1_OUTPUT_STUB,
        "agent2_output": AGENT2_OUTPUT_STUB,
        "agent3_output": AGENT3_OUTPUT_STUB,
    }

    print("\n--- Agent 4: Persona Generator ---")
    print("Input: agent1=TaskFlow, agent2=Brazil, agent3=Cultural Fit stub\n")

    try:
        result = run(agent4_input)
    except ValueError as exc:
        print(f"[FAIL] Validation error: {exc}")
        return False
    except Exception as exc:
        print(f"[FAIL] run() raised {type(exc).__name__}: {exc}")
        return False

    personas = result.get("personas", [])
    errors = []

    if len(personas) != 5:
        errors.append(f"expected 5 personas, got {len(personas)}")

    for i, p in enumerate(personas):
        label = f"Persona {i+1} ({p.get('archetype_name', '?')})"
        for field in MANDATORY_PERSONA_FIELDS:
            if field not in p:
                errors.append(f"{label}: missing '{field}'")

        if p.get("likelihood_to_convert") not in VALID_LIKELIHOOD:
            errors.append(f"{label}: invalid likelihood '{p.get('likelihood_to_convert')}'")

        vp = p.get("variance_profile")
        if not isinstance(vp, dict):
            errors.append(f"{label}: variance_profile is not an object")
        else:
            for vf in VARIANCE_PROFILE_FIELDS:
                if vf not in vp:
                    errors.append(f"{label}: variance_profile missing '{vf}'")

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return False

    # Diversity checks (warnings only — not hard failures)
    cities = [p.get("city") for p in personas]
    unique_cities = set(cities)
    likelihoods = [p.get("likelihood_to_convert") for p in personas]
    ages = [p.get("age") for p in personas if isinstance(p.get("age"), int)]
    job_titles = [p.get("job_title") for p in personas]

    print("Diversity check:")
    print(f"  Cities ({len(unique_cities)} unique): {sorted(unique_cities)}")
    print(f"  Likelihoods: {likelihoods}")
    age_span = max(ages) - min(ages) if len(ages) >= 2 else 0
    print(f"  Age range: {min(ages)}-{max(ages)} (span={age_span})")
    print(f"  Job titles unique: {len(set(job_titles)) == len(job_titles)}")

    print("\nPersonas (mandatory fields):")
    for i, p in enumerate(personas):
        print(f"\n  [{i+1}] {p.get('archetype_name')} — {p.get('name')}, {p.get('age')}")
        print(f"       {p.get('job_title')} @ {p.get('company_size')} in {p.get('city')}")
        print(f"       Likelihood: {p.get('likelihood_to_convert')}")
        print(f"       Why they buy: {p.get('why_they_buy')}")
        print(f"       What stops them: {p.get('what_stops_them')}")
        print(f"       How they discover: {p.get('how_they_discover')}")
        vp = p.get("variance_profile", {})
        print(f"       Variance profile:")
        print(f"         range: {vp.get('conversion_range')}")
        print(f"         key variables: {vp.get('key_variables')}")
        print(f"         tipping->High: {vp.get('tipping_point_to_high')}")
        print(f"         tipping->Low:  {vp.get('tipping_point_to_low')}")

    print("\nPersonas (optional fields):")
    for i, p in enumerate(personas):
        print(f"\n  [{i+1}] {p.get('archetype_name')}")
        for field in AGENT4_OPTIONAL_FIELDS:
            print(f"       {field}: {p.get(field)}")

    print("\n[PASS] Agent 4 returned 5 valid personas with all mandatory fields.")
    return True


if __name__ == "__main__":
    results = [check_agent1(), check_agent2(), check_agent3(), check_agent4()]
    sys.exit(0 if all(results) else 1)
