const form = document.getElementById("search-form");
const cityInput = document.getElementById("city-input");
const statusEl = document.getElementById("status");
const resultSection = document.getElementById("result");

// Weather fields
const cityNameEl = document.getElementById("city-name");
const countryEl = document.getElementById("country");
const coordsEl = document.getElementById("coords");
const tempEl = document.getElementById("temp");
const feelsLikeEl = document.getElementById("feels-like");
const descEl = document.getElementById("description");
const iconEl = document.getElementById("icon");
const sourceBadgeEl = document.getElementById("source-badge");
const humidityEl = document.getElementById("humidity");
const pressureEl = document.getElementById("pressure");
const cloudinessEl = document.getElementById("cloudiness");
const windEl = document.getElementById("wind");
const sunriseEl = document.getElementById("sunrise");
const sunsetEl = document.getElementById("sunset");
const rawJsonEl = document.getElementById("raw-json");

// Advice fields
const adviceSummaryEl = document.getElementById("advice-summary");
const precautionsListEl = document.getElementById("precautions-list");
const avoidListEl = document.getElementById("avoid-list");
const recommendListEl = document.getElementById("recommend-list");

function setStatus(msg, type = "info") {
  statusEl.textContent = msg;
  statusEl.className = `status ${type}`;
}

function clearStatus() {
  statusEl.textContent = "";
  statusEl.className = "status";
}

function fillList(ulEl, items) {
  ulEl.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = "No specific items.";
    ulEl.appendChild(li);
    return;
  }
  items.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    ulEl.appendChild(li);
  });
}

function showResult(data) {
  const { meta, location, weather, wind, sun, advice, provider_raw } = data;

  cityNameEl.textContent = location.city || "Unknown city";
  countryEl.textContent = location.country ? `Country: ${location.country}` : "";
  const lat = location.coordinates.lat;
  const lon = location.coordinates.lon;
  coordsEl.textContent =
    lat != null && lon != null ? `Lat: ${lat}, Lon: ${lon}` : "";

  if (weather.temperature != null) {
    tempEl.textContent = `${weather.temperature.toFixed(1)} °C`;
  } else {
    tempEl.textContent = "";
  }
  if (weather.feels_like != null) {
    feelsLikeEl.textContent = `Feels like ${weather.feels_like.toFixed(1)} °C`;
  } else {
    feelsLikeEl.textContent = "";
  }
  descEl.textContent = weather.description || "";

  if (weather.icon) {
  // WeatherAPI icon may start with //, so ensure protocol
  let iconUrl = weather.icon;
  if (iconUrl.startsWith("//")) {
    iconUrl = "https:" + iconUrl;
  }
  iconEl.src = iconUrl;
  iconEl.style.display = "block";
} else {
  iconEl.style.display = "none";
}


  sourceBadgeEl.textContent =
    meta.source === "cache" ? "From cache" : "Live data";

  humidityEl.textContent =
    weather.humidity != null ? `${weather.humidity} %` : "–";
  pressureEl.textContent =
    weather.pressure != null ? `${weather.pressure} hPa` : "–";
  cloudinessEl.textContent =
    weather.cloudiness != null ? `${weather.cloudiness} %` : "–";

  const windParts = [];
  if (wind.speed != null) windParts.push(`${wind.speed} m/s`);
  if (wind.deg != null) windParts.push(`${wind.deg}°`);
  windEl.textContent = windParts.join(" ") || "–";

  sunriseEl.textContent = sun.sunrise_utc || "–";
  sunsetEl.textContent = sun.sunset_utc || "–";

  rawJsonEl.textContent = JSON.stringify(provider_raw, null, 2);

  // Advice
  if (advice) {
    adviceSummaryEl.textContent = advice.summary || "";
    fillList(precautionsListEl, advice.precautions);
    fillList(avoidListEl, advice.avoid_places);

    const combined = [
      ...(advice.recommended_places || []),
      ...(advice.activities || []),
    ];
    fillList(recommendListEl, combined);
  }

  resultSection.classList.remove("hidden");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const city = cityInput.value.trim();
  if (!city) {
    setStatus("Please enter a city name.", "error");
    return;
  }

  clearStatus();
  setStatus("Loading...", "info");
  resultSection.classList.add("hidden");

  try {
    const resp = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    if (!resp.ok) {
      const body = await resp.json().catch(() => ({}));
      const msg = body.error || `Error: ${resp.status}`;
      setStatus(msg, "error");
      return;
    }
    const data = await resp.json();
    clearStatus();
    showResult(data);
  } catch (err) {
    console.error(err);
    setStatus("Network error. Please try again.", "error");
  }
});
