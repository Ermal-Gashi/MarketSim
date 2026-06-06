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


# Hardcoded Agent 4 output stub for Brazil / TaskFlow
AGENT4_OUTPUT_STUB = {
    "personas": [
        {
            "archetype_name": "The Burnout-Aware Engineering Lead",
            "name": "Rodrigo Mendonca",
            "age": 34,
            "job_title": "Head of Engineering",
            "city": "Sao Paulo",
            "company_size": "80-150 employees",
            "why_they_buy": "Loses hours weekly to manual sprint delegation; TaskFlow's auto-assignment directly attacks that pain.",
            "what_stops_them": "High UAI (76) means he needs a Brazilian reference customer before signing. English-only onboarding is a dealbreaker.",
            "how_they_discover": "LinkedIn post in a Brazilian engineering community shared by a peer EM.",
            "likelihood_to_convert": "High",
            "variance_profile": {
                "conversion_range": "Medium to High",
                "key_variables": ["Portuguese onboarding", "Brazilian case study", "CTO approval", "BRL/USD sensitivity"],
                "tipping_point_to_high": "Peer vouches via WhatsApp with a Brazilian case study attached.",
                "tipping_point_to_low": "English-only trial; black-box AI assignment logic.",
            },
            "conversation_starter": "How many hours a week does your team lose figuring out who picks up the next ticket?",
            "deal_breaker": "English-only UI — abandons trial within 48 hours.",
            "influencers": ["CTO", "Senior Backend Engineer", "Head of People & Culture"],
            "time_to_close": "4-8 weeks",
        },
        {
            "archetype_name": "The Cautious Operations Director",
            "name": "Fernanda Castilho",
            "age": 47,
            "job_title": "Director of Operations",
            "city": "Sao Paulo",
            "company_size": "200-500 employees",
            "why_they_buy": "Board-level deadline slippage conversation; needs workload visibility dashboard to make the case for structural change.",
            "what_stops_them": "High PDI (69) means she won't champion without COO buy-in. UAI (76) requires formal pilot proposal and SLAs.",
            "how_they_discover": "In-person B2B SaaS event in Sao Paulo or management consultant referral.",
            "likelihood_to_convert": "Medium",
            "variance_profile": {
                "conversion_range": "Low to High",
                "key_variables": ["COO sponsorship", "Portuguese pilot proposal", "LGPD compliance docs", "Brazilian reference", "Dedicated CSM"],
                "tipping_point_to_high": "COO joins demo and frames it as a strategic ops initiative.",
                "tipping_point_to_low": "IT raises LGPD concerns; no Portuguese compliance docs within evaluation window.",
            },
            "conversation_starter": "When a deadline slips, how long does it take to identify which person's plate was already overloaded?",
            "deal_breaker": "No local support in Portuguese or no formal data-residency documentation.",
            "influencers": ["COO", "Head of IT", "External Management Consultant"],
            "time_to_close": "3-6 months",
        },
        {
            "archetype_name": "The Ambitious Project Champion",
            "name": "Lucas Ferreira",
            "age": 29,
            "job_title": "Senior Project Coordinator",
            "city": "Rio de Janeiro",
            "company_size": "40-80 employees",
            "why_they_buy": "Wants to be the person who fixed the workflow before making a case for promotion to PM.",
            "what_stops_them": "Zero budget authority; high PDI means manager must be convinced first. Can't recommend publicly until stress-tested.",
            "how_they_discover": "YouTube tutorial in Portuguese or r/brdev thread on async team management.",
            "likelihood_to_convert": "Medium",
            "variance_profile": {
                "conversion_range": "Low to Medium",
                "key_variables": ["Self-serve free trial", "Portuguese help docs", "Manager receptiveness", "Peer validation"],
                "tipping_point_to_high": "Manager formally tasks him with solving delegation chaos.",
                "tipping_point_to_low": "Manager dismisses it or trial requires IT provisioning.",
            },
            "conversation_starter": "If you could show your manager one dashboard proving why last month's delivery slipped, what would change?",
            "deal_breaker": "No self-serve free trial — can't build conviction without hands-on access.",
            "influencers": ["Project Manager", "CTO or Head of Product"],
            "time_to_close": "6-12 weeks from champion to close",
        },
        {
            "archetype_name": "The Price-Sensitive SME Founder",
            "name": "Tatiane Braga",
            "age": 41,
            "job_title": "Founder & CEO",
            "city": "Belo Horizonte",
            "company_size": "10-25 employees",
            "why_they_buy": "Buying back her own hours — simultaneously PM, HR, and client lead at a 15-person agency.",
            "what_stops_them": "Mid-tier pricing stacks against Runrun.it's aggressive SME pricing. UAI means team must test and accept before she pays.",
            "how_they_discover": "Sebrae digitalisation webinar or Brazilian entrepreneurship podcast.",
            "likelihood_to_convert": "Low",
            "variance_profile": {
                "conversion_range": "Low to Medium",
                "key_variables": ["SME pricing vs Runrun.it", "Portuguese-first onboarding", "30-day ROI visibility", "Peer founder recommendation"],
                "tipping_point_to_high": "Founder peer shows real before/after and TaskFlow offers 3-month SME intro price.",
                "tipping_point_to_low": "Runrun.it runs a targeted discount campaign at the same moment.",
            },
            "conversation_starter": "If TaskFlow gave you back 10 hours a month, what would you do with that time for your clients?",
            "deal_breaker": "Monthly price above Runrun.it for comparable seat count.",
            "influencers": None,
            "time_to_close": "2-4 weeks if pricing hurdle cleared",
        },
        {
            "archetype_name": "The Quietly Influential People Manager",
            "name": "Mariana Souza",
            "age": 38,
            "job_title": "Head of People & Culture",
            "city": "Rio de Janeiro",
            "company_size": "100-200 employees",
            "why_they_buy": "eNPS burnout signals trace to opaque workload — TaskFlow's visibility dashboard gives her data to make the case to leadership.",
            "what_stops_them": "No direct SaaS budget; must broker cross-departmental buy-in. AI framing risks being read as surveillance.",
            "how_they_discover": "Portuguese HR tech blog or LinkedIn article from a Brazilian People Ops leader.",
            "likelihood_to_convert": "Medium",
            "variance_profile": {
                "conversion_range": "Low to High",
                "key_variables": ["People team dashboard framing", "Joint eval with Engineering", "Leadership mandate", "Wellbeing vs surveillance distinction"],
                "tipping_point_to_high": "CEO names burnout reduction a Q3 priority and tasks her jointly with Head of Engineering.",
                "tipping_point_to_low": "Senior engineer calls tool 'management spyware' in a team meeting.",
            },
            "conversation_starter": "When your eNPS flags burnout, how long does it take to trace it to a specific team's workload?",
            "deal_breaker": "Any perception of individual performance surveillance — she'll actively block adoption.",
            "influencers": ["Head of Engineering", "COO", "CEO"],
            "time_to_close": "2-5 months",
        },
    ]
}

