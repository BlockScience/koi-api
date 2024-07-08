from rid_lib.core import RID
from rid_lib.types import InternalLink, InternalSet

from .cache import CacheableObject
from .graph import GraphKnowledgeObject, GraphSetObject, GraphLinkObject


def extended_rid_post_init(self):
    self.cache = CacheableObject(self)

    if isinstance(self, InternalSet):
        self.graph = GraphSetObject(self)
    elif isinstance(self, InternalLink):
        self.graph = GraphLinkObject(self)
    else:
        self.graph = GraphKnowledgeObject(self)

def patch_rid():
    RID.__post_init__ = extended_rid_post_init