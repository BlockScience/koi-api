from fastapi import APIRouter
from pydantic import BaseModel
from rid_lib import RID
from server.database import objects

router = APIRouter(
    prefix="/object"
)

class Object(BaseModel):
    rid: str

@router.post("")
def create_object(obj: Object):
    rid = RID.from_string(obj.rid)
    objects.create(rid)
    return str(rid)

@router.delete("")
def delete_object(obj: Object):
    rid = RID.from_string(obj.rid)
    objects.delete(rid)
    return str(rid)