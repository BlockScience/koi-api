from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from rid_lib.spaces.koi import KoiLink

from koi.exceptions import ResourceNotFoundError
from koi.validators import RIDField


router = APIRouter(
    prefix="/link",
    tags=["Link"]
)

class CreateLink(BaseModel):
    tag: str
    source: RIDField
    target: RIDField

@router.post("")
def create_link(link_obj: CreateLink):
    if link_obj.source == link_obj.target:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Self links are not allowed, source and target must be different"
        )

    rid = KoiLink(link_obj.source, link_obj.target, link_obj.tag)
    success = rid.graph.create(
        source=link_obj.source,
        target=link_obj.target,
        tag=link_obj.tag
    )

    if not success:
        raise ResourceNotFoundError(rid, detail="Source and/or target not found")

    return {
        "rid": str(rid),
        "source": str(link_obj.source),
        "target": str(link_obj.target)
    }


class ReadLink(BaseModel):
    rid: RIDField

@router.get("")
def read_link(link_obj: ReadLink):
    rid = link_obj.rid
    result = rid.graph.read()

    if result is None:
        raise ResourceNotFoundError(rid)

    source, target = result

    return {
        "rid": str(rid),
        "source": source,
        "target": target
    }

class DeleteLink(BaseModel):
    rid: RIDField

@router.delete("")
def delete_link(link_obj: DeleteLink):
    rid = link_obj.rid
    success = rid.graph.delete()

    if not success:
        raise ResourceNotFoundError(rid)
