import json
import hashlib

from rid_lib.core import RID, DataObject
from .base import KoiSpace

class KoiLink(KoiSpace):
    format = "link"

    def __init__(
        self, 
        source: RID | str | None = None,
        target: RID | str | None = None,
        tag: str = None, 
        reference: str = None
    ):
        if reference:
            self.reference = reference

        elif source and target and tag:

            link_json = {
                "source": str(source),
                "target": str(target)
            }
            json_string = json.dumps(link_json)
            json_bytes = json_string.encode()
            hash = hashlib.sha256()
            hash.update(json_bytes)
            link_hash = hash.hexdigest()
            
            self.source = source
            self.target = target
            self.tag = tag

            self.reference = f"{tag}+{link_hash}"
        
        else:
            raise TypeError(
                "InternalLink must be instantiated with a reference or a "
                "source, target, and tag")

    @classmethod
    def from_reference(cls, reference):
        return cls(reference=reference)
    
    def dereference(self):
        return DataObject()

RID._add_type(KoiLink)