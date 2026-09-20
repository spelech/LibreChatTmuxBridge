"""
OpenAI-compatible API endpoints (/v1/models, /v1/chat/completions).
"""

import logging
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from librechat_tmux_bridge.config import settings
from librechat_tmux_bridge.core.models import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ModelList,
    ModelObject,
    Usage,
)
from librechat_tmux_bridge.core.terminal_streamer import TerminalStreamer
from librechat_tmux_bridge.core.tmux_driver import ITmuxDriver, TmuxDriver
from librechat_tmux_bridge.infrastructure.taps import diagnostic_tap

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["OpenAI Compatibility"])


def get_driver() -> ITmuxDriver:
    """Dependency provider for TmuxDriver."""
    return TmuxDriver(settings)


def get_streamer(driver: ITmuxDriver = Depends(get_driver)) -> TerminalStreamer:
    """Dependency provider for TerminalStreamer."""
    return TerminalStreamer(driver, settings)


def extract_session_name(model_id: str) -> str:
    """Extract clean tmux session name from OpenAI model ID."""
    if model_id.startswith("tmux:"):
        return model_id[5:]
    return model_id


@router.get("/models", response_model=ModelList)
async def list_models(driver: ITmuxDriver = Depends(get_driver)) -> ModelList:
    """
    Dynamically discover running tmux sessions and expose them as OpenAI models.
    Always includes 'tmux:new' as an entrypoint for spawning new sessions.
    """
    sessions = await driver.list_sessions()
    now_ts = int(time.time())

    models = [
        ModelObject(
            id="tmux:new",
            object="model",
            created=now_ts,
            owned_by="tmux-bridge",
        )
    ]

    for s in sessions:
        models.append(
            ModelObject(
                id=f"tmux:{s.name}",
                object="model",
                created=s.created or now_ts,
                owned_by="tmux-bridge",
            )
        )

    return ModelList(object="list", data=models)


@router.get("/models/{model_id:path}", response_model=ModelObject)
async def get_model(model_id: str, driver: ITmuxDriver = Depends(get_driver)) -> ModelObject:
    """Retrieve metadata for a specific tmux model session."""
    session_name = extract_session_name(model_id)
    if session_name == "new" or await driver.has_session(session_name):
        return ModelObject(
            id=f"tmux:{session_name}",
            object="model",
            created=int(time.time()),
            owned_by="tmux-bridge",
        )
    raise HTTPException(status_code=404, detail=f"Model/Session '{model_id}' not found")


@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    streamer: TerminalStreamer = Depends(get_streamer),
):
    """
    Execute terminal turns against the target tmux session and stream output
    via Server-Sent Events (SSE) or return complete text.
    """
    session_name = extract_session_name(request.model)

    # Extract user prompt from last message
    user_prompt = ""
    for msg in reversed(request.messages):
        if msg.role == "user" and msg.content:
            user_prompt = msg.content
            break

    req_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    start_time = time.time()

    diagnostic_tap.record_event(
        "request",
        {
            "id": req_id,
            "session": session_name,
            "stream": request.stream,
            "prompt_length": len(user_prompt),
        },
    )

    if request.stream:
        # Return SSE generator stream
        generator = streamer.stream_command(session_name, user_prompt, stream_id=req_id)
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        # Non-streaming mode
        output_text = await streamer.execute_command_non_streaming(session_name, user_prompt)

        return ChatCompletionResponse(
            id=req_id,
            object="chat.completion",
            created=int(start_time),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=output_text),
                    finish_reason="stop",
                )
            ],
            usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )
