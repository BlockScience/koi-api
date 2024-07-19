from rid_lib.core import RID
from rid_lib.types import InternalLink, InternalSet

from .graph import GraphBaseInterface, GraphSetInterface, GraphLinkInterface
from .cache import CacheInterface
from .vectorstore import VectorInterface


def purge(self: RID):
    self.graph.delete()
    self.cache.delete()
    self.vector.delete()

def extended_rid_post_init(self):
    if isinstance(self, InternalSet):
        self.graph = GraphSetInterface(self)
    elif isinstance(self, InternalLink):
        self.graph = GraphLinkInterface(self)
    else:
        self.graph = GraphBaseInterface(self)

    self.cache = CacheInterface(self)
    self.vector = VectorInterface(self)

def patch_rid():
    RID.__post_init__ = extended_rid_post_init
    RID.purge = purge