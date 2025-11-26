# api/views.py
from typing import Any, Dict

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .services import get_current_weather, WeatherServiceError
from .advice import build_weather_advice


def _normalize_weather(raw: Dict[str, Any], source: str) -> Dict[str, Any]:
    location = raw.get("location", {})
    current = raw.get("current", {})
    condition = current.get("condition", {})

    return {
        "meta": {
            "source": source,
            "provider": "WeatherAPI.com",
        },
        "location": {
            "city": location.get("name"),
            "country": location.get("country"),
            "coordinates": {
                "lat": location.get("lat"),
                "lon": location.get("lon"),
            },
        },
        "weather": {
            "temperature": current.get("temp_c"),
            "feels_like": current.get("feelslike_c"),
            "humidity": current.get("humidity"),
            "pressure": current.get("pressure_mb"),
            "description": condition.get("text"),
            "icon": condition.get("icon"),
            "cloudiness": current.get("cloud"),
        },
        "wind": {
            "speed": current.get("wind_kph"),
            "deg": current.get("wind_degree"),
        },
        "sun": {
            "sunrise_utc": None,
            "sunset_utc": None,
        },
        "provider_raw": raw,
    }


@require_GET
def current_weather_view(request):
    city = request.GET.get("city", "").strip()
    if not city:
        return JsonResponse({"error": "Query parameter 'city' is required."}, status=400)

    try:
        result = get_current_weather(city)
    except WeatherServiceError as e:
        return JsonResponse({"error": str(e)}, status=400)

    normalized = _normalize_weather(result["data"], result["source"])

    advice_input = {
        "temperature": normalized["weather"]["temperature"],
        "humidity": normalized["weather"]["humidity"],
        "description": normalized["weather"]["description"],
        "wind": normalized["wind"],
    }
    advice = build_weather_advice(advice_input)

    response = {
        "meta": normalized["meta"],
        "location": normalized["location"],
        "weather": normalized["weather"],
        "wind": normalized["wind"],
        "sun": normalized["sun"],
        "advice": advice,
        "provider_raw": normalized["provider_raw"],
    }

    return JsonResponse(response)
