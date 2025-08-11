from fastapi import APIRouter

from backend.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    return ChatResponse(
        answer="This is a mock answer. The RAG pipeline will be connected soon.",
        sources=[],
    ) 