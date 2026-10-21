# maava Community Agents

maava Community Agents is a fully open-source suite of AI agents for sales, marketing and growth,
built on top of open-source AI libraries that anyone can inspect, fork and improve.

**We're not building from scratch.** We're standing on the shoulders of the most proven,
community-validated open-source agent repositories on GitHub: thousands of stars, hundreds of
contributors, battle-tested prompts and workflows. We take what the community has already built,
refined and stress-tested, and make it work for you.

**We customise every open-source agent for your specific use case.** No generic templates. No
one-size-fits-all prompts. Each agent is tailored to your industry, your pipeline, your voice and
your revenue targets, so it doesn't just work, it works for you.

Developers contribute new agents, prompts and workflows. Businesses deploy customised agents to
run real revenue operations: prospecting, closing, retention and beyond. When a business puts a
maava agent to work and it earns, a share of that revenue flows back to the ecosystem:

- **Maava Charity:** funding the mission (40%)
- **The developer community:** rewarding the people who built it (60%)

No middlemen. No SaaS lock-in. Just open code, real revenue, and a circular economy where the
people who build get paid, and the proceeds do good.

## How this repo fits with the others

| Repo | Purpose |
| --- | --- |
| **maava-Community-Agents** (this repo) | The **code** of agents the community builds together, shown on [maavadao.com/agents](https://maavadao.com/agents) |
| [marketplace-registry](https://github.com/maavadao/marketplace-registry) | The **list** of tools and agents shown on [maavadao.com/marketplace](https://maavadao.com/marketplace). Anyone can list a product they built elsewhere |
| [open-source-ai-repos](https://github.com/maavadao/open-source-ai-repos) | A directory of open-source AI repos and the developers behind them, on [maavadao.com/repos](https://maavadao.com/repos) and [maavadao.com/developers](https://maavadao.com/developers) |
| [maava](https://github.com/maavadao/maava) | The platform that runs agents |

An agent here is also listed in the registry, with `links.repository` pointing at its folder.

## What's in it

Each agent lives in its own folder under [`agents/`](agents), with its code, a README and an
`agent.yaml` describing it. We start with a small founding set of agents maintained by the
maavaDao team. Once they are in place, we invite developers and contributors to improve them and
to add agents of their own.

## The index

On every merge to `main`, a GitHub Action validates the agents, runs `scripts/build_index.py` and
publishes `index.json` on GitHub Pages:

```
https://maavadao.github.io/maava-Community-Agents/index.json
```

[maavadao.com/agents](https://maavadao.com/agents) reads it, so a merged agent shows up on the website within
the hour, with no change to the website's code.

## Contribute

New here? Start with the [getting started guide](docs/getting-started.md). The
[`sdk/`](sdk) folder holds `maava-agent-sdk`, a small Python library for talking to a maava gateway.

1. Read [CONTRIBUTING.md](CONTRIBUTING.md).
2. Copy [`agents/_template`](agents/_template) to `agents/<your-agent>/`.
3. Build it, fill in `agent.yaml`, and open a pull request.

Agents go through community safety review (age suitability, data collection, fairness) before
they are listed in the marketplace.

## Licence

Apache 2.0. See [LICENSE](LICENSE).
