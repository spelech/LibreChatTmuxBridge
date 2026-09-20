# OpenAI Compatibility API Reference

LibreChatTmuxBridge implements standard OpenAI REST endpoints to seamlessly plug into LibreChat's Custom Endpoints feature.

---

## 📡 `GET /v1/models`

Returns the list of active host tmux sessions formatted as OpenAI models.

### Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "tmux:new",
      "object": "model",
      "created": 1700000000,
      "owned_by": "tmux-bridge"
    },
    {
      "id": "tmux:agy-work",
      "object": "model",
      "created": 1700000120,
      "owned_by": "tmux-bridge"
    },
    {
      "id": "tmux:infra",
      "object": "model",
      "created": 1700000240,
      "owned_by": "tmux-bridge"
    }
  ]
}
```

---

## 📡 `POST /v1/chat/completions`

Executes terminal turns against the target tmux session.

### Request Body

```json
{
  "model": "tmux:infra",
  "messages": [
    {
      "role": "user",
      "content": "docker ps --format 'table {{.Names}}\t{{.Status}}'"
    }
  ],
  "stream": true
}
```

### Streaming SSE Output

When `stream: true`, the endpoint emits standard `text/event-stream` chunks:

```text
data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1700000300,"model":"tmux:infra","choices":[{"index":0,"delta":{"content":"NAMES             STATUS\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1700000300,"model":"tmux:infra","choices":[{"index":0,"delta":{"content":"caddy             Up 12 hours\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1700000300,"model":"tmux:infra","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### Non-Streaming Output

When `stream: false`, the endpoint waits for output stabilization and returns a full response:

```json
{
  "id": "chatcmpl-a1b2c3d4",
  "object": "chat.completion",
  "created": 1700000300,
  "model": "tmux:infra",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "NAMES             STATUS\ncaddy             Up 12 hours\n"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```
