import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from maava_agent import Agent, Gateway, GatewayError

seen = []


class Fake(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        seen.append((self.path, {k.lower(): v for k, v in self.headers.items()}, body))
        if self.headers.get("Authorization") != "Bearer secret":
            self.send_response(401); self.end_headers(); self.wfile.write(b"no"); return
        out = {"choices": [{"message": {"content": "hello"}}]} if self.path == "/v1/chat/completions" else {"ok": True}
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(json.dumps(out).encode())

    def log_message(self, *a):
        pass


@pytest.fixture
def gateway():
    server = HTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    seen.clear()
    yield Gateway(f"http://127.0.0.1:{server.server_port}", "secret", timeout=5)
    server.shutdown()


def test_chat_sends_agent_system_and_session(gateway):
    assert gateway.chat("hi", system="be kind", agent="beta", session="s1") == "hello"
    path, headers, body = seen[0]
    assert path == "/v1/chat/completions"
    assert body["model"] == "openclaw:beta"
    assert body["messages"] == [{"role": "system", "content": "be kind"}, {"role": "user", "content": "hi"}]
    assert headers["x-openclaw-session-key"] == "s1"


def test_invoke_tool(gateway):
    assert gateway.invoke_tool("sessions_list", {"a": 1}) == {"ok": True}
    assert seen[0][2] == {"tool": "sessions_list", "args": {"a": 1}}


def test_bad_token_raises(gateway):
    with pytest.raises(GatewayError, match="401"):
        Gateway(gateway.url, "wrong").chat("hi")


def test_unreachable_raises():
    with pytest.raises(GatewayError, match="could not reach"):
        Gateway("http://127.0.0.1:1", timeout=1).chat("hi")


def test_agent_from_folder(tmp_path, gateway):
    (tmp_path / "instructions.md").write_text("Be helpful.")
    assert Agent.from_folder(tmp_path, gateway=gateway).run("hi") == "hello"
    assert seen[0][2]["messages"][0]["content"] == "Be helpful."


def test_agent_needs_instructions():
    with pytest.raises(ValueError):
        Agent("  ")
