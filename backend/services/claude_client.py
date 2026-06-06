import json
import logging
import os
import re

import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2000

_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def _strip_fences(text: str) -> str:
    """Remove markdown code fences if present."""
    return re.sub(r"^```[a-zA-Z]*\n?|```$", "", text.strip(), flags=re.MULTILINE).strip()


def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> dict:
    """Call Claude and return parsed JSON. Retries once on JSON parse failure."""
    for attempt in range(2):
        response = _client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text
        cleaned = _strip_fences(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            if attempt == 0:
                logger.warning("JSON parse failed on attempt 1, retrying...")
                continue
            logger.error("JSON parse failed after retry. Raw response: %s", raw)
            raise
