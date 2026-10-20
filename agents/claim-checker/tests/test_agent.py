import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import main


def test_instructions_load():
    assert main.agent.instructions.strip()


def test_parse_parts_reads_json_inside_prose():
    reply = 'Sure:\n```json\n{"parts": [{"statement": "A was built in 1889", "searches": ["A", "A history", "extra"]}, {"x": 1}]}\n```'
    assert main.parse_parts(reply) == [{"statement": "A was built in 1889", "searches": ["A", "A history"]}]


def test_parse_parts_rejects_garbage():
    assert main.parse_parts("I can't do that") == []
    assert main.parse_parts('{"parts": "nope"}') == []


def test_split_claim_falls_back_to_whole_claim(monkeypatch):
    monkeypatch.setattr(main.agent.gateway, "chat", lambda *a, **k: "no json here")
    assert main.split_claim("the moon is cheese", "en") == [{"statement": "the moon is cheese", "searches": ["the moon is cheese"]}]


def test_gather_fetches_each_article_once(monkeypatch):
    results = {"q1": ["Moon", "Cheese"], "q2": ["Moon"]}
    fetched = []

    def fake_articles(titles, lang):
        fetched.append(list(titles))
        return [{"title": t, "url": f"https://en.wikipedia.org/wiki/{t}", "text": f"{t} lead"} for t in titles]

    monkeypatch.setattr(main, "search", lambda q, lang: results[q])
    monkeypatch.setattr(main, "articles", fake_articles)
    out = main.gather([{"statement": "a", "searches": ["q1"]}, {"statement": "b", "searches": ["q2"]}], "en")
    assert fetched == [["Moon", "Cheese"]]
    assert [e["title"] for e in out[0]["evidence"]] == ["Moon", "Cheese"]
    assert [e["title"] for e in out[1]["evidence"]] == ["Moon"]
