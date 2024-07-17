from rid_lib.core import RID
from rid_lib.types import InternalLink, InternalSet

from .graph import GraphKnowledgeObject, GraphSetObject, GraphLinkObject
from .cache import CacheableObject
from .vectorstore import EmbeddableObject


def purge(self: RID):
    self.graph.delete()
    self.cache.delete()

def extended_rid_post_init(self):
    if isinstance(self, InternalSet):
        self.graph = GraphSetObject(self)
    elif isinstance(self, InternalLink):
        self.graph = GraphLinkObject(self)
    else:
        self.graph = GraphKnowledgeObject(self)

    self.cache = CacheableObject(self)
    self.vector = EmbeddableObject(self)

    self.purge = purge

def patch_rid():
    RID.__post_init__ = extended_rid_post_init