AGENT5_MANDATORY_FIELDS = [
    "title", "category", "description", "severity", "affected_personas", "mitigation"
]
AGENT5_OPTIONAL_FIELDS = ["time_sensitivity", "cost_to_fix", "early_warning_signal"]
VALID_CATEGORIES = {"Competitive", "Cultural", "Regulatory", "Economic", "Operational"}
VALID_SEVERITIES = {"Critical", "High", "Medium", "Low"}


def check_agent5() -> bool:
    from backend.agents.obstacle_detector import run

    agent5_input = {
        "agent1_output": AGENT1_OUTPUT_STUB,
        "agent2_output": AGENT2_OUTPUT_STUB,
        "agent3_output": AGENT3_OUTPUT_STUB,
        "agent4_output": AGENT4_OUTPUT_STUB,
        "country_code": "BR",
    }

    print("\n--- Agent 5: Obstacle Detector ---")
    print("Input: agent1-4 stubs, target=Brazil\n")

    try:
        result = run(agent5_input)
    except ValueError as exc:
        print(f"[FAIL] Validation error: {exc}")
        return False
    except Exception as exc:
        print(f"[FAIL] run() raised {type(exc).__name__}: {exc}")
        return False

    obstacles = result.get("obstacles", [])
    errors = []

    if len(obstacles) != 5:
        errors.append(f"expected 5 obstacles, got {len(obstacles)}")

    for i, obs in enumerate(obstacles):
        label = f"Obstacle {i+1} ({obs.get('title', '?')})"
        for field in AGENT5_MANDATORY_FIELDS:
            if field not in obs:
                errors.append(f"{label}: missing '{field}'")
        if obs.get("category") not in VALID_CATEGORIES:
            errors.append(f"{label}: invalid category '{obs.get('category')}'")
        if obs.get("severity") not in VALID_SEVERITIES:
            errors.append(f"{label}: invalid severity '{obs.get('severity')}'")
        if not isinstance(obs.get("affected_personas"), list):
            errors.append(f"{label}: 'affected_personas' must be a list")

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return False

    print("Obstacles (mandatory fields):")
    for i, obs in enumerate(obstacles):
        print(f"\n  [{i+1}] [{obs.get('severity')}] [{obs.get('category')}] {obs.get('title')}")
        print(f"       Description: {obs.get('description')}")
        print(f"       Affected personas: {obs.get('affected_personas')}")
        print(f"       Mitigation: {obs.get('mitigation')}")

    print("\nObstacles (optional fields):")
    for i, obs in enumerate(obstacles):
        print(f"\n  [{i+1}] {obs.get('title')}")
        for field in AGENT5_OPTIONAL_FIELDS:
            print(f"       {field}: {obs.get(field)}")

    print("\n[PASS] Agent 5 returned 5 valid obstacles with all mandatory fields.")
    return True


