import json

from rid_lib.core import RID
from koi.config import CHUNK_SIZE


class VectorObject:
    def __init__(
            self,
            vector: dict
        ):
        """Object representing a vector associated with an RID object.
        
        A container object for a vector associated with an RID. It is
        returned by read and query functions of a VectorInterface. It
        stores the metadata associated with an embedded RID object,
        and chunk information if applicable.
        """

        self.id = vector.get("id")
        self.metadata = vector.get("metadata")
        self.values = vector.get("values")
        self.score = vector.get("score")
        self.rid = RID.from_string(self.metadata["rid"])
        self.is_chunk = "chunk_id" in self.metadata

        if self.is_chunk:
            self.chunk_id = int(vector["metadata"]["chunk_id"])
            self.chunk_start = int(self.metadata["chunk_start"])
            self.chunk_end = int(self.metadata["chunk_end"])

    def __repr__(self):
        return f"<Vector object RID '{self.rid}'{' chunk ' + str(self.chunk_id) if self.is_chunk else ''}>"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return str(self) == str(other)
        else:
            return False
        
    def __hash__(self):
        return hash(str(self))
    
    def to_dict(self):
        json_data = {
            "id": self.id, 
            "rid": str(self.rid),
            "score": self.score or None,
            "metadata": self.metadata,
            "text": self.get_text(),
            "is_chunk": self.is_chunk,
        }

        if self.is_chunk:
            json_data.update({
                "chunk_id": self.chunk_id,
                "chunk_start": self.chunk_start,
                "chunk_end": self.chunk_end
            })
        return json_data

    def get_text(self):
        """Returns associated text data from the cache.

        If VectorObject is a chunk, the start and end string indices are
        used to return the correct chunk of text.
        """
        cached_obj = self.rid.cache.read()
        text = cached_obj.json_data.get("text")
        if not text: return

        if self.is_chunk:
            return text[self.chunk_start:self.chunk_end]
        else:
            return text
        
    def get_extended_text(self):
        """Extends chunk size to include greater context."""
        
        cached_obj = self.rid.cache.read()
        text = cached_obj.json_data.get("text")
        if not text: return

        if self.is_chunk:
            return text[
                max(0, self.chunk_start - CHUNK_SIZE):
                min(len(text), self.chunk_end + CHUNK_SIZE)
            ]
        else:
            return text
