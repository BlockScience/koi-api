from dataclasses import dataclass, field


@dataclass
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

    metadata: dict | None = None
    json_data: dict | None = None
    files: dict = field(init=False)

    def __post_init__(self):
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