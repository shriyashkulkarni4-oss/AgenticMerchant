"""
Agentic Chat API Router for AgenticBuy.

Endpoints and WebSocket connection for consumers to interact with the
Gemma-powered autonomous shopping and negotiation agent.
"""

from typing import Any, Dict, List, Optional
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import decode_access_token, get_optional_current_user
from app.config import get_settings
from app.database import async_session, get_db
from app.models.user import User
from app.services.agent import AgenticBuyAgent

router = APIRouter(prefix="/api/v1/chat", tags=["agent-chat"])
settings = get_settings()


class ChatMessageRequest(BaseModel):
    """Schema for chat input message to the agent."""

    message: str
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Schema for conversational agent response."""

    session_id: str
    response: str
    actions: List[Dict[str, Any]] = []


@router.post(
    "/",
    response_model=ChatMessageResponse,
    summary="Chat with the Gemma AgenticBuy shopping agent",
)
async def chat_with_agent(
    payload: ChatMessageRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageResponse:
    """Send a message to the agent to find products, negotiate, or complete purchases."""
    agent = AgenticBuyAgent(
        ollama_url=settings.OLLAMA_BASE_URL,
        model_name=settings.GEMMA_MODEL,
        db_session=db,
        user=current_user,
    )
    result = await agent.chat(
        message=payload.message,
        session_id=payload.session_id,
    )
    return ChatMessageResponse(
        session_id=result["session_id"],
        response=result["response"],
        actions=result.get("actions", []),
    )


@router.websocket("/ws/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    """Real-time bi-directional chat with the Gemma agent over WebSocket."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            async with async_session() as db:
                agent = AgenticBuyAgent(
                    ollama_url=settings.OLLAMA_BASE_URL,
                    model_name=settings.GEMMA_MODEL,
                    db_session=db,
                    user=None,
                )
                result = await agent.chat(message=data, session_id=session_id)
                await websocket.send_json(result)
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for session {session_id}")
