import logging

import httpx

logger = logging.getLogger(__name__)

_BASE = "https://restcountries.com/v3.1/name/{name}?fullText=true&fields=name,population,currencies,languages"


def get_country_info(country_name: str) -> dict:
    """
    Fetch population, currencies, and languages for a country by name.
    Returns a clean dict; missing fields are None and data_source is flagged.
    """
    url = _BASE.format(name=httpx.URL(country_name).raw_path.decode() if False else country_name)
    try:
        resp = httpx.get(
            "https://restcountries.com/v3.1/name/" + country_name,
            params={"fullText": "true", "fields": "name,population,currencies,languages"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            raise ValueError("Empty response")
        country = data[0]

        # currencies: {"BRL": {"name": "Brazilian real", "symbol": "R$"}, ...}
        currencies_raw = country.get("currencies", {})
        currencies = [
            {"code": code, "name": info.get("name"), "symbol": info.get("symbol")}
            for code, info in currencies_raw.items()
        ]

        # languages: {"por": "Portuguese", ...}
        languages = list(country.get("languages", {}).values())

        return {
            "country_name": country.get("name", {}).get("common", country_name),
            "population": country.get("population"),
            "currencies": currencies,
            "languages": languages,
            "data_source": "rest_countries",
        }
    except Exception as exc:
        logger.warning("REST Countries fetch failed for '%s': %s", country_name, exc)
        return {
            "country_name": country_name,
            "population": None,
            "currencies": None,
            "languages": None,
            "data_source": "estimated",
        }
