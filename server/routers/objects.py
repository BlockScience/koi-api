from fastapi import APIRouter
from base64 import urlsafe_b64decode
from rid_lib import RID
from server.database import objects

router = APIRouter(
    prefix="/object"
)

@router.post("/{rid_str}")
def object_endpoint(rid_str, use_base64: bool = False):
    if use_base64:
        rid_bytes = rid_str.encode()
        rid_str = urlsafe_b64decode(rid_bytes).decode()

    print(rid_str)

    rid = RID.from_string(rid_str)
    objects.create(rid)
    return str(rid)