import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import main
from main import Package


def test_instructions_load():
    assert main.agent.instructions.strip()


def test_parse_npm_v3(tmp_path):
    lock = {"packages": {"": {"name": "app"}, "node_modules/lodash": {"version": "4.17.15"},
                         "node_modules/a/node_modules/@scope/b": {"version": "1.0.0"},
                         "node_modules/local": {"link": True, "version": "0.0.0"}}}
    f = tmp_path / "package-lock.json"
    f.write_text(json.dumps(lock))
    assert main.parse_lockfile(f) == [Package("npm", "@scope/b", "1.0.0"), Package("npm", "lodash", "4.17.15")]


def test_parse_requirements(tmp_path):
    f = tmp_path / "requirements.txt"
    f.write_text("requests==2.19.0\n# comment\nflask>=2\nuvicorn[standard]==0.20.0 ; python_version>'3'\n")
    assert main.parse_lockfile(f) == [Package("PyPI", "requests", "2.19.0"), Package("PyPI", "uvicorn", "0.20.0")]


def test_parse_cargo(tmp_path):
    f = tmp_path / "Cargo.lock"
    f.write_text('version = 3\n\n[[package]]\nname = "time"\nversion = "0.1.43"\n')
    assert main.parse_lockfile(f) == [Package("crates.io", "time", "0.1.43")]


def test_version_key_orders_releases():
    assert main.version_key("4.17.21") > main.version_key("4.17.9")
    assert main.version_key("10.0") > main.version_key("9.9.9")


VULN = {
    "summary": "ReDoS",
    "database_specific": {"severity": "HIGH"},
    "affected": [{"package": {"name": "lodash", "ecosystem": "npm"},
                  "ranges": [{"events": [{"introduced": "0"}, {"fixed": "4.17.21"}]}]}],
}


def test_scan_ranks_and_picks_upgrade(monkeypatch):
    def fake(path, body=None):
        if path == "/querybatch":
            return {"results": [{"vulns": [{"id": "PYSEC-9"}, {"id": "GHSA-1"}, {"id": "GHSA-2"}]}, {}]}
        if path == "/vulns/GHSA-1":
            return VULN
        if path == "/vulns/PYSEC-9":
            return {**VULN, "aliases": ["GHSA-1"], "database_specific": {}}
        return {**VULN, "database_specific": {"severity": "CRITICAL"},
                "affected": [{"package": {"name": "lodash", "ecosystem": "npm"},
                              "ranges": [{"events": [{"introduced": "0"}, {"fixed": "4.17.19"}]}]}]}

    monkeypatch.setattr(main, "_osv", fake)
    findings = main.scan([Package("npm", "lodash", "4.17.15"), Package("npm", "safe", "1.0.0")])
    assert len(findings) == 1
    assert [v.id for v in findings[0].vulns] == ["GHSA-1", "GHSA-2"]  # PYSEC-9 is an alias of GHSA-1
    assert findings[0].worst == 4
    assert findings[0].upgrade_to == "4.17.21"
    text = main.report(findings, 2)
    assert "upgrade to 4.17.21" in text and "[CRITICAL] GHSA-2" in text
