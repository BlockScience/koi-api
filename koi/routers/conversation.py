from fastapi import APIRouter
from pydantic import BaseModel

from koi import llm


router = APIRouter(
    prefix="/llm",
    tags=["Conversation"]
)

class CreateConversation(BaseModel):
    conversation_id: str | None = None

@router.post("")
def create_conversation(obj: CreateConversation):
    """Creates a new LLM conversation and returns its ID."""

    return {
        "conversation_id": llm.start_conversation(obj.conversation_id)
    }


class CreateMessage(BaseModel):
    query: str

@router.post("/{conversation_id}")
def make_query(obj: CreateMessage, conversation_id: str):
    """Continues conversation and returns LLM response."""

    return {
        "response": llm.continue_conversation(conversation_id, obj.query)
    }