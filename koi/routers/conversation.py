from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from koi import llm


router = APIRouter(
    prefix="/llm",
    tags=["Conversation"]
)

class CreateConversation(BaseModel):
    conversation_id: Optional[str] = None

@router.post("")
def create_conversation(obj: CreateConversation):
    conversation_id = llm.start_conversation(obj.conversation_id)

    return {
        "conversation_id": conversation_id
    }


class CreateMessage(BaseModel):
    query: str

@router.post("/{conversation_id}")
def make_query(obj: CreateMessage, conversation_id: str):
    return {
        "response": llm.continue_conversation(conversation_id, obj.query)
    }