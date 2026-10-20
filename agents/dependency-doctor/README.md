# Dependency Doctor

Scans a project's lockfile for known vulnerabilities and tells you exactly what to upgrade first.

A typical project pulls in hundreds of packages, and audit tools print a wall of advisories with
no order to them. Dependency Doctor checks every package against [OSV.dev](https://osv.dev), the
open vulnerability database, and gives you a short plan: worst first, the exact version to move
to, and the commands to run.

Supported files: `package-lock.json` (npm), `poetry.lock`, pinned `requirements.txt` (PyPI) and
`Cargo.lock` (Rust).

## Run it

The scan needs no gateway and no key:

```bash
pip install -r requirements.txt
python src/main.py path/to/package-lock.json --raw
```

For the prioritised plan, it needs a running [maava gateway](https://github.com/maavadao/maava-gateway)
with its chat endpoint enabled. See the [getting started guide](../../docs/getting-started.md).

```bash
cp .env.example .env   # then set MAAVA_GATEWAY_TOKEN
export $(grep -v '^#' .env | xargs)
python src/main.py path/to/package-lock.json
```

Its brief is in [`instructions.md`](instructions.md).

## Limits

- It only knows what OSV.dev knows. "No known vulnerabilities" is not "safe".
- Version ordering is lenient. Check the suggested target against the advisory for pre-releases.

## Data

Package names and versions from your lockfile are sent to OSV.dev to look them up. Your code is
never sent. Nothing is kept after the session. No accounts or analytics.

## Licence

Apache 2.0.
