# Planting Advisor

Tells smallholder farmers and gardeners when to sow, water and protect a crop, from real weather
for their place.

Rains no longer arrive when they used to, and sowing a week too early or too late can lose a
whole season. Most growers have no agronomist to ask. Name your town and your crop: Planting
Advisor reads the last 30 days of weather and the next 16 for that exact place from
[Open-Meteo](https://open-meteo.com) and turns them into a plain plan.

It looks at soil temperature (can the seed germinate?), the rain of the last month against
evaporation (is the ground wet enough?), and the coming frost, heat, heavy-rain, wind and dry-spell
days.

## Run it

The weather facts need no gateway and no key:

```bash
pip install -r requirements.txt
python src/main.py "Kisumu, Kenya" maize --raw
python src/main.py "-0.09,34.77" beans --raw
```

For the plan, it needs a running [maava gateway](https://github.com/maavadao/maava-gateway) with
its chat endpoint enabled. See the [getting started guide](../../docs/getting-started.md).

```bash
cp .env.example .env   # then set MAAVA_GATEWAY_TOKEN
export $(grep -v '^#' .env | xargs)
python src/main.py "Kisumu, Kenya" maize "Is it too late to plant this season?"
```

Its brief is in [`instructions.md`](instructions.md).

## Limits

- Forecasts beyond 7 days are rough, and soil readings cover only the next few days.
- It knows weather, not your soil, seed variety or pests. It points to a local extension officer
  for those, and never recommends chemicals.

## Data

The place you name is sent to Open-Meteo to look up its weather. Nothing else is collected, and
nothing is kept after the session. No accounts or analytics.

Weather data by [Open-Meteo.com](https://open-meteo.com), licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Licence

Apache 2.0.
