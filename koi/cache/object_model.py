from dataclasses import dataclass, field


@dataclass
class CacheObject:
    """
    Object representing an individual RID cache entry.

    A container object for the cached data associated with an RID. It is 
    returned by the read and write functions of a CacheableObject. It 
    stores the JSON data associated with an RID object, corresponding
    metadata, and files if available.

    JSON format: 
    {
        "metadata": {
            "files": {
                ...
            },
            ...
        },
        "data": {
            ...
        }
    }
    """

    metadata: dict | None = None
    json_data: dict | None = None
    files: list = field(init=False)

    def __post_init__(self):
        """Populates files list if present in metadata."""
        self.files = []

        if self.metadata:
            for file in self.metadata.get("files", []):
                self.files.append(file)

    def __bool__(self):
        return bool(self.metadata) or bool(self.json_data)

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