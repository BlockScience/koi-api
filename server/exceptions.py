from rid_lib import RID
from fastapi import HTTPException, status

class ResourceNotFoundError(HTTPException):
    def __init__(self, rid: RID, detail=None):
        if detail is None:
            detail = f"{rid} not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )