from abc import ABC, abstractmethod

from .exceptions import *


class RID(ABC):
    space: str = None
    format: str = None

    table = {}

    means_delimiter = "."
    rid_delimiter = ":"
    
    def __str__(self):
        return self.means + RID.rid_delimiter + self.reference
    
    def __repr__(self):
        return f"<RID {self.__class__.__name__} object '{str(self)}'>"
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return str(self) == str(other)
        else:
            return False
        
    def __hash__(self):
        return hash(str(self))
        
    @staticmethod
    def _add_type(Type):
        RID.table[(Type.space, Type.format)] = Type

    @staticmethod
    def from_string(rid_str: str):
        if type(rid_str) is not str:
            raise InvalidRidFormatError("RID must inputted as a string")
            
        rid_components = rid_str.split(RID.rid_delimiter, 1)
        if len(rid_components) != 2:
            raise InvalidRidFormatError(f"Error processing string '{rid_str}': missing RID delimiter '{RID.rid_delimiter}'")

        symbol, reference = rid_components
        if not symbol:
            raise InvalidRidFormatError(f"Error processing string '{rid_str}': means is empty string")
        if not reference:
            raise InvalidRidFormatError(f"Error processing string '{rid_str}': reference is empty string")

        means_components = symbol.split(RID.means_delimiter)
        if len(means_components) != 2:
            raise InvalidRidFormatError(f"Error processing string '{rid_str}': the means component '{symbol}' should contain exactly one means delimiter '{RID.means_delimiter}'")
        
        space, format = means_components
        if not space:
            raise InvalidRidFormatError(f"Error processing string '{rid_str}': space is empty string")
        if not format:
            raise InvalidRidFormatError(f"Error processing string '{rid_str}': format is empty string")

        Type = RID.table.get((space, format))

        if Type is None:
            raise UndefinedMeansError(f"Error processing string '{rid_str}': the means '{symbol}' does not have a class definition")

        rid = Type.from_reference(reference)

        if not isinstance(rid, Type):
            raise TypeImplementationError(f"{Type.__name__} must return a class instance in the 'from_reference' function")

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
    
    @classmethod
    @abstractmethod
    def from_reference(cls, reference):
        ...

    @abstractmethod
    def dereference(self):
        ...


class DereferencedData:
    def __init__(self, json=None, bytes=None):
        self.json = json
        self.bytes = bytes