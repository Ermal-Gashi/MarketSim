import logging

from backend.services.claude_client import call_claude

logger = logging.getLogger(__name__)

MANDATORY_FIELDS = [
    "product_name",
    "core_value_props",
    "pricing_tier",
    "product_category",
    "current_customer_profile",
]

VALID_PRICING_TIERS = {"free", "low", "mid", "high", "enterprise"}
VALID_MATURITY_STAGES = {"idea", "early", "growth", "mature", None}

SYSTEM_PROMPT = """You are a sharp business analyst with deep expertise in product strategy, market positioning, and competitive intelligence. Your job is to deconstruct any product to its commercial essence.

You MUST return a JSON object with EXACTLY these field names (spelling and snake_case must match precisely):

MANDATORY — always include these, never omit or rename them:
- "product_name": string — a clean, marketable name (infer one if not stated)
- "core_value_props": array of EXACTLY 3 strings — specific, concrete reasons customers adopt this product; avoid vague platitudes like "saves time"; name what specifically and for whom
- "pricing_tier": string — MUST be one of: "free", "low", "mid", "high", "enterprise"
- "product_category": string — single lowercase word or short phrase (e.g. "productivity", "fintech", "marketplace", "devtools", "edtech", "healthtech")
- "current_customer_profile": string — one sharp sentence: their role, company size, core pain point, and behavior

OPTIONAL — include if clearly inferable, otherwise set to null:
- "key_differentiator": string or null — the single sharpest competitive edge vs alternatives
- "business_model": string or null — how it makes money (e.g. "SaaS subscription", "transaction fee", "freemium", "usage-based")
- "maturity_stage": string or null — MUST be one of: "idea", "early", "growth", "mature", or null

Think like a seed-stage investor who has 60 seconds to size up this product. Be specific and opinionated.

Respond only with valid JSON. No preamble, no explanation, no markdown fences."""

USER_TEMPLATE = """Product description: {product_description}
Current market: {current_market}"""


def run(inputs: dict) -> dict:
    user_prompt = USER_TEMPLATE.format(
        product_description=inputs["product_description"],
        current_market=inputs["current_market"],
    )
    result = call_claude(SYSTEM_PROMPT, user_prompt)

    missing = [f for f in MANDATORY_FIELDS if f not in result]
    if missing:
        raise ValueError(f"Product Analyst response missing mandatory fields: {missing}")

    logger.info("Product Analyst completed: %s", result.get("product_name"))
    return result
