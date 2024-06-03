from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from rid_lib import RID, UndirectedRelation
from server import graph
import nanoid

router = APIRouter(
    prefix="/relation"
)

class CreateRelation(BaseModel):
    members: Optional[List[str]] = []

@router.post("")
def create_relation(rel: CreateRelation):
    rid = UndirectedRelation(nanoid.generate())
    members = graph.undirected_relation.create(rid, rel.members)

    return {
        "rid": str(rid),
        "members": members
    }


def check_existence(rid: RID):
    if not graph.undirected_relation.exists(rid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RID '{str(rid)}' not found"
        )

class ReadRelation(BaseModel):
    rid: str

@router.get("")
def read_relation(rel: ReadRelation):
    rid = RID.from_string(rel.rid)
    check_existence(rid)

    members = graph.undirected_relation.read(rid)

    print(str(members))
    return {
        "rid": str(rid),
        "members": members
    }


class UpdateRelation(BaseModel):
    rid: str
    add_members: Optional[List[str]] = []
    remove_members: Optional[List[str]] = []

@router.put("")
def update_relation(rel: UpdateRelation):
    rid = RID.from_string(rel.rid)
    check_existence(rid)

    # remove duplicates
    add_members = set(rel.add_members)
    remove_members = set(rel.remove_members)

    # remove intersecting rids (would be added and removed in same operation)
    intersection = add_members & remove_members
    add_members -= intersection
    remove_members -= intersection

    graph.undirected_relation.update(rid, list(add_members), list(remove_members))
    updated_members = graph.undirected_relation.read(rid)

    return {
        "rid": str(rid),
        "members": updated_members
    }


class DeleteRelation(BaseModel):
    rid: str

@router.delete("")
def delete_relation(rel: DeleteRelation):
    rid = RID.from_string(rel.rid)
    check_existence(rid)
    graph.undirected_relation.delete(rid)