from pydantic import PlainSerializer, BeforeValidator, WithJsonSchema
from pydantic_core import PydanticCustomError
from rid_lib.core import RID
from rid_lib.exceptions import RidException

from dataclasses import dataclass
from typing import Any, Type
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler

@dataclass
class RIDField(RID):
    """Custom Pydantic field for RID objects."""
    @classmethod
    def __get_pydantic_core_schema__(
        cls, 
        source: Type[Any], 
        handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        
        assert source is RIDField
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )
    
    @staticmethod
    def _validate(value: str):
        """Returns RID object from input string, reraises RID errors."""
        try:
            return RID.from_string(value)
        except RidException as error:
            raise PydanticCustomError(type(error).__name__, str(error))
    
    @staticmethod
    def _serialize(value: RID):
        return str(value)



# def validate_rid(rid):
#     try:
#         return RID.from_string(rid)
#     except RidException as error:
#         # reraising RID processing errors so Pydantic can handle them through API response
#         raise PydanticCustomError(type(error).__name__, str(error)) # type: ignore

# rid_field_annotations = [
#     BeforeValidator(validate_rid),
#     PlainSerializer(lambda rid: str(rid), return_type=str),
#     WithJsonSchema({
#         "type": "str", 
#         "examples": [
#             "substack.post:metagov/metagov-project-spotlight-koi-pond",
#             "slack.message:TMQ3PKXT9/C06DMGNV7E0/1718870811.756359"
#         ]
#     })
# ]