from typing import Annotated

from pydantic import AfterValidator, PlainSerializer
from pydantic_core import PydanticCustomError
from rid_lib import RID
from rid_lib.exceptions import RidException

from .rid_extensions import ExtendedRID


def rid_validator(rid):
    try:
        return ExtendedRID(RID.from_string(rid))
    except RidException as error:
        # reraising RID processing errors so Pydantic can handle them through API response
        raise PydanticCustomError(type(error).__name__, str(error))

RIDField = Annotated[
    str,
    AfterValidator(rid_validator),
    PlainSerializer(lambda rid: str(rid), return_type=str)
]