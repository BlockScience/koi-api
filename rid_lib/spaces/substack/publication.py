from rid_lib.core import RID, DataObject
from .base import SubstackSpace


class SubstackPublication(SubstackSpace):
    format = "publication"

    def __init__(self, subdomain: str):
        self.subdomain = subdomain
        self.reference = subdomain

    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
    
    def dereference(self):
        return DataObject()
    
RID._add_type(SubstackPublication)