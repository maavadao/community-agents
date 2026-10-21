# Contributing an agent

## Ground rules

- **Free for education.** Schools, colleges, universities, teachers, students and orphanages use
  every agent here for free.
- **Apache 2.0.** Your code is released under the repo's licence. You keep your authorship.
- **Children first.** No tracking, no advertising, no collecting more data than the agent needs.
  Say exactly what you collect in `data_collected`.
- **No secrets in the repo.** Read keys from environment variables and document them.
- **Your own words and your own code.** Don't copy content you don't have the right to share.

## Add a new agent

1. Fork this repository.
2. Copy `agents/_template` to `agents/<name>/` (lowercase letters, digits and hyphens).
3. Put the code in the folder. Keep it self-contained, with its own README explaining what it
   does, how to run it and which environment variables it needs.
4. Fill in `agent.yaml`. It uses the same fields as the
   [registry's agent template](https://github.com/maavadao/marketplace-registry/blob/main/templates/agent.yaml),
   except `links.repository` is filled in for you by maintainers.
5. Open a pull request. CI checks the folder structure, and a maintainer reviews the code.
6. After the community safety review passes, a maintainer adds the listing to the marketplace
   registry.

## What goes in an agent folder

```
agents/<name>/
├── agent.yaml          required: listing details (see the template)
├── README.md           required: what it does, how to run it, env vars, data
├── instructions.md     the agent's written brief (optional if the code holds it)
├── src/main.py         the code (uses maava-agent-sdk), if the agent has any (agent.entrypoint)
├── requirements.txt    required when there is code; pin versions
├── tests/              tests for the code
└── .env.example        names of the environment variables, never real values
```

An agent can be only instructions, or Python code, or both. CI checks the folder layout,
compiles the entry point and rejects committed `.env` files. Run `python scripts/validate.py` and
`scripts/test_agents.sh` before you open a pull request. See the
[getting started guide](docs/getting-started.md).

## Improve an existing agent

Open an issue describing the change, then a pull request. Small fixes can skip the issue.

## Maintainers

Every agent has a named maintainer in `agent.yaml`. If a maintainer goes quiet for six months,
the maavaDao team may find a new one.

## Revenue

You get rewarded for your work, and help children in need. When an agent earns money, 60%
rewards the community who built it and 40% funds maava's education work for children in need. How the community share is divided between contributors is decided through
maavaDao governance.
