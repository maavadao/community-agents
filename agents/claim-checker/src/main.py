"""Entry point: checks a forwarded claim against Wikipedia and says what holds up, with sources.

1. The gateway splits the claim into parts that can each be checked, with search terms for each.
2. Plain code searches Wikipedia (free, no key) and fetches the lead of the best articles.
3. The gateway judges every part against that evidence only, citing the articles.

`--raw` skips both gateway steps and prints the evidence found for the whole claim.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from maava_agent import Agent

agent = Agent.from_folder(Path(__file__).resolve().parent.parent)

USER_AGENT = "maavaDao-claim-checker/0.1 (https://github.com/maavadao/maava-agents)"
RESULTS_PER_SEARCH = 3
MAX_PARTS = 5
EXTRACT_CHARS = 1500

SPLIT_BRIEF = """Split the message into at most 5 separate factual statements that can each be checked
against an encyclopaedia. Skip opinions, insults and calls to action. For each, give 1 or 2 short
search queries (names, places, events, numbers), in the language of the Wikipedia edition given.
Answer with JSON only, in this shape:
{"parts": [{"statement": "...", "searches": ["...", "..."]}]}"""


def _wiki(lang: str, params: dict) -> dict:
    url = f"https://{lang}.wikipedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json", "formatversion": 2})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def search(query: str, lang: str = "en") -> list[str]:
    hits = _wiki(lang, {"action": "query", "list": "search", "srsearch": query, "srlimit": RESULTS_PER_SEARCH})
    return [h["title"] for h in hits["query"]["search"]]


def articles(titles: list[str], lang: str = "en") -> list[dict]:
    """The lead section of each article, as plain text, with its URL."""
    if not titles:
        return []
    data = _wiki(lang, {"action": "query", "prop": "extracts|info", "inprop": "url", "exintro": 1,
                        "explaintext": 1, "exchars": EXTRACT_CHARS, "redirects": 1, "titles": "|".join(titles)})
    return [{"title": p["title"], "url": p["fullurl"], "text": p.get("extract", "").strip()}
            for p in data["query"]["pages"] if not p.get("missing") and p.get("extract")]


def split_claim(claim: str, lang: str) -> list[dict]:
    """Ask the gateway for checkable parts; fall back to the whole claim as one part."""
    reply = agent.gateway.chat(f"Wikipedia edition: {lang}\n\nMessage:\n{claim}", system=SPLIT_BRIEF)
    return parse_parts(reply) or [{"statement": claim, "searches": [claim[:200]]}]


def parse_parts(reply: str) -> list[dict]:
    m = re.search(r"\{.*\}", reply, re.S)
    try:
        parts = json.loads(m.group(0))["parts"] if m else []
    except (json.JSONDecodeError, KeyError, TypeError):
        return []
    return [{"statement": str(p["statement"]), "searches": [str(s) for s in p.get("searches", [])][:2] or [str(p["statement"])]}
            for p in parts if isinstance(p, dict) and p.get("statement")][:MAX_PARTS]


def gather(parts: list[dict], lang: str) -> list[dict]:
    """Attach evidence to every part. Each article is fetched once even if several parts need it."""
    titles_per_part = []
    for p in parts:
        titles = []
        for q in p["searches"]:
            titles += [t for t in search(q, lang) if t not in titles]
        titles_per_part.append(titles)
    all_titles = list(dict.fromkeys(t for ts in titles_per_part for t in ts))
    found = {a["title"]: a for i in range(0, len(all_titles), 20) for a in articles(all_titles[i : i + 20], lang)}
    return [{**p, "evidence": [found[t] for t in ts if t in found]} for p, ts in zip(parts, titles_per_part)]


def run(claim: str, lang: str = "en", *, raw: bool = False) -> str:
    parts = [{"statement": claim, "searches": [claim[:200]]}] if raw else split_claim(claim, lang)
    checked = gather(parts, lang)
    body = json.dumps(checked, ensure_ascii=False, indent=1)
    if raw:
        return body
    return agent.run(f"Claim as received:\n{claim}\n\nParts and Wikipedia evidence ({lang}):\n{body}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("claim", help="the message or claim to check, in quotes")
    ap.add_argument("--lang", default="en", help="Wikipedia edition to check against, e.g. en, fr, sw, hi (default en)")
    ap.add_argument("--raw", action="store_true", help="print the evidence without asking the gateway")
    args = ap.parse_args()
    print(run(args.claim, args.lang, raw=args.raw))
