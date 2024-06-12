from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from rid_lib import RID, Link
from .. import graph
from ..exceptions import ResourceNotFoundError

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

    params = obj.model_dump()
    rid = Link.from_params(**params)
    success = graph.link.create(rid, **params)

    if not success:
        raise ResourceNotFoundError(rid, detail="Source and/or target not found")

    return {
        "rid": str(rid),
        "source": obj.source,
        "target": obj.target
    }


class ReadLink(BaseModel):
    rid: str

@router.get("")
def read_link(obj: ReadLink):
    rid = RID.from_string(obj.rid)
    result = graph.link.read(rid)

    if result is None:
        raise ResourceNotFoundError(rid)

    source, target = result

    return {
        "rid": str(rid),
        "source": source,
        "target": target
    }

class DeleteLink(BaseModel):
    rid: str

@router.delete("")
def delete_link(obj: DeleteLink):
    rid = RID.from_string(obj.rid)
    success = graph.link.delete(rid)

    if not success:
        raise ResourceNotFoundError(rid)
