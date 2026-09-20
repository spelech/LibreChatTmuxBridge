# LibreChat Integration Guide

Integrating **LibreChatTmuxBridge** with LibreChat gives you two powerful modes:
1. **Mode 1: Direct Pseudo-LLM Terminal Driver** (Zero-token streaming via `/v1/chat/completions`)
2. **Mode 2: FastMCP Agent Copilot** (Reasoning LLM with tools via `/mcp/sse`)

---

## ⚙️ Configuration in `librechat.yaml`

Edit your `librechat.yaml` file (e.g. `/containers/ai/librechat/librechat.yaml`):

### 1. Custom Endpoint (Mode 1)

Add the bridge under `endpoints.custom`:

```yaml
endpoints:
  custom:
    - name: "Tmux Terminal"
      apiKey: "sk-tmux"
      baseURL: "http://10.0.0.10:8035/v1"
      models:
        fetch: true
      titleConvo: true
      modelDisplayLabel: "Host Tmux"
      dropParams:
        - stop
        - temperature
```

### 2. FastMCP Server Registration (Mode 2)

Add the bridge under `mcpSettings.allowedAddresses` and `mcpServers`:

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

---

## 🔄 Restarting LibreChat

Once `librechat.yaml` is updated, restart your LibreChat container:

```bash
docker compose restart librechat
```

---

## 📱 Verifying in the UI

1. Open LibreChat (e.g. `https://librechat.wileyriley.com` or `http://localhost:8451`).
2. Tap the endpoint selector and choose **"Host Tmux"**.
3. The model dropdown automatically populates with active sessions (e.g. `tmux:agy-work`, `tmux:infra`, `tmux:new`).
4. Type `uptime` or `/list` to begin driving your terminal!
