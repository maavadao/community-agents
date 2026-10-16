# Content Research Agent

Plans content: finds and summarises trustworthy sources, suggests angles, and builds an outline with citations.

Stage 1 of 3 in the content lifecycle (research and plan → create → review and publish).

Given a topic and an audience, it finds sources, summarises what each says in its own words, notes where sources disagree, suggests three angles, and returns an outline with a numbered source list. It always shows where a claim came from and says when it could not find support.

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
