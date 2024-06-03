from fastapi import status, HTTPException
from .. import graph
from rid_lib import RID

def check_existence(rid: RID):
    if not graph.node.exists(rid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"RID '{str(rid)}' not found"
        )