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


if __name__ == "__main__":
    results = [check_agent1(), check_agent2(), check_agent3()]
    sys.exit(0 if all(results) else 1)
