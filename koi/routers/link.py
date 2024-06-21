from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from rid_lib.spaces.internal import InternalLink

from koi import graph
from koi.exceptions import ResourceNotFoundError
from koi.validators import RIDField


router = APIRouter(
    prefix="/link"
)

class CreateLink(BaseModel):
    tag: str
    source: str
    target: str

@router.post("")
def create_link(obj: CreateLink):
    if obj.source == obj.target:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Self links are not allowed, source and target must be different"
        )

    rid = InternalLink(obj.source, obj.target, obj.tag)
    success = graph.link.create(rid, obj.source, obj.target, obj.tag)

    if not success:
        raise ResourceNotFoundError(rid, detail="Source and/or target not found")

    return {
        "rid": str(rid),
        "source": obj.source,
        "target": obj.target
    }


class ReadLink(BaseModel):
    rid: RIDField

@router.get("")
def read_link(obj: ReadLink):
    result = graph.link.read(obj.rid)

    if result is None:
        raise ResourceNotFoundError(obj.rid)

    source, target = result

    return {
        "rid": str(obj.rid),
        "source": source,
        "target": target
    }

class DeleteLink(BaseModel):
    rid: RIDField

@router.delete("")
def delete_link(obj: DeleteLink):
    success = graph.link.delete(obj.rid)

    if not success:
        raise ResourceNotFoundError(obj.rid)
