# Getting started: build your first agent

About fifteen minutes from a fresh clone to an agent answering you.

## 1. What an agent is, here

An agent in this repo is a folder with:

- a **brief** (`instructions.md`): what it does, step by step, and what it must never do;
- optional **Python code** (`src/main.py`): anything the brief alone can't do;
- a **listing** (`agent.yaml`): name, summary, who it is for, pricing and what data it collects.

It runs on a **maava gateway**, which owns the models and keys. Your code never holds an API key
for a model; it talks to the gateway through the [SDK](../sdk).

```
you ──► your agent (src/main.py) ──► maava-agent-sdk ──► maava gateway ──► model
```

## 2. Set up

You need Python 3.10 or newer and a running maava gateway
([maavadao/maava-gateway](https://github.com/maavadao/maava-gateway)) with its chat endpoint on:

```json5
{ gateway: { http: { endpoints: { chatCompletions: { enabled: true } } } } }
```

```bash
git clone https://github.com/maavadao/community-agents && cd community-agents
python -m venv .venv && source .venv/bin/activate
pip install -e sdk pytest pyyaml
export MAAVA_GATEWAY_URL=http://127.0.0.1:18789
export MAAVA_GATEWAY_TOKEN=<your gateway token>
```

## 3. Try an existing agent

```bash
cd agents/content-research-agent
python src/main.py "Plan a 5-minute video on how vaccines work, for 12-year-olds"
```

Read `instructions.md` next to it. That file is the whole agent.

## 4. Make your own

```bash
cp -r agents/_template agents/my-agent
```

1. Write `instructions.md`.
2. Fill in `agent.yaml`. Agents must be free for education, and `data_collected` must be honest.
3. Fill in `README.md`.
4. Run `python src/main.py "a test request"`.

## 5. Add code when the brief isn't enough

Edit `run()` in `src/main.py`. The SDK gives you two calls:

```python
from maava_agent import Agent, Gateway

gateway = Gateway()                       # reads MAAVA_GATEWAY_URL and MAAVA_GATEWAY_TOKEN
reply = gateway.chat("Summarise this", system="You are concise.")
result = gateway.invoke_tool("<tool name>", {"<arg>": "<value>"})   # any tool your gateway's policy allows
```

A typical pattern is to fetch or prepare material in Python, hand it to the agent, then check or
reshape the reply:

```python
def run(request: str) -> str:
    material = fetch_pages(request)               # your code
    reply = agent.run(f"{request}\n\nSources:\n{material}")
    return add_citation_list(reply, material)     # your code
```

Keep dependencies few, pin them in `requirements.txt`, and put variable names (never values) in
`.env.example`.

## 6. Check it

```bash
python scripts/validate.py      # layout, listing fields, free for education
scripts/test_agents.sh          # every agent's tests and the SDK's
```

## 7. Share it

Open a pull request. CI runs the same checks. After a maintainer's review and the community safety
review, your agent is published to the [index](https://maavadao.github.io/community-agents/index.json)
and appears on maavadao.com.

## Questions

Open an issue in this repository.