# Hardcoded Agent 5 output stub for Brazil / TaskFlow
AGENT5_OUTPUT_STUB = {
    "obstacles": [
        {
            "title": "LGPD Compliance Gate + Local DPO Requirement",
            "category": "Regulatory",
            "severity": "Critical",
            "description": (
                "Brazil's LGPD mandates a local DPO and Portuguese-language data processing agreements "
                "before any enterprise procurement sign-off. With CPI of 35, enforcement is selective "
                "but high-visibility foreign SaaS entrants are disproportionate targets. "
                "The Cautious Operations Director and The Burnout-Aware Engineering Lead will both "
                "block vendor contracts without documented LGPD compliance."
            ),
            "affected_personas": [
                "The Cautious Operations Director",
                "The Burnout-Aware Engineering Lead",
                "The Ambitious Project Champion",
            ],
            "mitigation": (
                "Engage a Brazilian privacy law firm before any commercial activity to appoint a "
                "named local DPO, draft a Portuguese LGPD-compliant DPA, and conduct a DPIA "
                "covering the AI workload-profiling feature. Budget 90 days and R$80-150k BRL."
            ),
            "time_sensitivity": "Day-one — enterprise procurement will request LGPD documentation at first commercial conversation.",
            "cost_to_fix": "High — requires local legal entity or representative, DPO, DPIA, and Portuguese compliance docs. 3-4 months elapsed.",
            "early_warning_signal": "First enterprise prospect requests a data security questionnaire and TaskFlow cannot produce a Portuguese LGPD-compliant version within 5 business days.",
        },
        {
            "title": "Payment Infrastructure Lockout — Pix/Boleto Gap",
            "category": "Operational",
            "severity": "Critical",
            "description": (
                "Brazil's SaaS billing is structurally incompatible with standard international payment stacks. "
                "Pix dominates, boleto bancario is mandatory for SME segments, and Stripe has no native boleto support. "
                "At household consumption of USD 6,218, The Price-Sensitive SME Founder will not enter a "
                "credit card billing flow requiring an international card. Without Iugu or Pagar.me, "
                "TaskFlow will generate pipeline it cannot convert."
            ),
            "affected_personas": [
                "The Price-Sensitive SME Founder",
                "The Ambitious Project Champion",
                "The Cautious Operations Director",
            ],
            "mitigation": "Integrate Pagar.me or Iugu before soft launch with boleto as a first-class checkout option. Allocate 6-8 weeks for API integration and Portuguese billing flow QA.",
            "time_sensitivity": "Day-one — this is a conversion blocker, not a growth friction issue. The first paid signup attempt will fail.",
            "cost_to_fix": "Medium — 6-8 weeks engineering plus gateway setup fees. CNPJ may be required for gateway onboarding.",
            "early_warning_signal": "Trial-to-paid conversion in Brazil falls below 8% despite healthy trial activation; exit surveys cite 'forma de pagamento' as abandonment reason.",
        },
        {
            "title": "High-PDI Executive Sponsorship Bottleneck",
            "category": "Cultural",
            "severity": "High",
            "description": (
                "PDI of 69 concentrates decision authority at the top, meaning TaskFlow's AI auto-assignment "
                "will be perceived as threatening managerial hierarchy if introduced bottom-up. "
                "The Ambitious Project Champion and The Quietly Influential People Manager will stall "
                "deals in 'internal review' for 6-9 months without C-suite sponsorship."
            ),
            "affected_personas": [
                "The Ambitious Project Champion",
                "The Quietly Influential People Manager",
                "The Cautious Operations Director",
                "The Burnout-Aware Engineering Lead",
            ],
            "mitigation": "Route Brazilian inbound into sales-assisted onboarding requiring a Director-level sponsor before full trial activation. Frame AI assignment as 'manager decision amplified by data', not autonomous AI.",
            "time_sensitivity": "At first enterprise deal attempt — self-serve pipeline will look healthy in trials but conversion collapses at 30-day mark.",
            "cost_to_fix": "Medium-High — requires sales motion redesign, Portuguese executive collateral, and a local sales hire or channel partner.",
            "early_warning_signal": "Trial accounts show IC usage but zero Director/VP engagement after 14 days; deals stall with 'precisamos alinhar internamente'.",
        },
        {
            "title": "Runrun.it and Monday.com BR Price-Anchoring",
            "category": "Competitive",
            "severity": "High",
            "description": (
                "Runrun.it offers BRL-denominated pricing, Portuguese-first UX, and local case studies — "
                "exactly the social proof UAI-76 Brazilian buyers require. At current BRL/USD rates, "
                "TaskFlow's mid-tier USD price is 25-40% above Runrun.it for The Price-Sensitive SME Founder. "
                "Monday.com BR has also invested in Portuguese localisation and regional references."
            ),
            "affected_personas": [
                "The Price-Sensitive SME Founder",
                "The Cautious Operations Director",
                "The Burnout-Aware Engineering Lead",
            ],
            "mitigation": "Launch with BRL-denominated pricing benchmarked to Runrun.it mid-tier. Fast-track a lighthouse customer programme — 3-5 Sao Paulo tech companies at 50% discount for 6 months in exchange for Portuguese video case studies.",
            "time_sensitivity": "At first competitive evaluation — Brazilian buyers request a competitor comparison within the first sales call.",
            "cost_to_fix": "Medium — BRL pricing page is low-cost; lighthouse programme costs USD 15-30k in foregone ARR but unlocks mid-market pipeline.",
            "early_warning_signal": "Runrun.it or Monday.com BR cited in >40% of lost deals within Q1; deal cycle exceeds 90 days in SME segment.",
        },
        {
            "title": "English-Only Onboarding Disqualifies Mid-Market",
            "category": "Cultural",
            "severity": "Medium",
            "description": (
                "IDV of 38 means purchasing involves multiple stakeholders — one team member's inability "
                "to navigate English UI becomes a group veto. IVR of 59 means Brazilians penalise "
                "clunky foreign onboarding as a product quality signal. The Price-Sensitive SME Founder "
                "in Belo Horizonte operates 12-18 months behind Sao Paulo's tech adoption curve, "
                "making English a hard filter that removes significant SAM."
            ),
            "affected_personas": [
                "The Price-Sensitive SME Founder",
                "The Ambitious Project Champion",
                "The Quietly Influential People Manager",
            ],
            "mitigation": "Ship complete Brazilian Portuguese UI, onboarding, help docs, and in-app tooltips before any paid marketing in Brazil. Hire a Brazilian UX copywriter (not translator) to adapt onboarding narrative away from AI replacement framing.",
            "time_sensitivity": "Pre-launch — any paid acquisition before Portuguese localisation is live burns budget acquiring users who churn at first login.",
            "cost_to_fix": "Medium — 2-3 months localisation work, estimated USD 8-20k depending on product surface area.",
            "early_warning_signal": "Brazilian trial onboarding completion falls >30% below global baseline; session recordings show abandonment at team invitation or task creation step.",
        },
    ]
}

