from fastapi import APIRouter
from pydantic import BaseModel
from .. import llm

router = APIRouter(
    prefix="/llm"
)

@router.post("")
def create_conversation():
    conversation_id = llm.start_conversation()

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