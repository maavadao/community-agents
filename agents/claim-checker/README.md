# Claim Checker

Checks a forwarded message or rumour against Wikipedia and says, part by part, what holds up,
with sources.

False messages spread because checking them takes longer than forwarding them. Paste what you
received. Claim Checker splits it into the statements that can be checked, searches
[Wikipedia](https://www.wikipedia.org) for each, and judges every statement against what the
articles actually say. Every verdict quotes and links its source, and "can't tell" is an
allowed answer.

## How it works

1. The gateway splits the message into up to five checkable statements, with search terms.
2. The code searches Wikipedia and fetches the lead section of the best articles.
3. The gateway judges each statement against that evidence only.

## Run it

Needs a running [maava gateway](https://github.com/maavadao/maava-gateway) with its chat endpoint
enabled. See the [getting started guide](../../docs/getting-started.md).

```bash
pip install -r requirements.txt
cp .env.example .env   # then set MAAVA_GATEWAY_TOKEN
export $(grep -v '^#' .env | xargs)
python src/main.py "The Great Wall of China is the only man-made structure visible from space"
python src/main.py "La tour Eiffel a été construite en 1889" --lang fr
```

To see only the Wikipedia evidence for the whole message, with no gateway:

```bash
python src/main.py "your claim" --raw
```

Its brief is in [`instructions.md`](instructions.md).

## Limits

- It checks against Wikipedia only. Very recent events and local news are often missing, and it
  says "can't tell" rather than guess.
- It reads article leads, not whole articles.

## Data

The message is sent to your maava gateway, and search terms to Wikipedia. Nothing is kept after
the session. No accounts or analytics.

Article text from Wikipedia, licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

## Licence

Apache 2.0.
