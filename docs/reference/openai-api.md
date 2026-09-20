# OpenAI Compatibility API Reference

LibreChatTmuxBridge provides REST endpoints compatible with the OpenAI API specification. These endpoints allow LibreChat to connect to host terminal sessions without custom client plugins.

## Endpoint Overview

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/v1/models` | Returns available host tmux sessions as language models |
| `POST` | `/v1/chat/completions` | Injects terminal input and streams terminal responses |

## GET /v1/models

Queries active tmux sessions and returns them in the OpenAI model list format.

### Request

```http
GET /v1/models HTTP/1.1
Host: 10.0.0.10:8035
Authorization: Bearer sk-tmux
```

### Response Example

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

The model `tmux:new` is always included to allow creating new sessions from the client interface.

## POST /v1/chat/completions

Transmits user messages to the specified tmux session and captures resulting terminal changes.

### Request Body Parameters

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `model` | string | Yes | Target session identifier (for example, `tmux:infra` or `tmux:agy-work`) |
| `messages` | array | Yes | Array of chat messages. The final user message contains the command or keystroke |
| `stream` | boolean | No | Enables Server-Sent Events streaming. Default is `false` |

### Request Example

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

### Streaming Response Format

When `stream` is `true`, the server sets the content type to `text/event-stream` and transmits incremental chunks:

```text
data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1700000300,"model":"tmux:infra","choices":[{"index":0,"delta":{"content":"NAMES             STATUS\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1700000300,"model":"tmux:infra","choices":[{"index":0,"delta":{"content":"caddy             Up 12 hours\n"},"finish_reason":null}]}

data: {"id":"chatcmpl-a1b2c3d4","object":"chat.completion.chunk","created":1700000300,"model":"tmux:infra","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### Non-Streaming Response Format

When `stream` is `false`, the server gathers settled output and returns a single JSON object:

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
