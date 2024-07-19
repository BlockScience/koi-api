from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib.spaces.koi import KoiSet

from koi.exceptions import ResourceNotFoundError
from koi.validators import RIDField


router = APIRouter(
    prefix="/set",
    tags=["Set"]
)

class CreateSet(BaseModel):
    members: Optional[List[str]] = []

@router.post("")
def create_set(set_obj: CreateSet):
    rid = KoiSet(nanoid.generate())
    members = rid.graph.create(rid, set_obj.members)

    return {
        "rid": str(rid),
        "members": members
    }


class ReadSet(BaseModel):
    rid: RIDField

@router.get("")
def read_set(set_obj: ReadSet):
    rid = set_obj.rid
    members = rid.graph.read()

    if members is None:
        raise ResourceNotFoundError(rid)

    return {
        "rid": str(rid),
        "members": members
    }


class UpdateSet(BaseModel):
    rid: RIDField
    add_members: Optional[List[str]] = []
    remove_members: Optional[List[str]] = []

@router.put("")
def update_set(set_obj: UpdateSet):
    rid = set_obj.rid

    # remove duplicates
    add_members = set(set_obj.add_members)
    remove_members = set(set_obj.remove_members)

    # remove intersecting rids (would be added and removed in same operation)
    intersection = add_members & remove_members
    add_members -= intersection
    remove_members -= intersection

    result = rid.graph.update(
        add_members=list(add_members),
        remove_members=list(remove_members)
    )

    if result is None:
        raise ResourceNotFoundError(rid)

    added_members, removed_members = result

    return {
        "rid": str(rid),
        "added_members": added_members,
        "removed_members": removed_members
    }


class DeleteSet(BaseModel):
    rid: RIDField

@router.delete("")
def delete_set(set_obj: DeleteSet):
    rid = set_obj.rid
    success = rid.graph.delete()

    if not success:
        raise ResourceNotFoundError(rid)