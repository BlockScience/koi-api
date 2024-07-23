from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib.core import DataObject
from rid_lib.spaces.koi import KoiLink, KoiSet

from koi.exceptions import ResourceNotFoundError
from koi.validators import RIDField
from koi import utils


router = APIRouter(tags=["Knowledge Object"])

class CreateObject(BaseModel):
    rid: RIDField
    data: dict | None = None
    use_dereference: bool = True
    overwrite: bool = False
    create_embedding: bool = True

@router.post("/object")
def create_object(knowledge_obj: CreateObject):
    """Observes RID object, optionally caching and embedding its data."""
    rid = knowledge_obj.rid
    rid.graph.create()
    data_object = DataObject(json_data=knowledge_obj.data)

    cached_object = rid.cache.read()
    if not cached_object or knowledge_obj.overwrite:
        if data_object:
            print("writing cache with provided data")
            cached_object = rid.cache.write(data_object)

        elif knowledge_obj.use_dereference:
            print("writing cache with dereferenced data")
            cached_object = rid.cache.write(from_dereference=True)

    if knowledge_obj.create_embedding:
        rid.vector.embed(from_cache=True)
    
    return cached_object.to_dict()


class CreateObjects(BaseModel):
    rids: dict[RIDField, dict | None]
    use_dereference: bool = True
    overwrite: bool = False
    create_embedding: bool = True

@router.post("/objects")
def create_objects(knowledge_objs: CreateObjects):
    """Observes multiple RID objects."""
    objects = {}
    for rid, data in knowledge_objs.rids.items():
        objects[str(rid)] = create_object(
            CreateObject(
                rid, 
                data, 
                knowledge_objs.use_dereference, 
                knowledge_objs.overwrite, 
                knowledge_objs.create_embedding
            )
        )

    return objects


class ReadObject(BaseModel):
    rid: RIDField

@router.get("/object")
def read_object(knowledge_obj: ReadObject):
    """Returns cached JSON data of RID object."""
    rid = knowledge_obj.rid
    return rid.cache.read().json_data

# @router.get("/{encoded_id:path}")
# def read_object_path(encoded_id: str):
#     return encoded_id

class DeleteObject(BaseModel):
    rid: RIDField

@router.delete("/object")
def delete_object(knowledge_obj: DeleteObject):
    """Deletes RID object from graph, cache, and vectorstore."""
    rid = knowledge_obj.rid
    success = rid.graph.delete()

    if not success:
        raise ResourceNotFoundError(rid)

    rid.cache.delete()
    rid.vector.delete()


class ReadObjectLink(BaseModel):
    rid: RIDField
    tag: str

@router.get("/object/link")
def read_object_link(obj_link: ReadObjectLink):
    """Returns RID of linked object, or a linked set's members."""
    rid = obj_link.rid
    target = rid.graph.read_link(obj_link.tag)

    if not target:
        raise ResourceNotFoundError(
            rid, detail=f"{rid} has no link with tag '{obj_link.tag}'")
    
    result = {
        "rid": rid,
        "target_rid": target
    }
    
    if isinstance(target, KoiSet):
        members = target.graph.read()
        result["members"] = members
    
    return utils.serialize_rids(result)


class MergeLinkedSet(BaseModel):
    rid: RIDField
    tag: str
    members: list[str] 

@router.post("/object/link")
def merge_linked_set(linked_set: MergeLinkedSet):
    """Adds members to linked set, which is created if it doesn't exist yet."""
    rid = linked_set.rid
    target = rid.graph.read_link(linked_set.tag)
    
    if not target:
        set_rid = KoiSet(nanoid.generate())
        members = set_rid.graph.create(linked_set.members)
        link_rid = KoiLink(rid, set_rid, linked_set.tag)
        link_rid.graph.create(
            source=rid,
            target=set_rid,
            tag=linked_set.tag
        )
    else:
        target.graph.update(add_members=linked_set.members)
        members = target.graph.read()

    return utils.serialize_rids({
        "rid": rid,
        "members": members
    })
        
