"""A small client for the maava gateway's HTTP API. No third-party dependencies."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class GatewayError(Exception):
    """The gateway could not be reached, or it answered with an error."""


class Gateway:
    """Talks to a maava gateway.

    Reads ``MAAVA_GATEWAY_URL`` (default ``http://127.0.0.1:18789``) and ``MAAVA_GATEWAY_TOKEN``
    from the environment when not given.
    """

    def __init__(self, url: str | None = None, token: str | None = None, timeout: float = 120):
        self.url = (url or os.environ.get("MAAVA_GATEWAY_URL") or "http://127.0.0.1:18789").rstrip("/")
        self.token = token or os.environ.get("MAAVA_GATEWAY_TOKEN")
        self.timeout = timeout

    def _post(self, path: str, body: dict[str, Any], headers: dict[str, str] | None = None) -> Any:
        req = urllib.request.Request(
            self.url + path,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", **({"Authorization": f"Bearer {self.token}"} if self.token else {}), **(headers or {})},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                return json.load(res)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:300]
            raise GatewayError(f"{path} answered {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise GatewayError(f"could not reach the gateway at {self.url}: {exc}") from exc

    def chat(
        self,
        message: str | list[dict[str, str]],
        *,
        system: str | None = None,
        agent: str = "main",
        session: str | None = None,
    ) -> str:
        """Run one agent turn and return the reply text.

        ``message`` is a string or a list of ``{"role", "content"}`` messages. ``agent`` picks the
        gateway agent. Without ``session`` each call is stateless; pass one to keep a conversation.
        """
        messages = [{"role": "user", "content": message}] if isinstance(message, str) else list(message)
        if system:
            messages.insert(0, {"role": "system", "content": system})
        headers = {"x-openclaw-session-key": session} if session else None
        data = self._post("/v1/chat/completions", {"model": f"openclaw:{agent}", "messages": messages}, headers)
        try:
            return data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise GatewayError(f"unexpected reply from the gateway: {str(data)[:300]}") from exc

    def invoke_tool(self, tool: str, args: dict[str, Any] | None = None, *, session: str | None = None) -> Any:
        """Call one gateway tool directly, without a full agent turn. Subject to the gateway's tool policy."""
        body: dict[str, Any] = {"tool": tool, "args": args or {}}
        if session:
            body["sessionKey"] = session
        return self._post("/tools/invoke", body)
