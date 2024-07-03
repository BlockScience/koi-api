from rid_lib.core import RID
from .base import InternalSpace

class InternalSet(InternalSpace):
    format = "set"

    def __init__(self, reference):
        self.reference = reference

    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self):
        return None
    
RID._add_type(InternalSet)