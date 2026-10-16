# Content Review Agent

Checks a draft before it goes out: facts, tone, accessibility, age suitability and copyright, then prepares it for publishing.

Stage 3 of 3 in the content lifecycle (research and plan → create → review and publish).

Reads a draft against its sources and a publishing checklist: facts match sources, no copied text, language suits the audience's age, headings and alt text for accessibility, and no private information. It returns a pass/fix list and, once fixed, a publish-ready version with title, description and tags.

## Run it

Needs a running [maava gateway](https://github.com/maavadao/maava-gateway) with its chat endpoint
enabled. See the [getting started guide](../../docs/getting-started.md).

```bash
pip install -r requirements.txt
cp .env.example .env   # then set MAAVA_GATEWAY_TOKEN
export $(grep -v '^#' .env | xargs)
python src/main.py "your request"
```

Its brief is in [`instructions.md`](instructions.md).

## Data

Content you provide is processed to answer you and is not kept after the session. No accounts or analytics.

## Licence

Apache 2.0.
