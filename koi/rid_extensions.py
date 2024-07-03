from rid_lib.core import RID, RIDWrapper
from .cache import CacheableObject

class ExtendedRID(RIDWrapper):
    def __init__(self, rid: RID):
        super().__init__(rid)
        
        self.cache = CacheableObject(self)