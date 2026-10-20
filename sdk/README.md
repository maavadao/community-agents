# maava-agent-sdk

A tiny Python library for building maava agents. No third-party dependencies.

```python
from maava_agent import Agent

agent = Agent("You explain photosynthesis to ten-year-olds.")
print(agent.run("Why are leaves green?"))
```

It talks to a [maava gateway](https://github.com/maavadao/maava-gateway) over HTTP:

| Method | Gateway endpoint | Use |
| --- | --- | --- |
| `Gateway.chat(...)` | `POST /v1/chat/completions` | Run one agent turn and get the reply |
| `Gateway.invoke_tool(...)` | `POST /tools/invoke` | Call one gateway tool directly |
| `Agent.from_folder(path).run(...)` | `chat` with the folder's `instructions.md` | The normal way to run a maava agent |

## Configure

| Variable | Default | Meaning |
| --- | --- | --- |
| `MAAVA_GATEWAY_URL` | `http://127.0.0.1:18789` | Where the gateway runs |
| `MAAVA_GATEWAY_TOKEN` | none | The gateway's bearer token |

The gateway's chat endpoint is off by default. Turn it on with
`gateway.http.endpoints.chatCompletions.enabled: true` in the gateway config.

## Install

```bash
pip install "maava-agent-sdk @ git+https://github.com/maavadao/maava-agents#subdirectory=sdk"
```

Version 0.1.0 is a first draft; the API may change.
