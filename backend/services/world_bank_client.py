import logging

import httpx

logger = logging.getLogger(__name__)

_BASE = "https://api.worldbank.org/v2/country/{code}/indicator/{indicator}?format=json&mrv=1"

# World Bank indicator codes
_GDP_INDICATOR = "NY.GDP.PCAP.CD"          # GDP per capita (current USD)
_INTERNET_INDICATOR = "IT.NET.USER.ZS"     # Internet users (% of population)


def _fetch_indicator(country_code: str, indicator: str) -> float | None:
    url = _BASE.format(code=country_code, indicator=indicator)
    try:
        resp = httpx.get(url, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        # payload is [metadata_dict, [data_points...]]
        data_points = payload[1] if len(payload) > 1 else []
        if not data_points:
            return None
        # Take the first non-null value
        for point in data_points:
            if point.get("value") is not None:
                return round(float(point["value"]), 2)
        return None
    except Exception as exc:
        logger.warning("World Bank fetch failed for %s / %s: %s", country_code, indicator, exc)
        return None


def get_country_data(country_code: str) -> dict:
    """
    Fetch GDP per capita and internet penetration for a country.
    country_code: ISO 3166-1 alpha-2 or alpha-3 (e.g. 'BR', 'BRA').
    Returns a dict; missing fields carry None and data_source is flagged.
    """
    gdp = _fetch_indicator(country_code, _GDP_INDICATOR)
    internet = _fetch_indicator(country_code, _INTERNET_INDICATOR)

    missing = gdp is None or internet is None
    return {
        "country_code": country_code.upper(),
        "gdp_per_capita_usd": gdp,
        "internet_penetration_pct": internet,
        "data_source": "estimated" if missing else "world_bank",
    }
