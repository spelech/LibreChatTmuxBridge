# LibreChat Integration Guide

This guide explains how to connect LibreChat to the LibreChatTmuxBridge daemon.

LibreChat supports two integration methods:
1. **Direct Terminal Driver:** Uses the OpenAI-compatible endpoint for zero-token terminal execution.
2. **Model Context Protocol (MCP) Copilot:** Uses FastMCP tools for LLM reasoning and multi-session supervision.

## Configuration in librechat.yaml

Open and edit your `librechat.yaml` file (for example, `/containers/ai/librechat/librechat.yaml`).

### Configure Custom Endpoint

Add the bridge definition under the `endpoints.custom` section:

```yaml
endpoints:
  custom:
    - name: "Tmux Terminal"
      apiKey: "sk-tmux"
      baseURL: "http://10.0.0.10:8035/v1"
      models:
        default:
          - tmux:new
        fetch: true
      titleConvo: true
      modelDisplayLabel: "Host Tmux"
      dropParams:
        - stop
        - temperature
```

### Configure FastMCP Server

Add the bridge URL to `mcpSettings.allowedAddresses` and register the server under `mcpServers`:

```yaml
mcpSettings:
  allowedAddresses:
    - 10.0.0.10:8035
    - localhost:8035

mcpServers:
  tmux-bridge:
    type: sse
    url: http://10.0.0.10:8035/mcp/sse
```

## Restart LibreChat

Restart the LibreChat container to apply the configuration changes:

```bash
docker compose restart librechat
```

## Verify Interface Integration

1. Open the LibreChat web interface (for example, `http://localhost:8451` or `https://librechat.wileyriley.com`).
2. Select the endpoint menu and choose **Host Tmux**.
3. Verify that the model selector lists available sessions (for example, `tmux:agy-work`, `tmux:infra`, `tmux:new`).
4. Submit the command `/list` to verify bidirectional communication.
