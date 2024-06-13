from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from rid_lib import RID
from .. import graph, cache
from ..exceptions import ResourceNotFoundError
from ..validation import RIDField

router = APIRouter(
    prefix="/object"
)

class CreateObject(BaseModel):
    rid: RIDField
    data: Optional[dict] = None
    use_dereference: Optional[dict] = True
    overwrite: Optional[bool] = False

@router.post("")
def create_object(obj: CreateObject):
    # rid = RID.from_string(obj.rid)
    graph.knowledge_object.create(obj.rid)

    existing_data = cache.read(obj.rid)
    if existing_data is None:
        if obj.data is not None:
            print("writing cache with provided data")
            cache.write(obj.rid, obj.data)

        elif obj.use_dereference:
            print("writing cache with dereferenced data")
            data = obj.rid.dereference()
            cache.write(obj.rid, data)            
    
    elif obj.overwrite:
        if obj.data is not None:
            print("overwriting cache with provided data")
            cache.write(obj.rid, obj.data)

        elif obj.use_dereference:
            print("overwriting cache with dereferenced data")
            data = obj.rid.dereference()
            cache.write(obj.rid, data)
    
    return {
        "rid": str(obj.rid)
    }


class ReadObject(BaseModel):
    rid: RIDField

@router.get("")
def read_object(obj: ReadObject):
    data, hash = cache.read(obj.rid)
    return {
        "rid": str(obj.rid),
        "data": data,
        "hash": hash
    }


class DeleteObject(BaseModel):
    rid: RIDField

@router.delete("")
def delete_object(obj: DeleteObject):
    success = graph.knowledge_object.delete(obj.rid)

    if not success:
        raise ResourceNotFoundError(obj.rid)

    cache.delete(obj.rid)


class ReadObjectLink(BaseModel):
    rid: RIDField
    tag: str

@router.get("/link")
def read_object_link(obj: ReadObjectLink):
    target = graph.knowledge_object.read_link(obj.rid, obj.tag)

    if not target:
        raise ResourceNotFoundError(obj.rid, detail=f"{obj.rid} has no link with tag '{obj.tag}'")

    members = graph.set.read(target)
    
    return {
        "rid": str(obj.rid),
        "target_rid": str(target),
        "members": members
    }