AGENT6_MANDATORY_FIELDS = [
    "verdict", "verdict_reason", "confidence_score", "executive_summary",
    "signal_scorecard", "critical_assumptions", "recommended_first_move",
    "regional_weights", "dot_intensity", "radar_scores",
]
AGENT6_OPTIONAL_FIELDS = [
    "time_to_first_revenue", "estimated_cac", "biggest_wildcard",
    "revisit_trigger", "market_entry_sequence",
]
VALID_VERDICTS = {"Go", "Cautious Go", "No-Go"}
RADAR_KEYS = {"Market growth", "Cultural fit", "Internet penetration",
              "Political stability", "Ease of business", "Corruption index"}


def check_agent6() -> bool:
    from backend.agents.synthesizer import run

    agent6_input = {
        "agent1_output": AGENT1_OUTPUT_STUB,
        "agent2_output": AGENT2_OUTPUT_STUB,
        "agent3_output": AGENT3_OUTPUT_STUB,
        "agent4_output": AGENT4_OUTPUT_STUB,
        "agent5_output": AGENT5_OUTPUT_STUB,
        "biz_env": {"cpi": 35, "ease_of_business": 35, "press_freedom": 66, "political_stability": 40},
        "household_consumption_usd": 6218,
    }

    print("\n--- Agent 6: Synthesizer ---")
    print("Input: all agent stubs, target=Brazil\n")

    try:
        result = run(agent6_input)
    except ValueError as exc:
        print(f"[FAIL] Validation error: {exc}")
        return False
    except Exception as exc:
        print(f"[FAIL] run() raised {type(exc).__name__}: {exc}")
        return False

    errors = []

    for field in AGENT6_MANDATORY_FIELDS:
        if field not in result:
            errors.append(f"missing mandatory field '{field}'")

    if result.get("verdict") not in VALID_VERDICTS:
        errors.append(f"invalid verdict '{result.get('verdict')}'")

    rw = result.get("regional_weights", {})
    if isinstance(rw, dict):
        rw_sum = sum(rw.values())
        if rw_sum != 100:
            errors.append(f"regional_weights sums to {rw_sum}, expected 100")
    else:
        errors.append("regional_weights is not a dict")

    rs = result.get("radar_scores", {})
    if isinstance(rs, dict):
        missing_keys = RADAR_KEYS - set(rs.keys())
        extra_keys = set(rs.keys()) - RADAR_KEYS
        if missing_keys:
            errors.append(f"radar_scores missing keys: {missing_keys}")
        if extra_keys:
            errors.append(f"radar_scores has unexpected keys: {extra_keys}")
    else:
        errors.append("radar_scores is not a dict")

    ca = result.get("critical_assumptions", [])
    if not isinstance(ca, list) or len(ca) != 3:
        errors.append(f"critical_assumptions must have exactly 3 items, got {len(ca) if isinstance(ca, list) else type(ca)}")

    sc = result.get("signal_scorecard", [])
    if not isinstance(sc, list) or len(sc) == 0:
        errors.append("signal_scorecard must be a non-empty list")

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return False

    # ── Print mandatory fields ──────────────────────────────────────────
    print("Mandatory fields:")
    print(f"  verdict:          {result['verdict']}")
    print(f"  confidence_score: {result['confidence_score']}/100")
    print(f"  verdict_reason:   {result['verdict_reason']}")
    print(f"  executive_summary:\n    {result['executive_summary']}")

    print(f"\n  signal_scorecard ({len(sc)} signals):")
    for s in sc:
        print(f"    [{s.get('direction').upper():8}] [{s.get('weight'):6}] {s.get('signal')}")

    print(f"\n  critical_assumptions:")
    for i, a in enumerate(ca):
        print(f"    [{i+1}] IF FALSE: {a.get('consequence_if_false')}")
        print(f"         ASSUMES:  {a.get('assumption')}")

    print(f"\n  recommended_first_move: {result['recommended_first_move']}")

    print(f"\n  regional_weights (sum={sum(rw.values())}):")
    for region, weight in rw.items():
        intensity = result.get("dot_intensity", {}).get(region, "?")
        print(f"    {region}: weight={weight}% | dot_intensity={intensity}")

    print(f"\n  radar_scores:")
    for key in sorted(RADAR_KEYS):
        print(f"    {key}: {rs.get(key)}")

    # ── Print optional fields ───────────────────────────────────────────
    print("\nOptional fields:")
    for field in AGENT6_OPTIONAL_FIELDS:
        val = result.get(field)
        if field == "market_entry_sequence" and isinstance(val, list):
            print(f"  {field}:")
            for phase in val:
                print(f"    Phase: {phase.get('phase_name')} ({phase.get('timeframe')})")
                for action in phase.get("actions", []):
                    print(f"      - {action}")
        else:
            print(f"  {field}: {val}")

    print("\n[PASS] Agent 6 returned a valid synthesis with all mandatory fields.")
    return True


