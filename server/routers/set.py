from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from rid_lib import RID, Set
from .. import graph
import nanoid
from ..exceptions import ResourceNotFoundError

router = APIRouter(
    prefix="/set"
)

    
class CreateSet(BaseModel):
    members: Optional[List[str]] = []

@router.post("")
def create_set(obj: CreateSet):
    rid = Set(nanoid.generate())
    members = graph.set.create(rid, obj.members)

    return {
        "rid": str(rid),
        "members": members
    }


class ReadSet(BaseModel):
    rid: str

@router.get("")
def read_set(obj: ReadSet):
    rid = RID.from_string(obj.rid)
    members = graph.set.read(rid)

    if members is None:
        raise ResourceNotFoundError(rid)

    return {
        "rid": str(rid),
        "members": members
    }


class UpdateSet(BaseModel):
    rid: str
    add_members: Optional[List[str]] = []
    remove_members: Optional[List[str]] = []

@router.put("")
def update_set(obj: UpdateSet):
    rid = RID.from_string(obj.rid)

    # remove duplicates
    add_members = set(obj.add_members)
    remove_members = set(obj.remove_members)

    # remove intersecting rids (would be added and removed in same operation)
    intersection = add_members & remove_members
    add_members -= intersection
    remove_members -= intersection

    result = graph.set.update(rid, list(add_members), list(remove_members))

    if result is None:
        raise ResourceNotFoundError(rid)

    added_members, removed_members = result

    return {
        "rid": str(rid),
        "added_members": added_members,
        "removed_members": removed_members
    }


class DeleteSet(BaseModel):
    rid: str

@router.delete("")
def delete_set(obj: DeleteSet):
    rid = RID.from_string(obj.rid)
    success = graph.set.delete(rid)

    if not success:
        raise ResourceNotFoundError(rid)