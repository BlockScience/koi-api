"""Typing overrides for the koi library to add interface support."""

from dataclasses import dataclass

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


RIDTypes = (KoiLink | KoiSet | SlackChannel | SlackFile | SlackMessage |
            SlackMessage | SlackUser | SlackWorkspace | SubstackPublication | 
            SubstackPost)


class RID:
    space: str
    format: str
    
    def __init__(self) -> None:
        self.reference: str

        self.graph: GraphBaseInterface | GraphLinkInterface | GraphSetInterface
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


@dataclass
class DataObject:
    json_data: dict | None = None
    files: dict[str, bytes | str] | None = None

    def to_dict(self) -> dict: ...