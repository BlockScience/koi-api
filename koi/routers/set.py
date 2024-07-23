from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib.spaces.koi import KoiSet

from koi.exceptions import ResourceNotFoundError
from koi.validators import RIDField
from koi import utils


router = APIRouter(
    prefix="/set",
    tags=["Set"]
)

class CreateSet(BaseModel):
    members: list[str] = []

@router.post("")
def create_set(set_obj: CreateSet):
    """Creates new set containing provided RIDs."""
    rid = KoiSet(nanoid.generate())
    members = rid.graph.create(rid, set_obj.members)

    return utils.serialize_rids({
        "rid": rid,
        "members": members
    })


class ReadSet(BaseModel):
    rid: RIDField

@router.get("")
def read_set(set_obj: ReadSet):
    """Returns set RID and member RIDs."""
    rid = set_obj.rid
    members = rid.graph.read()

    if members is None:
        raise ResourceNotFoundError(rid)

    return utils.serialize_rids({
        "rid": rid,
        "members": members
    })


class UpdateSet(BaseModel):
    rid: RIDField
    add_members: list[str] = []
    remove_members: list[str] = []

@router.put("")
def update_set(set_obj: UpdateSet):
    """Updates set by adding or removing members."""
    rid = set_obj.rid

    # remove duplicates
    add_members = set(set_obj.add_members)
    remove_members = set(set_obj.remove_members)

    # remove intersecting rids (would be added and removed in same operation)
    intersection = add_members & remove_members
    add_members -= intersection
    remove_members -= intersection

    success = rid.graph.update(
        add_members=list(add_members),
        remove_members=list(remove_members)
    )
    if not success:
        raise ResourceNotFoundError(rid)

    return utils.serialize_rids({
        "rid": rid,
        "success": success
    })


class DeleteSet(BaseModel):
    rid: RIDField

@router.delete("")
def delete_set(set_obj: DeleteSet):
    """Deletes set object."""
    rid = set_obj.rid
    success = rid.graph.delete()

    if not success:
        raise ResourceNotFoundError(rid)