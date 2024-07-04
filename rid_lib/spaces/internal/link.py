import json
import hashlib
from typing import Union

from rid_lib.core import RID, DataObject
from .base import InternalSpace

class InternalLink(InternalSpace):
    format = "link"

    def __init__(self, source: Union[RID, str] = None, target: Union[RID, str] = None, tag: str = None, reference: str = None):

        if reference is not None:
            self.reference = reference

        elif source is not None and target is not None and tag is not None:

            link_json = {
                "source": str(source),
                "target": str(target)
            }
            json_string = json.dumps(link_json)
            json_bytes = json_string.encode()
            hash = hashlib.sha256()
            hash.update(json_bytes)
            link_hash = hash.hexdigest()

            self.reference = f"{tag}+{link_hash}"
        
        else:
            raise TypeError("InternalLink must be instantiated with a reference or a source, target, and tag")

    @classmethod
    def from_reference(cls, reference):
        return cls(reference=reference)
    
    def dereference(self):
        return DataObject()

RID._add_type(InternalLink)