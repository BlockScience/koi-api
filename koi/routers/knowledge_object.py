from typing import Optional, Union

from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib.core import DataObject
from rid_lib.spaces.internal import InternalLink, InternalSet

from koi import vectorstore
from koi.exceptions import ResourceNotFoundError
from koi.validators import RIDField


router = APIRouter(tags=["Knowledge Object"])

class CreateObject(BaseModel):
    rid: RIDField
    data: Optional[dict] = None
    use_dereference: Optional[bool] = True
    overwrite: Optional[bool] = False
    create_embedding: Optional[bool] = True

@router.post("/object")
def create_object(knowledge_obj: CreateObject):
    rid = knowledge_obj.rid
    rid.graph.create()
    data_object = DataObject(json_data=knowledge_obj.data)

    cached_object = rid.cache.read()
    if cached_object.empty or knowledge_obj.overwrite:
        if not data_object.empty:
            print("writing cache with provided data")
            cached_object = rid.cache.write(data_object)

        elif knowledge_obj.use_dereference:
            print("writing cache with dereferenced data")
            cached_object = rid.cache.write(from_dereference=True)

    if knowledge_obj.create_embedding:
        vectorstore.embed_objects([rid])
    
    return cached_object.json()


class CreateObjects(BaseModel):
    rids: dict[RIDField, Union[dict, None]]
    use_dereference: Optional[bool] = True
    overwrite: Optional[bool] = False
    create_embedding: Optional[bool] = True

@router.post("/objects")
def create_objects(knowledge_objs: CreateObjects):
    objects = {}
    for rid, data in knowledge_objs.rids.items():
        objects[str(rid)] = create_object(CreateObject(
            rid, data, knowledge_objs.use_dereference, knowledge_objs.overwrite, create_embedding=False
        ))

    if knowledge_objs.create_embedding:
        vectorstore.embed_objects(knowledge_objs.rids.keys())

    return objects


class ReadObject(BaseModel):
    rid: RIDField

@router.get("/object")
def read_object(knowledge_obj: ReadObject):
    rid = knowledge_obj.rid
    return rid.cache.read().json_data

# @router.get("/{encoded_id:path}")
# def read_object_path(encoded_id: str):
#     return encoded_id

class DeleteObject(BaseModel):
    rid: RIDField

@router.delete("/object")
def delete_object(knowledge_obj: DeleteObject):
    rid = knowledge_obj.rid
    success = rid.graph.delete()

    if not success:
        raise ResourceNotFoundError(rid)

    rid.cache.delete()


class ReadObjectLink(BaseModel):
    rid: RIDField
    tag: str

@router.get("/object/link")
def read_object_link(obj_link: ReadObjectLink):
    rid = obj_link.rid
    target = rid.graph.read_link(obj_link.tag)

    if not target:
        raise ResourceNotFoundError(rid, detail=f"{rid} has no link with tag '{obj_link.tag}'")
    
    result = {
        "rid": str(rid),
        "target_rid": str(target)
    }
    
    if isinstance(target, InternalSet):
        members = target.graph.read()
        result["members"] = members
    
    return result


class MergeLinkedSet(BaseModel):
    rid: RIDField
    tag: str
    members: list[str] 

@router.post("/object/link")
def merge_linked_set(linked_set: MergeLinkedSet):
    print(linked_set.model_dump())

    rid = linked_set.rid
    target = rid.graph.read_link(linked_set.tag)
    
    if not target:
        set_rid = InternalSet(nanoid.generate())
        members = set_rid.graph.create(linked_set.members)
        link_rid = InternalLink(rid, set_rid, linked_set.tag)
        link_rid.graph.create(
            source=rid,
            target=set_rid,
            tag=linked_set.tag
        )
    else:
        members, _ = target.graph.update(add_members=linked_set.members)

    print(rid, members)

    return {
        "rid": str(rid),
        "members": members
    }
        
