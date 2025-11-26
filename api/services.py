# api/services.py
import logging
from typing import Dict, Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_PREFIX = "weather:"
CACHE_TTL_SECONDS = 600  # 10 minutes


class WeatherServiceError(Exception):
    """Custom error for weather service issues."""


def _cache_key(city: str) -> str:
    return f"{CACHE_PREFIX}{city.strip().lower()}"


def get_current_weather(city: str) -> Dict[str, Any]:
    """
    Uses WeatherAPI.com to fetch current weather for a city.

    Returns:
        {
          "source": "cache" | "live",
          "data": <raw_weatherapi_json>
        }
    Raises:
        WeatherServiceError on problems.
    """
    if not city or not city.strip():
        raise WeatherServiceError("City name is required.")

    cache_key = _cache_key(city)
    cached = cache.get(cache_key)
    if cached is not None:
        return {"source": "cache", "data": cached}

    api_key = settings.WEATHERAPI_KEY
    if not api_key or api_key == "REPLACE_WITH_REAL_KEY":
        raise WeatherServiceError("WeatherAPI key is not configured.")

    params = {
        "key": api_key,
        "q": city,
        "aqi": "no",
    }

    try:
        resp = requests.get(settings.WEATHERAPI_BASE_URL, params=params, timeout=5)
    except requests.RequestException as e:
        logger.exception("Error calling WeatherAPI")
        raise WeatherServiceError("Failed to contact weather provider.") from e

    # WeatherAPI returns 200 even for many errors, but with an "error" field
    try:
        data = resp.json()
    except Exception:
        logger.error("Failed to parse WeatherAPI response: %s", resp.text)
        raise WeatherServiceError("Invalid response from weather provider.")

    if "error" in data:
        message = data["error"].get("message", "Unknown error from WeatherAPI.")
        code = data["error"].get("code")
        logger.error("WeatherAPI error %s: %s", code, message)
        raise WeatherServiceError(f"Weather provider error: {message}")

    if resp.status_code != 200:
        logger.error("WeatherAPI HTTP error %s: %s", resp.status_code, resp.text)
        raise WeatherServiceError(
            f"Weather provider HTTP error {resp.status_code}."
        )

    # Success -> cache and return
    cache.set(cache_key, data, CACHE_TTL_SECONDS)
    return {"source": "live", "data": data}