# Hardcoded Agent 6 output stub for Brazil / TaskFlow
AGENT6_OUTPUT_STUB = {
    "verdict": "Cautious Go",
    "verdict_reason": "Strong urban tech-hub demand offset by a critical LGPD compliance gap that must be closed before any enterprise deal can complete.",
    "confidence_score": 62,
    "executive_summary": (
        "Brazil's developing SaaS market shows genuine pull for remote-team tooling, with 84% internet "
        "penetration and a 25% YoY growth rate backing the opportunity. Two Critical obstacles — LGPD "
        "compliance and payment infrastructure — are solvable but require 90-day investment before "
        "commercial activity. Cultural fit is moderate (62/100); a sales-led motion with Portuguese "
        "localisation is essential. Enter with a Sao Paulo lighthouse programme while resolving "
        "compliance in parallel."
    ),
    "signal_scorecard": [
        {"signal": "UAI 76 demands local proof and Portuguese onboarding before any trial commitment", "direction": "negative", "weight": "High"},
        {"signal": "84% internet penetration exceeds regional average — digital infrastructure is not a blocker", "direction": "positive", "weight": "Medium"},
        {"signal": "LGPD DPO requirement is a day-one enterprise procurement gate", "direction": "negative", "weight": "High"},
        {"signal": "Brazil SaaS market growing 25% YoY driven by SME digitalisation", "direction": "positive", "weight": "High"},
        {"signal": "Pix/boleto payment gap will block first paid conversion attempt", "direction": "negative", "weight": "High"},
    ],
    "critical_assumptions": [
        {
            "assumption": "TaskFlow will complete Portuguese localisation and LGPD compliance before first paid marketing spend",
            "consequence_if_false": "Trial pipeline will generate leads that churn at onboarding or payment, wasting budget and burning early reputation",
        },
        {
            "assumption": "At least one Sao Paulo lighthouse customer can be signed within 90 days at a discounted rate",
            "consequence_if_false": "No local social proof means UAI-76 buyers will not progress past first demo, stalling mid-market pipeline indefinitely",
        },
        {
            "assumption": "BRL/USD rate stays within ±15% of current level during the 12-month entry phase",
            "consequence_if_false": "USD-denominated mid-tier pricing becomes uncompetitive against Runrun.it, collapsing SME conversion rates",
        },
    ],
    "recommended_first_move": (
        "Engage a Brazilian privacy law firm this week to appoint a local DPO and begin the LGPD DPA "
        "draft — this is the single gate blocking every enterprise deal and must run in parallel with "
        "Portuguese localisation."
    ),
    "regional_weights": {
        "Sao Paulo": 55,
        "Rio de Janeiro": 30,
        "Belo Horizonte": 15,
    },
    "dot_intensity": {
        "Sao Paulo": 72,
        "Rio de Janeiro": 65,
        "Belo Horizonte": 45,
    },
    "radar_scores": {
        "Market growth": 74,
        "Cultural fit": 62,
        "Internet penetration": 84,
        "Political stability": 40,
        "Ease of business": 35,
        "Corruption index": 35,
    },
    "time_to_first_revenue": "4-6 months (90 days compliance + 4-8 week first enterprise close)",
    "estimated_cac": "USD 800-2,400 per seat for sales-led mid-market motion",
    "biggest_wildcard": "Runrun.it launching an AI auto-assignment feature while TaskFlow is still in compliance setup",
    "revisit_trigger": "If LGPD compliance takes >120 days or lighthouse programme produces zero signed customers by month 4",
    "market_entry_sequence": None,
}

