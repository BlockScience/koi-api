from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from rid_lib import RID, Set
from .. import graph
from .utils import check_existence
import nanoid

router = APIRouter(
    prefix="/set"
)

class CreateSet(BaseModel):
    members: Optional[List[str]] = []

@router.post("")
def create_set(rel: CreateSet):
    rid = Set(nanoid.generate())
    members = graph.set.create(rid, rel.members)

    return {
        "rid": str(rid),
        "members": members
    }


class ReadSet(BaseModel):
    rid: str

@router.get("")
def read_set(rel: ReadSet):
    rid = RID.from_string(rel.rid)
    check_existence(rid)

    members = graph.set.read(rid)

    print(str(members))
    return {
        "rid": str(rid),
        "members": members
    }


class UpdateSet(BaseModel):
    rid: str
    add_members: Optional[List[str]] = []
    remove_members: Optional[List[str]] = []

@router.put("")
def update_set(rel: UpdateSet):
    rid = RID.from_string(rel.rid)
    check_existence(rid)

    # remove duplicates
    add_members = set(rel.add_members)
    remove_members = set(rel.remove_members)

    # remove intersecting rids (would be added and removed in same operation)
    intersection = add_members & remove_members
    add_members -= intersection
    remove_members -= intersection

    graph.set.update(rid, list(add_members), list(remove_members))
    updated_members = graph.set.read(rid)

    return {
        "rid": str(rid),
        "members": updated_members
    }


class DeleteSet(BaseModel):
    rid: str

@router.delete("")
def delete_set(rel: DeleteSet):
    rid = RID.from_string(rel.rid)
    check_existence(rid)
    graph.node.delete(rid)