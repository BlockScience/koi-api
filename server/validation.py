from rid_lib import RID
from rid_lib.exceptions import (
    InvalidFormatError,
    UndefinedMeansError
)
from typing import Annotated
from pydantic import AfterValidator, PlainSerializer
from pydantic_core import PydanticCustomError

def validator(rid):
    try:
        return RID.from_string(rid)
    except (InvalidFormatError, UndefinedMeansError) as error:
        # reraising RID processing errors so Pydantic can handle them through API response
        raise PydanticCustomError(type(error).__name__, str(error))

RIDField = Annotated[
    str,
    AfterValidator(validator),
    PlainSerializer(lambda rid: str(rid), return_type=str)
]