AGENT7_MANDATORY_FIELDS = [
    "instance_id", "archetype_name", "archetype_index", "city", "region",
    "lat", "lng", "conversion_outcome", "confidence_score", "pulse_intensity",
    "spawn_delay_ms", "rolled_variables", "tipping_high_met", "tipping_low_met",
    "display_name", "job_title", "archetype_label", "avatar_style",
    "outcome_reason", "deciding_factor",
]
VALID_OUTCOMES = {"converted", "evaluating", "abandoned"}


def check_agent7() -> bool:
    from backend.agents.simulation_layer import run

    agent7_input = {
        "agent4_output": AGENT4_OUTPUT_STUB,
        "agent6_output": AGENT6_OUTPUT_STUB,
    }

    print("\n--- Agent 7: Simulation Layer ---")
    print("Input: agent4=Brazil personas stub, agent6=Brazil synthesizer stub\n")

    try:
        result = run(agent7_input)
    except ValueError as exc:
        print(f"[FAIL] Validation error: {exc}")
        return False
    except Exception as exc:
        print(f"[FAIL] run() raised {type(exc).__name__}: {exc}")
        return False

    instances = result.get("instances", [])
    summary = result.get("summary", {})
    errors = []

    # --- Exactly 200 instances ---
    if len(instances) != 200:
        errors.append(f"expected 200 instances, got {len(instances)}")

    # --- All mandatory fields present on every instance ---
    for i, inst in enumerate(instances):
        missing = [f for f in AGENT7_MANDATORY_FIELDS if f not in inst]
        if missing:
            errors.append(f"instance {i} missing fields: {missing}")
        if inst.get("conversion_outcome") not in VALID_OUTCOMES:
            errors.append(f"instance {i} invalid conversion_outcome: {inst.get('conversion_outcome')}")

    # --- Summary internal consistency ---
    s_total = summary.get("total", -1)
    s_converted = summary.get("converted", 0)
    s_evaluating = summary.get("evaluating", 0)
    s_abandoned = summary.get("abandoned", 0)
    if s_converted + s_evaluating + s_abandoned != s_total:
        errors.append(
            f"summary mismatch: {s_converted}+{s_evaluating}+{s_abandoned} "
            f"= {s_converted + s_evaluating + s_abandoned} != total={s_total}"
        )
    if s_total != 200:
        errors.append(f"summary.total should be 200, got {s_total}")

    # --- by_region totals must match regional_weights within 15% of 200 ---
    regional_weights = AGENT6_OUTPUT_STUB["regional_weights"]
    by_region = summary.get("by_region", {})
    for region, weight in regional_weights.items():
        expected = 200 * weight / 100
        actual = by_region.get(region, {}).get("total", 0)
        tolerance = 200 * 0.15
        if abs(actual - expected) > tolerance:
            errors.append(
                f"region '{region}': expected ~{expected:.0f} (±{tolerance:.0f}), got {actual}"
            )

    # --- spawn_delay_ms range 0-8000 ---
    for i, inst in enumerate(instances):
        sd = inst.get("spawn_delay_ms", -1)
        if not (0 <= sd <= 8000):
            errors.append(f"instance {i} spawn_delay_ms={sd} out of range 0-8000")

    # --- lat/lng non-zero (persona cities all have known coords) ---
    zero_coords = [i for i, inst in enumerate(instances) if inst.get("lat") == 0.0 and inst.get("lng") == 0.0]
    if zero_coords:
        errors.append(f"{len(zero_coords)} instances have (0,0) coordinates: indices {zero_coords[:5]}")

    if errors:
        for e in errors:
            print(f"[FAIL] {e}")
        return False

    # --- Print summary stats ---
    print("Summary stats:")
    print(f"  total:           {summary['total']}")
    print(f"  converted:       {summary['converted']}")
    print(f"  evaluating:      {summary['evaluating']}")
    print(f"  abandoned:       {summary['abandoned']}")
    print(f"  conversion_rate: {summary['conversion_rate']}%")

    print("\n  by_region:")
    for region, stats in summary["by_region"].items():
        rw = regional_weights.get(region, "?")
        print(f"    {region}: total={stats['total']} converted={stats['converted']} rate={stats['rate']}% (weight={rw}%)")

    print("\n  by_archetype:")
    for arch, stats in summary["by_archetype"].items():
        print(f"    {arch}: total={stats['total']} converted={stats['converted']} rate={stats['rate']}%")

    # --- Print first 3 instances in full ---
    print("\nFirst 3 instances (full):")
    for inst in instances[:3]:
        print(f"\n  [{inst['instance_id']}]")
        for key, val in inst.items():
            if key == "instance_id":
                continue
            print(f"    {key}: {val}")

    print("\n[PASS] Agent 7 generated 200 valid instances with consistent summary stats.")
    return True


if __name__ == "__main__":
    results = [check_agent1(), check_agent2(), check_agent3(), check_agent4(), check_agent5(), check_agent6(), check_agent7()]
    sys.exit(0 if all(results) else 1)
