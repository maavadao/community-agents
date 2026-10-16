# maavaDao community agents

The open-source code for agents built by and for the maavaDao community. Every agent here is
free for education, free to read, and free to improve.

maavaDao brings together agentic AI and blockchain technologies to create an open,
community-owned ecosystem for education. There are no listing fees, no creation fees and no
commissions. When a product earns money, 75% goes to the community who built it and 25% goes
to maava to educate deserving children, orphans and street children.

## How this repo fits with the others

| Repo | Purpose |
| --- | --- |
| **community-agents** (this repo) | The **code** of agents the community builds together |
| [marketplace-registry](https://github.com/maavadao/marketplace-registry) | The **list** of tools and agents shown on [maavadao.com/marketplace](https://maavadao.com/marketplace). Anyone can list a product they built elsewhere |
| [maava](https://github.com/maavadao/maava) | The platform that runs agents |

An agent here is also listed in the registry, with `links.repository` pointing at its folder.

## What's in it

Each agent lives in its own folder under [`agents/`](agents), with its code, a README and an
`agent.yaml` describing it. We start with a small founding set of agents maintained by the
maavaDao team. Once they are in place, we invite developers and contributors to improve them and
to add agents of their own.

## Contribute

1. Read [CONTRIBUTING.md](CONTRIBUTING.md).
2. Copy [`agents/_template`](agents/_template) to `agents/<your-agent>/`.
3. Build it, fill in `agent.yaml`, and open a pull request.

Agents go through community safety review (age suitability, data collection, fairness) before
they are listed in the marketplace.

## Licence

Apache 2.0. See [LICENSE](LICENSE).
