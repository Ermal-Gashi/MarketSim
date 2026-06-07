import logging

from backend.services.claude_client import call_claude
from backend.services.countries_client import get_country_info
from backend.services.world_bank_client import get_country_data

logger = logging.getLogger(__name__)

MANDATORY_FIELDS = [
    "country_name",
    "gdp_per_capita_usd",
    "internet_penetration_pct",
    "population",
    "currency",
    "languages",
    "market_maturity",
    "payment_infrastructure",
    "major_local_competitors",
    "regulatory_notes",
]

VALID_MARKET_MATURITY = {"emerging", "developing", "mature"}
VALID_MARKET_TREND = {"growing", "stable", "contracting", None}

SYSTEM_PROMPT = """You are a senior market entry strategist. You have just received real economic and demographic data about a target country, along with a product profile. Your job is to assess this specific market for this specific product category — not the country in the abstract.

Use the real data provided (GDP, internet penetration, population, currency, languages) directly in your response. Do not ignore or contradict it. Then layer on your qualitative expertise to fill in what the raw numbers cannot tell you.

You MUST return a JSON object with EXACTLY these field names (spelling and snake_case must match precisely):

MANDATORY — always include, never omit or rename:
- "country_name": string — the full common name of the country
- "gdp_per_capita_usd": number — use the value from the provided real data; use null only if real data was unavailable
- "internet_penetration_pct": number — use the value from the provided real data; use null only if real data was unavailable
- "population": number — use the value from the provided real data; use null only if real data was unavailable
- "currency": string — primary currency code and name (e.g. "BRL - Brazilian Real")
- "languages": array of strings — official or dominant languages
- "market_maturity": string — MUST be one of: "emerging", "developing", "mature" — assessed specifically for the given product category, not the country overall
- "payment_infrastructure": string — describe the dominant payment rails, digital wallet adoption, card penetration, and any friction points relevant to SaaS or digital product sales
- "major_local_competitors": array of strings — name actual local or regionally dominant competitors in this product category; if none exist, say so explicitly with a short explanation in a single string inside the array. The major_local_competitors field must contain a minimum of 6 competitors and ideally 8-10. Include both large international players present in this market AND smaller local/regional competitors. Each competitor should be a descriptive string including the company name and a brief note about their positioning, e.g. "Aldi — German discount grocery giant with 40% private label market share". Do not return fewer than 6 competitors under any circumstances.
- "regulatory_notes": string — relevant legal, data privacy, or business registration considerations a foreign company must know before entering this market

OPTIONAL — include if clearly inferable, otherwise set to null:
- "regional_breakdown": string or null — which cities or regions are the strongest first beachheads and why
- "market_trend": string or null — MUST be one of: "growing", "stable", "contracting", or null
- "market_trend_explanation": string or null — one sentence explaining the trend
- "tech_adoption_profile": string or null — how quickly and broadly this market adopts new software tools, and what drives or slows adoption

Be specific. Name real companies, real cities, real regulations. Do not be vague or generic.

Respond only with valid JSON. No preamble, no explanation, no markdown fences."""

USER_TEMPLATE = """TARGET MARKET: {target_market}

REAL FETCHED DATA:
- GDP per capita (USD): {gdp_per_capita}
- Internet penetration (%): {internet_pct}
- Population: {population}
- Currencies: {currencies}
- Languages: {languages}
- Data source reliability: {data_source}

PRODUCT PROFILE (from Agent 1):
- Product name: {product_name}
- Product category: {product_category}
- Pricing tier: {pricing_tier}
- Core value props: {core_value_props}
- Current customer profile: {current_customer_profile}

Assess the target market for this specific product. Use the real data above directly in your response."""


def run(inputs: dict) -> dict:
    target_market = inputs["target_market"]
    agent1 = inputs["agent1_output"]

    # --- Step 1: Fetch real data from both APIs ---
    wb_data = get_country_data(_guess_country_code(target_market))
    rc_data = get_country_info(target_market)

    currencies = rc_data.get("currencies") or []
    currency_str = (
        ", ".join(f"{c['code']} - {c['name']}" for c in currencies)
        if currencies else "unknown"
    )
    languages = rc_data.get("languages") or []
    population = rc_data.get("population")
    gdp = wb_data.get("gdp_per_capita_usd")
    internet = wb_data.get("internet_penetration_pct")

    # Combine data_source flags
    sources = {wb_data.get("data_source"), rc_data.get("data_source")}
    data_source = "estimated (partial)" if "estimated" in sources else "world_bank + rest_countries"

    # --- Step 2: Call Claude with real data + Agent 1 context ---
    user_prompt = USER_TEMPLATE.format(
        target_market=target_market,
        gdp_per_capita=gdp if gdp is not None else "unavailable",
        internet_pct=internet if internet is not None else "unavailable",
        population=f"{population:,}" if population else "unavailable",
        currencies=currency_str,
        languages=", ".join(languages) if languages else "unavailable",
        data_source=data_source,
        product_name=agent1.get("product_name", "unknown"),
        product_category=agent1.get("product_category", "unknown"),
        pricing_tier=agent1.get("pricing_tier", "unknown"),
        core_value_props="; ".join(agent1.get("core_value_props", [])),
        current_customer_profile=agent1.get("current_customer_profile", "unknown"),
    )

    result = call_claude(SYSTEM_PROMPT, user_prompt)

    # --- Step 3: Validate mandatory fields ---
    missing = [f for f in MANDATORY_FIELDS if f not in result]
    if missing:
        raise ValueError(f"Market Data Fetcher response missing mandatory fields: {missing}")

    logger.info("Market Data Fetcher completed for: %s", result.get("country_name"))
    return result


def _guess_country_code(market_name: str) -> str:
    """Map common country names to ISO alpha-2 codes for the World Bank API."""
    mapping = {
        "brazil": "BR", "germany": "DE", "india": "IN", "china": "CN",
        "japan": "JP", "united kingdom": "GB", "uk": "GB", "france": "FR",
        "canada": "CA", "australia": "AU", "mexico": "MX", "nigeria": "NG",
        "south africa": "ZA", "indonesia": "ID", "turkey": "TR",
        "argentina": "AR", "colombia": "CO", "kenya": "KE", "egypt": "EG",
        "saudi arabia": "SA", "united arab emirates": "AE", "uae": "AE",
        "spain": "ES", "italy": "IT", "netherlands": "NL", "sweden": "SE",
        "poland": "PL", "vietnam": "VN", "thailand": "TH", "philippines": "PH",
        "pakistan": "PK", "bangladesh": "BD", "ethiopia": "ET",
        "united states": "US", "usa": "US",
    }
    return mapping.get(market_name.lower(), market_name[:2].upper())
