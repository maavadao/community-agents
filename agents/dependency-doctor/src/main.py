"""Entry point: scans a lockfile for known vulnerabilities and says what to upgrade first.

The scan is plain code against OSV.dev (free, no key). The gateway only turns the findings into a
short, prioritised plan, so `--raw` works with no gateway at all.
"""
from __future__ import annotations

import json
import re
import tomllib
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from maava_agent import Agent

agent = Agent.from_folder(Path(__file__).resolve().parent.parent)

OSV = "https://api.osv.dev/v1"
BATCH = 1000  # OSV's querybatch limit
SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MODERATE": 2, "MEDIUM": 2, "LOW": 1}


@dataclass(frozen=True)
class Package:
    ecosystem: str  # OSV ecosystem name: npm, PyPI, crates.io
    name: str
    version: str


@dataclass
class Vuln:
    id: str
    summary: str
    severity: str
    fixed: str | None  # the lowest fixed version above the installed one, if OSV knows it


@dataclass
class Finding:
    package: Package
    vulns: list[Vuln] = field(default_factory=list)

    @property
    def worst(self) -> int:
        return max((SEVERITY_RANK.get(v.severity, 0) for v in self.vulns), default=0)

    @property
    def upgrade_to(self) -> str | None:
        """The lowest version that fixes every vulnerability with a known fix."""
        fixes = [v.fixed for v in self.vulns if v.fixed]
        return max(fixes, key=version_key) if fixes else None


# --- Lockfiles -------------------------------------------------------------------------------


def parse_lockfile(path: Path) -> list[Package]:
    text = path.read_text()
    name = path.name
    if name == "package-lock.json":
        return _npm(json.loads(text))
    if name == "poetry.lock":
        return [Package("PyPI", p["name"], p["version"]) for p in tomllib.loads(text).get("package", [])]
    if name == "Cargo.lock":
        return [Package("crates.io", p["name"], p["version"]) for p in tomllib.loads(text).get("package", [])]
    if name.endswith(".txt"):
        return _requirements(text)
    raise ValueError(f"unsupported file {name}: use package-lock.json, poetry.lock, Cargo.lock or a pinned requirements.txt")


def _npm(lock: dict) -> list[Package]:
    found = set()
    for key, meta in (lock.get("packages") or {}).items():  # lockfileVersion 2 and 3
        if key and "version" in meta and not meta.get("link"):
            found.add(Package("npm", key.rsplit("node_modules/", 1)[-1], meta["version"]))
    if not found:  # lockfileVersion 1
        stack = list((lock.get("dependencies") or {}).items())
        while stack:
            pkg, meta = stack.pop()
            if "version" in meta:
                found.add(Package("npm", pkg, meta["version"]))
            stack.extend((meta.get("dependencies") or {}).items())
    return sorted(found, key=lambda p: (p.name, p.version))


def _requirements(text: str) -> list[Package]:
    found = []
    for line in text.splitlines():
        m = re.match(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)(\[[^\]]*\])?\s*==\s*([^\s;#\\]+)", line)
        if m:
            found.append(Package("PyPI", m.group(1), m.group(3)))
    return found


# --- OSV -------------------------------------------------------------------------------------


def _osv(path: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(
        OSV + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        return json.load(res)


def version_key(v: str) -> tuple:
    """A lenient sort key that orders SemVer and PEP 440 release numbers correctly in common cases."""
    parts = re.split(r"[.\-+]", v)
    return tuple((0, int(p), "") if p.isdigit() else (-1, 0, p) for p in parts)


def _severity(vuln: dict) -> str:
    sev = (vuln.get("database_specific") or {}).get("severity")
    if isinstance(sev, str) and sev.upper() in SEVERITY_RANK:
        return sev.upper()
    return "UNKNOWN"


def _fixed_for(vuln: dict, pkg: Package) -> str | None:
    fixes = []
    for aff in vuln.get("affected", []):
        p = aff.get("package") or {}
        if p.get("name", "").lower() != pkg.name.lower() or p.get("ecosystem") != pkg.ecosystem:
            continue
        for rng in aff.get("ranges", []):
            fixes += [e["fixed"] for e in rng.get("events", []) if "fixed" in e]
    above = [f for f in fixes if version_key(f) > version_key(pkg.version)]
    return min(above, key=version_key) if above else None


def scan(packages: list[Package]) -> list[Finding]:
    """Look every package up on OSV and return the vulnerable ones, worst first."""
    hits: dict[Package, list[str]] = {}
    for i in range(0, len(packages), BATCH):
        chunk = packages[i : i + BATCH]
        queries = [{"package": {"name": p.name, "ecosystem": p.ecosystem}, "version": p.version} for p in chunk]
        for pkg, res in zip(chunk, _osv("/querybatch", {"queries": queries})["results"]):
            if res.get("vulns"):
                hits[pkg] = [v["id"] for v in res["vulns"]]

    details: dict[str, dict] = {}
    findings = []
    for pkg, ids in hits.items():
        finding = Finding(pkg)
        seen: set[str] = set()
        # GitHub advisories carry a severity, so keep them and drop their aliases from other databases.
        for vid in sorted(ids, key=lambda i: (not i.startswith("GHSA-"), i)):
            if vid not in details:
                details[vid] = _osv(f"/vulns/{vid}")
            d = details[vid]
            aliases = {vid, *d.get("aliases", [])}
            if aliases & seen:
                seen |= aliases
                continue
            seen |= aliases
            finding.vulns.append(Vuln(vid, d.get("summary") or d.get("details", "")[:120], _severity(d), _fixed_for(d, pkg)))
        findings.append(finding)
    return sorted(findings, key=lambda f: (-f.worst, -len(f.vulns), f.package.name))


def report(findings: list[Finding], total: int) -> str:
    if not findings:
        return f"Scanned {total} packages. No known vulnerabilities in OSV.dev."
    lines = [f"Scanned {total} packages. {len(findings)} have known vulnerabilities.", ""]
    for f in findings:
        p = f.package
        target = f"upgrade to {f.upgrade_to}" if f.upgrade_to else "no fixed version known"
        lines.append(f"- {p.ecosystem} {p.name} {p.version}: {len(f.vulns)} vuln(s), {target}")
        for v in sorted(f.vulns, key=lambda v: -SEVERITY_RANK.get(v.severity, 0)):
            lines.append(f"    - [{v.severity}] {v.id}: {v.summary} (https://osv.dev/vulnerability/{v.id})")
    return "\n".join(lines)


def run(lockfile: str, *, raw: bool = False) -> str:
    packages = parse_lockfile(Path(lockfile))
    text = report(scan(packages), len(packages))
    return text if raw else agent.run(f"Lockfile: {Path(lockfile).name}\n\n{text}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("lockfile")
    ap.add_argument("--raw", action="store_true", help="print the scan without asking the gateway for a plan")
    args = ap.parse_args()
    print(run(args.lockfile, raw=args.raw))
