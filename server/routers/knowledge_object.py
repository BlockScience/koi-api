from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from rid_lib import RID
from server import cache, graph

router = APIRouter(
    prefix="/object"
)

class Object(BaseModel):
    rid: str
    data: Optional[dict] = None

@router.post("")
def create_object(obj: Object):
    rid = RID.from_string(obj.rid)
    graph.knowledge_object.create(rid)

    # experimental, defaults to internal dereference if no data provided
    if obj.data:
        data = obj.data
    else:
        data = rid.dereference()

    cache.write(rid, data)
    return str(rid)

@router.get("")
def read_object(obj: Object):
    rid = RID.from_string(obj.rid)
    data, hash = cache.read(rid)
    return {
        "rid": str(rid),
        "data": data,
        "hash": hash
    }

@router.delete("")
def delete_object(obj: Object):
    rid = RID.from_string(obj.rid)
    graph.node.delete(rid)
    cache.delete(rid)
    return str(rid)