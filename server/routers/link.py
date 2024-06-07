from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
import nanoid
from rid_lib import RID, Link
from .. import graph
from .utils import check_existence

router = APIRouter(
    prefix="/link"
)

class CreateLink(BaseModel):
    tag: str
    source: str
    target: str

@router.post("")
def create_link(rel: CreateLink):
    reference = rel.tag + "/" + nanoid.generate()
    rid = Link(reference)
    graph.link.create(rid, rel.tag, rel.source, rel.target)

    return {
        "rid": str(rid)
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