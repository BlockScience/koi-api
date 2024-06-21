from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib.spaces.internal import InternalSet

from koi import graph
from koi.exceptions import ResourceNotFoundError
from koi.validators import RIDField


router = APIRouter(
    prefix="/set"
)

    
class CreateSet(BaseModel):
    members: Optional[List[str]] = []

@router.post("")
def create_set(obj: CreateSet):
    rid = InternalSet(nanoid.generate())
    members = graph.set.create(rid, obj.members)

    return {
        "rid": str(rid),
        "members": members
    }


class ReadSet(BaseModel):
    rid: RIDField

@router.get("")
def read_set(obj: ReadSet):
    members = graph.set.read(obj.rid)

    if members is None:
        raise ResourceNotFoundError(obj.rid)

    return {
        "rid": str(obj.rid),
        "members": members
    }


class UpdateSet(BaseModel):
    rid: RIDField
    add_members: Optional[List[str]] = []
    remove_members: Optional[List[str]] = []

@router.put("")
def update_set(obj: UpdateSet):
    # remove duplicates
    add_members = set(obj.add_members)
    remove_members = set(obj.remove_members)

    # remove intersecting rids (would be added and removed in same operation)
    intersection = add_members & remove_members
    add_members -= intersection
    remove_members -= intersection

    result = graph.set.update(obj.rid, list(add_members), list(remove_members))

    if result is None:
        raise ResourceNotFoundError(obj.rid)

    added_members, removed_members = result

    return {
        "rid": str(obj.rid),
        "added_members": added_members,
        "removed_members": removed_members
    }


class DeleteSet(BaseModel):
    rid: RIDField

@router.delete("")
def delete_set(obj: DeleteSet):
    success = graph.set.delete(obj.rid)

    if not success:
        raise ResourceNotFoundError(obj.rid)