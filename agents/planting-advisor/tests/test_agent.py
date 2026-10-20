import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import main


def test_instructions_load():
    assert main.agent.instructions.strip()


def test_find_place_accepts_coordinates():
    p = main.find_place("-0.09, 34.77")
    assert (p.latitude, p.longitude) == (-0.09, 34.77)


def test_find_place_prefers_named_country(monkeypatch):
    results = [{"name": "Kisumu", "country": "Elsewhere", "country_code": "XX", "latitude": 1, "longitude": 1},
               {"name": "Kisumu", "country": "Kenya", "country_code": "KE", "latitude": -0.1, "longitude": 34.8}]
    monkeypatch.setattr(main, "_get", lambda url, params: {"results": results})
    assert main.find_place("Kisumu, Kenya").latitude == -0.1


def _weather():
    days = [f"2026-10-{d:02d}" for d in range(1, 32)] + [f"2026-11-{d:02d}" for d in range(1, 16)]
    n = len(days)  # 30 past + 16 ahead (today included), as Open-Meteo returns; today is 2026-10-31
    daily = {
        "time": days,
        "precipitation_sum": [2.0] * 30 + [0, 0, 0, 40] + [None] * (n - 34),
        "precipitation_probability_max": [50] * n,
        "temperature_2m_max": [25.0] * 31 + [36.0] + [25.0] * (n - 32),
        "temperature_2m_min": [10.0] * 32 + [1.5] + [10.0] * (n - 33),
        "et0_fao_evapotranspiration": [3.0] * n,
        "wind_speed_10m_max": [10.0] * n,
    }
    hourly = {"time": ["2026-10-31T00:00", "2026-10-31T12:00", "2026-11-01T00:00", "2026-11-09T00:00"],
              "soil_temperature_6cm": [14.0, 18.0, 15.0, None],
              "soil_moisture_3_to_9cm": [0.2, 0.3, None, None]}
    return {"daily": daily, "hourly": hourly}


def test_summarise_splits_at_today_and_flags_risks():
    s = main.summarise(_weather())
    assert s["today"] == "2026-10-31"
    assert s["past_30_days"]["rain_mm"] == 60.0
    assert s["past_30_days"]["water_balance_mm"] == -30.0
    ahead = s["next_16_days"]
    assert ahead["heavy_rain_days"] == ["2026-11-03"]
    assert ahead["heat_stress_days"] == ["2026-11-01"]
    assert ahead["frost_risk_days"] == ["2026-11-02"]
    assert ahead["dry_spell_longest_days"] == 12
    assert s["soil_next_days"] == [{"date": "2026-10-31", "temp_c": 16.0, "moisture_m3m3": 0.25},
                                   {"date": "2026-11-01", "temp_c": 15.0, "moisture_m3m3": None}]
