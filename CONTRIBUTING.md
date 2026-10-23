# Contributing

Every agent is its own repository. This repository is the index that brings them together as Git
submodules. Read [RULES.md](RULES.md) first: it covers safety, privacy, fairness and code quality
for every agent.

## Ground rules

- **Free for education.** Schools, colleges, universities, teachers, students and orphanages use
  every agent here for free.
- **Apache 2.0.** Your code is released under the Apache 2.0 licence. You keep your authorship.
- **Children first.** No tracking, no advertising, no collecting more data than the agent needs.
  Say exactly what you collect in `data_collected`.
- **No secrets in any repo.** Read keys from environment variables and document them.
- **Your own words and your own code.** Don't copy content you don't have the right to share.
  Building on an open-source agent is welcome: keep its licence and credit it.

## Improve an existing agent

Open an issue or a pull request **in that agent's repository** (the table in the
[README](README.md#the-agents) links to each one). Small fixes can skip the issue. Once your change
is merged there, this index picks it up within a day; you don't need a second pull request here.

## Add a new agent

1. **Build it in its own repository.** Create a public repository (in your own account, or ask a
   maintainer for one under `maavadao`, named `community-agent-<name>`). Copy the files from
   [`template/`](template) into it.
2. **Fill it in.** Write `instructions.md`, the code if it needs any, `README.md` and `agent.yaml`.
   `agent.yaml` uses the same fields as the
   [registry's agent template](https://github.com/maavadao/marketplace-registry/blob/main/templates/agent.yaml);
   `links.repository` is filled in for you.
3. **Check it** from a clone of this repository (see below).
4. **Open a pull request here** that adds your repository as a submodule:

   ```bash
   git submodule add https://github.com/<you>/<repo>.git agents/<name>
   python scripts/build_readme.py   # adds your agent to the README's table
   ```

   `<name>` is lowercase letters, digits and hyphens. Use the `https://` URL, not `git@`, so
   everyone can clone it.
5. A maintainer reviews the code. After the community safety review passes, a maintainer adds the
   listing to the marketplace registry.

Folders under `agents/` that aren't submodules fail CI.

## What goes in an agent's repository

```
<repo>/
├── agent.yaml          required: listing details (see the template)
├── README.md           required: what it does, how to run it, env vars, data
├── instructions.md     the agent's written brief (optional if the code holds it)
├── src/main.py         the code (uses maava-agent-sdk), if the agent has any (agent.entrypoint)
├── requirements.txt    required when there is code; pin versions
├── tests/              tests for the code
├── .env.example        names of the environment variables, never real values
└── LICENSE             Apache 2.0
```

An agent can be only instructions, or Python code, or both. Give the repository its own CI that
runs its tests; the maavaDao agents use a small
[test workflow](https://github.com/maavadao/community-agent-claim-checker/blob/main/.github/workflows/test.yml)
you can copy.

## Check your work

From a clone of this repository, with your agent added under `agents/<name>`:

```bash
pip install -r requirements.txt -e sdk pytest
python scripts/validate.py agents/<name>   # layout, listing fields, free for education
scripts/test_agents.sh                     # every agent's tests and the SDK's
```

CI runs the same checks on every pull request. See the [getting started guide](docs/getting-started.md).

## Keeping the index current

Each submodule points at one commit. The [Update agents](.github/workflows/update-agents.yml)
workflow runs daily and moves every agent to the latest commit on its default branch, so merged
changes reach maavadao.com without anyone bumping pointers by hand. If an agent's latest commit
fails validation, the index keeps the last good commit and the workflow's log says why.

## Maintainers

Every agent has a named maintainer in `agent.yaml`, who reviews pull requests in its repository.
If a maintainer goes quiet for six months, the maavaDao team may find a new one.

## Revenue

You get rewarded for your work, and help children in need. When an agent earns money, 60% rewards
the developer community who built it and 40% goes to Maava Charity to educate children in need.
How the community share is divided between contributors is decided through maavaDao governance.
