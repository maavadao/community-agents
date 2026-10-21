# maava agents

The open-source code for agents built by and for the maavaDao community. Every agent here is
free for education, free to read, and free to improve.

maavaDao brings together agentic AI and blockchain technologies to create an open,
community-owned ecosystem for education. There are no listing fees, no creation fees and no
commissions. When a product earns money, 60% rewards the contributors who built it and 40% helps
children in need: deserving children, orphans and street children, through maava's schools.

## How this repo fits with the others

| Repo | Purpose |
| --- | --- |
| **maava-agents** (this repo) | The **code** of agents the community builds together, shown on [maavadao.com/agents](https://maavadao.com/agents) |
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
https://maavadao.github.io/maava-agents/index.json
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
