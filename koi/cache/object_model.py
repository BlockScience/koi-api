from typing import Optional


class CacheObject:
    """
    A container object for the cached data associated with an RID. It is returned by the read and write functions of a CacheableObject. It provides slightly more flexibility than a raw JSON object, which is the format that the underlying data is actually stored in.

    NOTE: can this just be simplified to a dict? provides support for accessing files

    JSON format: 
    {
        "metadata": {
            ...
        },
        "data": {
            ...
        }
    }
    """

    def __init__(
            self, 
            metadata: Optional[dict] = None,
            json_data: Optional[dict] = None
        ):
        
        self.metadata = metadata
        self.json_data = json_data
        self.files = []

        if self.metadata:
            for file in self.metadata.get("files", []):
                self.files.append(file)
    
    @property
    def empty(self):
        return self.metadata is None and self.json_data is None

    @classmethod
    def from_dict(cls, json_object):
        if (json_object is None) or (json_object == {}):
            raise Exception("Invalid JSON body read from cached file")

        return cls(
            json_object.get("metadata"),
            json_object.get("data")
        )

    def to_dict(self):
        return {
            "metadata": self.metadata,
            "data": self.json_data,
        }