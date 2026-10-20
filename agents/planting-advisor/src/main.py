"""Entry point: tells a grower when to sow, water and protect a crop, from real weather for their place.

The weather comes from Open-Meteo (free, no key): the last 30 days and the next 16. Plain code
turns it into a few facts that matter for planting, and the gateway explains them for the crop.
`--raw` prints the facts with no gateway.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

from maava_agent import Agent

agent = Agent.from_folder(Path(__file__).resolve().parent.parent)

GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST = "https://api.open-meteo.com/v1/forecast"
DAILY = ["precipitation_sum", "precipitation_probability_max", "temperature_2m_max", "temperature_2m_min",
         "et0_fao_evapotranspiration", "wind_speed_10m_max"]
HOURLY = ["soil_temperature_6cm", "soil_moisture_3_to_9cm"]
FROST_C = 2.0  # air minimum at or below this risks ground frost
HEAT_C = 35.0  # air maximum at or above this stresses most crops at flowering
HEAVY_RAIN_MM = 30.0
GALE_KMH = 50.0
PAST_DAYS = 30


@dataclass
class Place:
    name: str
    latitude: float
    longitude: float
    elevation: float | None


def _get(url: str, params: dict) -> dict:
    with urllib.request.urlopen(f"{url}?{urllib.parse.urlencode(params)}", timeout=30) as res:
        return json.load(res)


def find_place(query: str) -> Place:
    """Accepts a place name ("Kisumu", "Kisumu, Kenya") or "lat,lon"."""
    try:
        lat, lon = (float(x) for x in query.split(","))
        return Place(f"{lat:.3f}, {lon:.3f}", lat, lon, None)
    except ValueError:
        pass
    name, _, country = (s.strip() for s in query.partition(","))
    results = _get(GEOCODE, {"name": name, "count": 10}).get("results") or []
    if country:
        results = [r for r in results if country.lower() in (r.get("country", "") + r.get("country_code", "")).lower()] or results
    if not results:
        raise ValueError(f"couldn't find {query!r}; try a nearby town or 'lat,lon'")
    r = results[0]
    label = ", ".join(x for x in (r["name"], r.get("admin1"), r.get("country")) if x)
    return Place(label, r["latitude"], r["longitude"], r.get("elevation"))


def fetch_weather(place: Place) -> dict:
    return _get(FORECAST, {
        "latitude": place.latitude, "longitude": place.longitude, "timezone": "auto",
        "daily": ",".join(DAILY), "hourly": ",".join(HOURLY), "past_days": PAST_DAYS, "forecast_days": 16,
    })


def _daily_means(hourly: dict, key: str) -> dict[str, float]:
    by_day: dict[str, list[float]] = {}
    for t, v in zip(hourly["time"], hourly[key]):
        if v is not None:
            by_day.setdefault(t[:10], []).append(v)
    return {d: mean(vs) for d, vs in by_day.items()}


def summarise(weather: dict) -> dict:
    """Split the series at today and reduce it to the facts a planting decision turns on."""
    d = weather["daily"]
    today = d["time"][min(PAST_DAYS, len(d["time"]) - 1)]  # local date, since we ask for PAST_DAYS first
    past = [i for i, t in enumerate(d["time"]) if t < today]
    ahead = [i for i, t in enumerate(d["time"]) if t >= today]

    def total(key, idx):
        return round(sum(d[key][i] or 0 for i in idx), 1)

    def days(pred, idx):
        return [d["time"][i] for i in idx if pred(i)]

    soil_t = _daily_means(weather["hourly"], "soil_temperature_6cm")
    soil_m = _daily_means(weather["hourly"], "soil_moisture_3_to_9cm")
    soil_days = [t for t in sorted(soil_t) if t >= today]
    return {
        "today": today,
        "past_30_days": {
            "rain_mm": total("precipitation_sum", past),
            "evaporation_mm": total("et0_fao_evapotranspiration", past),
            "water_balance_mm": round(total("precipitation_sum", past) - total("et0_fao_evapotranspiration", past), 1),
            "rain_days": len(days(lambda i: (d["precipitation_sum"][i] or 0) >= 1, past)),
        },
        "next_16_days": {
            "rain_mm": total("precipitation_sum", ahead),
            "evaporation_mm": total("et0_fao_evapotranspiration", ahead),
            "water_balance_mm": round(total("precipitation_sum", ahead) - total("et0_fao_evapotranspiration", ahead), 1),
            "frost_risk_days": days(lambda i: d["temperature_2m_min"][i] is not None and d["temperature_2m_min"][i] <= FROST_C, ahead),
            "heat_stress_days": days(lambda i: d["temperature_2m_max"][i] is not None and d["temperature_2m_max"][i] >= HEAT_C, ahead),
            "heavy_rain_days": days(lambda i: (d["precipitation_sum"][i] or 0) >= HEAVY_RAIN_MM, ahead),
            "strong_wind_days": days(lambda i: (d["wind_speed_10m_max"][i] or 0) >= GALE_KMH, ahead),
            "dry_spell_longest_days": _longest_run([(d["precipitation_sum"][i] or 0) < 1 for i in ahead]),
        },
        "soil_next_days": [
            {"date": t, "temp_c": round(soil_t[t], 1), "moisture_m3m3": round(soil_m[t], 3) if t in soil_m else None}
            for t in soil_days
        ],
        "daily_forecast": [
            {"date": d["time"][i], "rain_mm": d["precipitation_sum"][i], "rain_chance_pct": d["precipitation_probability_max"][i],
             "min_c": d["temperature_2m_min"][i], "max_c": d["temperature_2m_max"][i]}
            for i in ahead
        ],
    }


def _longest_run(flags: list[bool]) -> int:
    best = run = 0
    for f in flags:
        run = run + 1 if f else 0
        best = max(best, run)
    return best


def run(place: str, crop: str, question: str = "", *, raw: bool = False) -> str:
    where = find_place(place)
    facts = summarise(fetch_weather(where))
    body = json.dumps({"place": where.__dict__, "crop": crop, "weather": facts}, indent=1)
    if raw:
        return body
    ask = question or f"When should I sow, water and protect {crop} over the next two weeks?"
    return agent.run(f"{ask}\n\nWeather facts (Open-Meteo):\n{body}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("place", help='a town ("Kisumu, Kenya") or "lat,lon"')
    ap.add_argument("crop", help="what you want to grow, e.g. maize, beans, tomatoes")
    ap.add_argument("question", nargs="?", default="", help="optional: your own question")
    ap.add_argument("--raw", action="store_true", help="print the weather facts without asking the gateway")
    args = ap.parse_args()
    print(run(args.place, args.crop, args.question, raw=args.raw))
