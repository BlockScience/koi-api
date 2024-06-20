from abc import ABC, abstractmethod
import inspect
from .exceptions import *

class RID(ABC):
    space: str = None
    format: str = None

    means_loaded = False

    table = {}

    means_delimiter = "."
    rid_delimiter = ":"

    def __init__(self, reference):
        self.reference = reference

    @classmethod
    def from_reference(cls, reference):
        if cls is RID:
            raise Exception
        
        return cls(reference)

    @classmethod
    def from_string(cls, rid_str: str):
        if type(rid_str) is not str:
            raise Exception("RID must inputted as a string")

        # generates a table mapping the means symbol to the class
        if not cls.means_loaded:
            print("loading means table")
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
                (m.space, m.format): m for m in means_classes
            }
            
            cls.means_loaded = True

        rid_components = rid_str.split(RID.rid_delimiter, 1)
        if len(rid_components) != 2:
            raise InvalidFormatError(f"Error processing string '{rid_str}': missing RID delimiter '{RID.rid_delimiter}'")

        symbol, reference = rid_components
        if not symbol:
            raise InvalidFormatError(f"Error processing string '{rid_str}': means is empty string")
        if not reference:
            raise InvalidFormatError(f"Error processing string '{rid_str}': reference is empty string")

        means_components = symbol.split(RID.means_delimiter)
        if len(means_components) != 2:
            raise InvalidFormatError(f"Error processing string '{rid_str}': the means component '{symbol}' should contain exactly one means delimiter '{RID.means_delimiter}'")
        
        space, format = means_components
        if not space:
            raise InvalidFormatError(f"Error processing string '{rid_str}': space is empty string")
        if not format:
            raise InvalidFormatError(f"Error processing string '{rid_str}': format is empty string")

        Means = cls.table.get((space, format), None)

        if not Means:
            raise UndefinedMeansError(f"Error processing string '{rid_str}': the means '{symbol}' does not have a class definition")

        rid = Means.from_reference(reference)
        return rid
    
    @property
    def means(self):
        return self.space + RID.means_delimiter + self.format

    @property
    def params(self):
        return {
            "rid": str(self),
            "space": self.space,
            "format": self.format,
            "means": self.means,
            "reference": self.reference
        }
    
    def __str__(self):
        return self.means + RID.rid_delimiter + self.reference
    
    def __repr__(self):
        return f"<RID {self.__class__.__name__} object '{str(self)}'>"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return str(self) == str(other)
        else:
            return False

    def dereference(self):
        pass