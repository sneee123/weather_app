# api/advice.py
from typing import Dict, Any, List


def build_weather_advice(weather: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given normalized weather data (from view), return:
      - summary
      - precautions
      - avoid_places
      - recommended_places
      - activities
    """

    temp = weather.get("temperature")
    humidity = weather.get("humidity")
    wind_speed = weather.get("wind", {}).get("speed")
    description = (weather.get("description") or "").lower()

    precautions: List[str] = []
    avoid_places: List[str] = []
    recommended_places: List[str] = []
    activities: List[str] = []

    # Flags
    is_rainy = any(w in description for w in ["rain", "drizzle", "shower"])
    is_stormy = any(w in description for w in ["storm", "thunder"])
    is_snowy = "snow" in description
    is_foggy = any(w in description for w in ["fog", "mist", "haze"])

    is_hot = temp is not None and temp >= 32
    is_very_hot = temp is not None and temp >= 37
    is_cold = temp is not None and temp <= 10
    is_cool = temp is not None and 10 < temp < 18
    is_pleasant = (
        temp is not None
        and 18 <= temp <= 30
        and not is_rainy
        and not is_stormy
        and not is_snowy
    )
    is_windy = wind_speed is not None and wind_speed >= 8
    is_very_windy = wind_speed is not None and wind_speed >= 12

    # Precautions
    if is_hot:
        precautions += [
            "Stay hydrated and carry a water bottle.",
            "Wear light, breathable clothes.",
            "Use sunscreen, sunglasses, and a cap/hat.",
        ]
        if is_very_hot:
            precautions.append("Avoid going out in peak afternoon hours if possible.")

    if is_cold or is_cool:
        precautions += [
            "Wear warm layers when going outside.",
            "Keep head and ears covered if it's windy.",
        ]

    if is_rainy or is_snowy:
        precautions += [
            "Carry an umbrella or raincoat, and wear waterproof footwear.",
            "Be careful on slippery roads and pavements.",
        ]
        if humidity and humidity > 85:
            precautions.append("Allow extra travel time due to slow traffic.")

    if is_stormy or is_very_windy:
        precautions += [
            "Stay away from large trees and weak structures during strong winds.",
            "Avoid riding two-wheelers in very strong wind if possible.",
        ]

    if is_foggy:
        precautions += [
            "If driving, keep headlights on low beam.",
            "Maintain safe distance from the vehicle in front.",
        ]

    if not precautions:
        precautions.append("Weather seems normal. Usual daily precautions are enough.")

    # Places to avoid
    if is_rainy or is_stormy:
        avoid_places += [
            "Open parks and large open fields during heavy rain or storms.",
            "Waterfront areas like beaches during strong winds.",
        ]
    if is_very_hot:
        avoid_places += [
            "Open grounds in direct afternoon sun.",
            "Crowded, poorly ventilated markets in peak heat.",
        ]
    if is_cold or is_snowy:
        avoid_places.append("Spending long time outside without proper winter wear.")
    if is_foggy:
        avoid_places.append("High-speed highways or hilly roads in very low visibility.")

    if not avoid_places:
        avoid_places.append("No specific places to avoid due to weather. Follow usual safety tips.")

    # Recommended places & activities
    if is_pleasant:
        recommended_places += [
            "City parks and gardens.",
            "Lakeside or riverside promenades.",
            "Outdoor cafes.",
        ]
        activities += [
            "Morning or evening walk/jog.",
            "Cycling in nearby areas.",
            "Picnic with friends or family.",
        ]

    if is_hot:
        recommended_places += [
            "Malls and indoor shopping centers.",
            "Air-conditioned cafes.",
            "Indoor gyms or sports clubs.",
        ]
        activities += [
            "Swimming in a safe pool.",
            "Light indoor workouts or yoga.",
            "Evening or early-morning walks instead of afternoon outings.",
        ]

    if is_cold or is_cool:
        recommended_places += [
            "Cozy cafes or bookshops.",
            "Indoor museums or galleries.",
        ]
        activities += [
            "Hot beverages at a nearby café.",
            "Movie night at home or cinema.",
        ]

    if is_rainy:
        recommended_places += [
            "Malls, cinemas, and indoor gaming zones.",
            "Indoor food courts and coffee shops.",
        ]
        activities += [
            "Watching movies or series.",
            "Indoor hobbies like reading or cooking.",
        ]

    if is_stormy or is_very_windy:
        activities += [
            "Stay indoors and catch up on reading or online courses.",
            "Light indoor workouts or stretching.",
        ]

    if is_snowy:
        activities += [
            "Short walks to enjoy snow with warm clothing.",
            "Indoor games and warm drinks.",
        ]

    if not recommended_places:
        recommended_places.append("Cafes, libraries, or indoor hangout spots nearby.")
    if not activities:
        activities.append("Normal daily activities as per your routine.")

    # Summary
    summary_parts = []
    if is_hot:
        summary_parts.append("It’s quite hot.")
    if is_cold:
        summary_parts.append("It’s quite cold.")
    if is_rainy:
        summary_parts.append("Expect rain.")
    if is_stormy:
        summary_parts.append("Conditions are stormy or very windy.")
    if is_pleasant:
        summary_parts.append("Weather is pleasant for outdoor plans.")

    summary = " ".join(summary_parts) if summary_parts else "Weather looks normal overall."

    return {
        "summary": summary,
        "precautions": precautions,
        "avoid_places": avoid_places,
        "recommended_places": recommended_places,
        "activities": activities,
    }
