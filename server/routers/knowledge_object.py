from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from rid_lib import RID
from .. import graph, cache
from ..exceptions import ResourceNotFoundError

router = APIRouter(
    prefix="/object"
)

class CreateObject(BaseModel):
    rid: str
    data: Optional[dict] = None
    use_dereference: Optional[dict] = True
    overwrite: Optional[bool] = False

@router.post("")
def create_object(obj: CreateObject):
    rid = RID.from_string(obj.rid)
    graph.knowledge_object.create(rid)

    existing_data = cache.read(rid)
    if existing_data is None:
        if obj.data is not None:
            print("writing cache with provided data")
            cache.write(rid, obj.data)

        elif obj.use_dereference:
            print("writing cache with dereferenced data")
            data = rid.dereference()
            cache.write(rid, data)            
    
    elif obj.overwrite:
        if obj.data is not None:
            print("overwriting cache with provided data")
            cache.write(rid, obj.data)

        elif obj.use_dereference:
            print("overwriting cache with dereferenced data")
            data = rid.dereference()
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
    success = graph.knowledge_object.delete(rid)

    if not success:
        raise ResourceNotFoundError(rid)

    cache.delete(rid)


class ReadObjectLink(BaseModel):
    rid: str
    tag: str

@router.get("/link")
def read_object_link(obj: ReadObjectLink):
    rid = RID.from_string(obj.rid)
    target = graph.knowledge_object.read_link(rid, obj.tag)

    if not target:
        raise ResourceNotFoundError(rid, detail=f"{rid} has no link with tag '{obj.tag}'")

    members = graph.set.read(target)
    
    return {
        "rid": str(rid),
        "target_rid": str(target),
        "members": members
    }