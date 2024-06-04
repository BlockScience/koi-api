from abc import ABC, abstractmethod
import inspect

class RID(ABC):
    space: str = None
    format: str = None

    means_loaded = False

    table = {}

    means_delimiter = "+"
    rid_delimiter = ":"

    def __init__(self, reference=None):
        self.reference = reference

    @classmethod
    def from_string(cls, rid_str):
        # generates a table mapping the means symbol to the class
        if not cls.means_loaded:
            from rid_lib import means

            # generates list of all Means derived from RID
            means_classes = [
                m[1] for m in
                inspect.getmembers(means)
                if inspect.isclass(m[1]) and
                issubclass(m[1], RID) and
                m[1] is not RID 
            ]

            # class properties no longer supported
            cls.table = {
                m.space + RID.means_delimiter + m.format: m for m in means_classes
            }

            cls.means_loaded = True

        symbol, reference = rid_str.split(RID.rid_delimiter, 1)

        Means = cls.table.get(symbol, None)

        if not Means:
            raise Exception("Means not found")

        rid = Means(reference)
        return rid
    
    @property
    def means(self):
        return self.space + RID.means_delimiter + self.format
    
    def __str__(self):
        return self.means + RID.rid_delimiter + self.reference

    def dereference(self):
        pass