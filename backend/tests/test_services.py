"""
Run with:
    .venv\\Scripts\\python -m backend.tests.test_services
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def check_env() -> bool:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        print(f"[PASS] ANTHROPIC_API_KEY loaded ({len(key)} chars)")
        return True
    print("[FAIL] ANTHROPIC_API_KEY is missing or empty")
    return False


def check_claude() -> bool:
    from backend.services.claude_client import call_claude

    system = 'Respond only with valid JSON. No preamble, no explanation, no markdown fences.'
    user = 'Return the JSON object {"status": "ok"}.'

    try:
        result = call_claude(system, user)
        print(f"[PASS] call_claude returned: {result}")
        return True
    except Exception as exc:
        print(f"[FAIL] call_claude raised {type(exc).__name__}: {exc}")
        return False


def check_world_bank() -> bool:
    from backend.services.world_bank_client import get_country_data

    try:
        result = get_country_data("BR")
        gdp = result.get("gdp_per_capita_usd")
        internet = result.get("internet_penetration_pct")
        if gdp is not None and internet is not None:
            print(f"[PASS] world_bank get_country_data('BR'): GDP={gdp}, Internet={internet}%")
            return True
        print(f"[FAIL] world_bank returned None for one or more fields: {result}")
        return False
    except Exception as exc:
        print(f"[FAIL] get_country_data raised {type(exc).__name__}: {exc}")
        return False


def check_countries() -> bool:
    from backend.services.countries_client import get_country_info

    try:
        result = get_country_info("Brazil")
        pop = result.get("population")
        langs = result.get("languages")
        currencies = result.get("currencies")
        if pop and langs and currencies:
            print(
                f"[PASS] countries get_country_info('Brazil'): "
                f"pop={pop:,}, languages={langs}, currencies={[c['code'] for c in currencies]}"
            )
            return True
        print(f"[FAIL] countries returned incomplete data: {result}")
        return False
    except Exception as exc:
        print(f"[FAIL] get_country_info raised {type(exc).__name__}: {exc}")
        return False


if __name__ == "__main__":
    results = [check_env(), check_claude(), check_world_bank(), check_countries()]
    sys.exit(0 if all(results) else 1)
