from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib import RID, DirectedRelation
from .. import graph
from .utils import check_existence

router = APIRouter(
    prefix="/link"
)

class CreateLink(BaseModel):
    sources: Optional[List[str]] = []
    targets: Optional[List[str]] = []

@router.post("")
def create_link(rel: CreateLink):
    rid = DirectedRelation(nanoid.generate())
    sources, targets = graph.directed_relation.create(rid, rel.sources, rel.targets)

    return {
        "rid": str(rid),
        "sources": sources,
        "targets": targets
    }


class ReadLink(BaseModel):
    rid: str

@router.get("")
def read_link(rel: ReadLink):
    rid = RID.from_string(rel.rid)
    check_existence(rid)

    sources, targets = graph.directed_relation.read(rid)

    return {
        "rid": str(rid),
        "sources": sources,
        "targets": targets
    }


class UpdateLink(BaseModel):
    rid: str
    add_sources: Optional[List[str]] = []
    remove_sources: Optional[List[str]] = []
    add_targets: Optional[List[str]] = []
    remove_targets: Optional[List[str]] = []

@router.put("")
def update_link(rel: UpdateLink):
    rid = RID.from_string(rel.rid)
    check_existence(rid)

    # remove duplicates
    add_sources = set(rel.add_sources)
    remove_sources = set(rel.remove_sources)
    add_targets = set(rel.add_targets)
    remove_targets = set(rel.remove_targets)

    # remove intersections
    source_intersection = add_sources & remove_sources
    add_sources -= source_intersection
    remove_sources -= source_intersection

    target_intersection = add_targets & remove_targets
    add_targets -= target_intersection
    remove_targets -= target_intersection

    graph.directed_relation.update(rid, list(add_sources), list(remove_sources), list(add_targets), list(remove_targets))
    updated_sources, updated_targets = graph.directed_relation.read(rid)

    return {
        "rid": str(rid),
        "sources": updated_sources, 
        "targets": updated_targets
    }


class DeleteLink(BaseModel):
    rid: str

@router.delete("")
def delete_link(rel: DeleteLink):
    rid = RID.from_string(rel.rid)
    check_existence(rid)
    graph.node.delete(rid)