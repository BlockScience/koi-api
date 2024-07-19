from rid_lib.core import RID


class VectorObject:
    def __init__(
            self,
            vector: dict
        ):

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

    def to_dict(self):
        json_data = {
            "id": self.id, 
            "rid": str(self.rid),
            "score": self.score,
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
        cached_obj = self.rid.cache.read()
        text = cached_obj.json_data.get("text")
        if not text: return

        if self.is_chunk:
            return text[self.chunk_start:self.chunk_end]
        else:
            return text
