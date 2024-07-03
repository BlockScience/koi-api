from typing import Optional, Union, List, Dict

from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib.spaces.internal import InternalLink, InternalSet

from koi import graph, cache, vectorstore
from koi.exceptions import ResourceNotFoundError
from koi.validators import RIDField
from koi.rid_extensions import ExtendedRID


router = APIRouter(tags=["Knowledge Object"])

class CreateObject(BaseModel):
    rid: RIDField
    data: Optional[dict] = None
    use_dereference: Optional[bool] = True
    overwrite: Optional[bool] = False
    create_embedding: Optional[bool] = True

@router.post("/object")
def create_object_endpoint(obj: CreateObject):
    create_object(**obj.model_dump())

def create_object(
    rid: ExtendedRID,
    data: Optional[dict] = None, 
    use_dereference: Optional[bool] = True, 
    overwrite: Optional[bool] = False, 
    create_embedding: Optional[bool] = True
):

    graph.knowledge_object.create(rid)
    
    cached_object = rid.cache.read()
    if cached_object.json_data is None:
        if data is not None:
            print("writing cache with provided data")
            cached_object = rid.cache.write(data)

        elif use_dereference:
            print("writing cache with dereferenced data")
            cached_object = rid.cache.write(from_dereference=True)
            
    elif overwrite:
        if data is not None:
            print("overwriting cache with provided data")
            cached_object = rid.cache.write(data)

        elif use_dereference:
            print("overwriting cache with dereferenced data")
            cached_object = rid.cache.write(from_dereference=True)

    if create_embedding and (cached_object.json_data is not None) and ("text" in cached_object.json_data):
        vectorstore.embed_objects([rid])
    
    return cached_object.json()


class CreateObjects(BaseModel):
    rids: Dict[RIDField, Union[dict, None]]
    use_dereference: Optional[bool] = True
    overwrite: Optional[bool] = False
    create_embedding: Optional[bool] = True

@router.post("/objects")
def create_objects_endpoint(payload: CreateObjects):
    objects = {}
    for rid, data in payload.rids.items():
        objects[str(rid)] = create_object(rid, data, payload.use_dereference, payload.overwrite, False)        

    if payload.create_embedding:
        embeddable_rids = [
            rid for rid in payload.rids.keys()
            if rid.format == "message"
        ]
        vectorstore.embed_objects(embeddable_rids)

    return objects


class ReadObject(BaseModel):
    rid: RIDField

@router.get("/object")
def read_object(obj: ReadObject):
    cached_object = cache.read(obj.rid)
    return cached_object.json()


# @router.get("/{encoded_id:path}")
# def read_object_path(encoded_id: str):
#     return encoded_id

class DeleteObject(BaseModel):
    rid: RIDField

@router.delete("/object")
def delete_object(obj: DeleteObject):
    success = graph.knowledge_object.delete(obj.rid)

    if not success:
        raise ResourceNotFoundError(obj.rid)

    cache.delete(obj.rid)


class ReadObjectLink(BaseModel):
    rid: RIDField
    tag: str

@router.get("/object/link")
def read_object_link(obj: ReadObjectLink):
    target = graph.knowledge_object.read_link(obj.rid, obj.tag)

    if not target:
        raise ResourceNotFoundError(obj.rid, detail=f"{obj.rid} has no link with tag '{obj.tag}'")
    
    result = {
        "rid": str(obj.rid),
        "target_rid": str(target)
    }
    
    if isinstance(target, InternalSet):
        members = graph.set.read(target)
        result["members"] = members
    
    return result


class MergeLinkedSet(BaseModel):
    rid: RIDField
    tag: str
    members: List[str] 

@router.post("/object/link")
def merge_linked_set(obj: MergeLinkedSet):
    target = graph.knowledge_object.read_link(obj.rid, obj.tag)
    
    if not target:
        set_rid = InternalSet(nanoid.generate())
        members = graph.set.create(set_rid, obj.members)
        link_rid = InternalLink(obj.rid, set_rid, obj.tag)
        graph.link.create(link_rid, obj.rid, set_rid, obj.tag)
    else:
        members = graph.set.update(target, add_members=obj.members)

    return {
        "rid": obj.rid,
        "members": members
    }
        
