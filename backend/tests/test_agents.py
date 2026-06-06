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


if __name__ == "__main__":
    results = [check_agent1()]
    sys.exit(0 if all(results) else 1)
