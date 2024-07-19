from rid_lib.core import RID, DataObject
from .base import KoiSpace

class KoiSet(KoiSpace):
    format = "set"

    def __init__(self, reference):
        self.reference = reference

    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self):
        return DataObject()
    
RID._add_type(KoiSet)