from typing import Union, Optional

from rid_lib.types import (
    InternalLink,
    InternalSet,
    SlackChannel,
    SlackFile,
    SlackMessage,
    SlackUser,
    SlackWorkspace,
    SubstackPublication,
    SubstackPost
)

from koi.cache import CacheableObject
from koi.graph import GraphKnowledgeObject, GraphLinkObject, GraphSetObject

RIDTypes = InternalLink | InternalSet | SlackChannel | SlackFile | SlackMessage | SlackMessage | SlackUser | SlackWorkspace | SubstackPublication | SubstackPost

class RID:
    space: str
    format: str
    
    def __init__(self) -> None:
        self.reference: str

        self.cache: CacheableObject
        self.graph: Union[GraphKnowledgeObject, GraphLinkObject, GraphSetObject]

    def __post_init__(self) -> None: ...

    @staticmethod
    def from_string(rid_str: str) -> RIDTypes: ...

    @property
    def means(self) -> str: ...

    @property
    def params(self) -> dict: ...

    def dereference(self) -> DataObject: ...


class DataObject:
    def __init__(self, json_data: Optional[dict] = None, files: Optional[dict[str, bytes | str]] = None) -> None:
        self.json_data: Optional[dict]
        self.files: Optional[dict[str, bytes | str]]

    @property
    def empty(self) -> bool: ...

    @property
    def merged_json(self) -> dict: ...