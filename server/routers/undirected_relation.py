from fastapi import APIRouter
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
    graph.undirected_relation.create(rid, rel.members)
    return str(rid)


class ReadRelation(BaseModel):
    rid: str

@router.get("")
def read_relation(rel: ReadRelation):
    rid = RID.from_string(rel.rid)
    return graph.undirected_relation.read(rid)


class UpdateRelation(BaseModel):
    rid: str
    add_members: Optional[List[str]] = None
    remove_members: Optional[List[str]] = None

@router.put("")
def update_relation(rel: UpdateRelation):
    rid = RID.from_string(rel.rid)
    graph.undirected_relation.update(rid, rel.add_members, rel.remove_members)