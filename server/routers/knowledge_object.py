from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from rid_lib import RID
from server import graph, cache

router = APIRouter(
    prefix="/object"
)

class CreateObject(BaseModel):
    rid: str
    data: Optional[dict] = None

@router.post("")
def create_object(obj: CreateObject):
    rid = RID.from_string(obj.rid)
    graph.knowledge_object.create(rid)

    # experimental, defaults to internal dereference if no data provided
    if obj.data:
        data = obj.data
    else:
        data = rid.dereference()

    if data:
        cache.write(rid, data)
    
    return {
        "rid": str(rid)
    }


class ReadObject(BaseModel):
    rid: str

@router.get("")
def read_object(obj: ReadObject):
    rid = RID.from_string(obj.rid)
    data, hash = cache.read(rid)
    return {
        "rid": str(rid),
        "data": data,
        "hash": hash
    }

@router.delete("")
def delete_object(obj: ReadObject):
    rid = RID.from_string(obj.rid)
    graph.node.delete(rid)
    cache.delete(rid)


class ReadObjectLink(BaseModel):
    rid: str
    tag: str

@router.get("/link")
def read_object_link(obj: ReadObjectLink):
    rid = RID.from_string(obj.rid)
    target = graph.knowledge_object.read_link(rid, obj.tag)

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RID '{str(rid)}' has no link with tag '{obj.tag}'"
        )

    contains = graph.set.read(target)
    
    return {
        "rid": str(rid),
        "target_rid": str(target),
        "contains": contains
    }