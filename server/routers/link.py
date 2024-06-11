from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib import RID, Link
from .. import graph

router = APIRouter(
    prefix="/link"
)

class CreateLink(BaseModel):
    tag: str
    source: str
    target: str

@router.post("")
def create_link(rel: CreateLink):
    rid = Link.from_params(rel.tag, rel.source, rel.target)
    graph.link.create(rid, rel.tag, rel.source, rel.target)

    return {
        "rid": str(rid),
        "source": rel.source,
        "target": rel.target
    }


class ReadLink(BaseModel):
    rid: str

@router.get("")
def read_link(rel: ReadLink):
    rid = RID.from_string(rel.rid)
    source, target = graph.link.read(rid)

    return {
        "rid": str(rid),
        "source": source,
        "target": target
    }

class DeleteLink(BaseModel):
    rid: str

@router.delete("")
def delete_link(rel: DeleteLink):
    rid = RID.from_string(rel.rid)
    graph.link.delete(rid)