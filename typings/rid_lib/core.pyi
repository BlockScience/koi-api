from typing import Union, Optional

from rid_lib.types import (
    KoiLink,
    KoiSet,
    SlackChannel,
    SlackFile,
    SlackMessage,
    SlackUser,
    SlackWorkspace,
    SubstackPublication,
    SubstackPost
)

from koi.graph import GraphBaseInterface, GraphLinkInterface, GraphSetInterface
from koi.cache import CacheInterface
from koi.vectorstore import VectorInterface


RIDTypes = KoiLink | KoiSet | SlackChannel | SlackFile | SlackMessage | SlackMessage | SlackUser | SlackWorkspace | SubstackPublication | SubstackPost


class RID:
    space: str
    format: str
    
    def __init__(self) -> None:
        self.reference: str

        self.graph: Union[GraphBaseInterface, GraphLinkInterface, GraphSetInterface]
        self.cache: CacheInterface
        self.vector: VectorInterface

    def __post_init__(self) -> None: ...

    @staticmethod
    def _add_type(Type: RID) -> None: ...

    @staticmethod
    def from_string(rid_str: str) -> RIDTypes: ...

    @property
    def means(self) -> str: ...

    @property
    def params(self) -> dict: ...

    def dereference(self) -> DataObject: ...

    def purge(self) -> None: ...


class DataObject:
    def __init__(self, json_data: Optional[dict] = None, files: Optional[dict[str, bytes | str]] = None) -> None:
        self.json_data: Optional[dict]
        self.files: Optional[dict[str, bytes | str]]

    @property
    def empty(self) -> bool: ...

    @property
    def merged_json(self) -> dict: ...