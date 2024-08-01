from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from .exceptions import *


class PostInitCaller(ABCMeta):
    """RID metaclass adding support for a post init function."""
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.__post_init__()
        return obj
    
class RID(metaclass=PostInitCaller):
    """Base RID class which defines expected parameters and functions to
    be implemented by RID types.


    # RID Protocol

    Reference IDs (RIDs) identify and reference arbitrary knowledge 
    objects. They are composed of a space, a type, and a reference 
    arranged in the following way: {space}.{format}:{reference}

    Examples:
        substack.post:metagov/metagov-project-spotlight-koi-pond
        slack.message:TMQ3PKXT9/C06DMGNV7E0/1718870811.756359
        koi.set:TEEHCqd2AOlvpf2a7olTw

    Spaces represent large containers that knowledge objects are found
    in. Generally, they should represent a general access method, such
    as a platform API, but not a specific endpoint or method of 
    retrieving a resource. Conceptually they map to a platform or domain
    where many types of objects exist. In the examples above, Substack,
    Slack, and Koi are spaces.

    Formats (better name pending) are the types of objects that exist
    within spaces. They are bound to specific access methods within the
    context of the space they belong to. In the examples above Posts,
    Messages, and Sets are formats.

    Together, a space and a format form an RID type, with a defined
    method of retrieval called a dereference function. A type can be
    thought of as a "means of reference", or the way a knowledge
    object is referenced by an RID.

    The final component of an RID is the reference, which provides the 
    information necessary to dereference the knowledge object it refers 
    to. One way to think of it is the input to the dereference function. 
    
    
    # RID Class Implementation

    The RID class provides the template for all RID types and access to
    a global constructor. It cannot be instantiated. Derived RID spaces
    and types must implement the following methods and properties:

        space: str
        format: str
        reference: str

        def from_reference(cls, reference) -> RIDType: ...
        def dereference(self) -> DataObject: ...

    In addition to the basic magic methods defined (__str__, __repr__,
    __eq__, __hash__), the following properties are defined:

        means: str
        params: dict

    Finally, the RID class is called directly in two cases, accessing
    the following static methods:

        def from_string(rid_str: str) -> RIDType: ...
        def _add_type(Type: RIDType) -> None: ...

    RID.from_string is a global RID validator and constructor, which
    accepts any RID string and returns an instance of the corresponding
    RID type if that type has a definition. If the string is improperly
    formatted, or the type is unknown, an exception will be raised.

    In order to bind new types to be handled by RID.from_string, the 
    RID._add_type method should be called, passing in the RID type class.


    # Implementing New RID Types

    The RID system is designed to be easily expandable to support new
    types. Let's walk through a simple example implementing a custom 
    space and type for a made up platform called SimpleText, a 
    publishing website that serves simple text posts. Here is what the 
    URL for a SimpleText post looks like:

        https://simpletext.com/p/my-text-post

    To build a corresponding RID, we'll extract the minimum information
    needed to uniquely identify this post. In this case, the post id at 
    the end of the URL is all the information needed, and can become our
    reference. For our space and format strings, "simpletext" and "post"
    can be used, giving us the following RID:

        simpletext.post:my-text-post

    Now we can move on to the implementation of our RID type. We'll need
    to set up a package to contain our new classes. This is the
    recommended structure:

        my_rid_types/
            spaces/
                simpletext/
                    __init__.py
                    base.py
                    post.py
                __init__.py         
            __init__.py
            types.py

    First we'll define our new space, which should be defined in base.py:

        # my_rid_types/spaces/simpletext/base.py
        from rid_lib.core import RID

        class SimpleTextSpace(RID):
            space = "substack"

    Next we can define our post type:

        # my_rid_types/spaces/simpletext/post.py
        import requests
        from rid_lib.core import RID, DataObject
        from .base import SimpleTextSpace

        class SimpleTextPost(SimpleTextSpace):
            format = "post"

            def __init__(self, post_id: str):
                self.post_id = post_id
                self.reference = post_id
            
            @classmethod
            def from_reference(cls, reference):
                return cls(reference)

            def dereference(self):
                url = f"https://simpletext.com/p/{self.post_id}"
                response = requests.get(url)

                return DataObject(
                    json_data=response.json()
                )
        
        RID._add_type(SimpleTextPost)

    Finally make sure to update the package imports to easily import
    your types.

        # my_rid_types/spaces/simpletext/__init__.py
        from .post import SimpleTextPost

        # my_rid_types/spaces/__init__.py
        from . import simpletext

        # my_rid_types/types.py
        from .spaces.simpletext import *

        # my_rid_types/__init_-.py
        from . import spaces
        from . import types

    Now we can use the new RID types in our code:

        # rid_test.py
        from rid_lib.core import RID
        from my_rid_types.types import SimpleTextPost
        
        post1 = RID.from_string("simpletext.post:my-text-post")
        post2 = SimpleTextPost.from_reference("my-text-post")
        assert post1 == post2
        post_data_object = post1.dereference()
        print(post_data_object.json_data)

    And that's it! Take a look at the included RID types for more 
    complex examples.
    """
    
    space: str
    format: str
    reference: str

    table = {}

    means_delimiter = "."
    rid_delimiter = ":"

    def __post_init__(self):
        print("called post init")
        pass
    
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
            raise InvalidRidFormatError(
                f"Error processing string '{rid_str}': missing RID delimiter"
                f"'{RID.rid_delimiter}'")

        symbol, reference = rid_components
        if not symbol:
            raise InvalidRidFormatError(
                f"Error processing string '{rid_str}': means is empty string")
        if not reference:
            raise InvalidRidFormatError(
                f"Error processing string '{rid_str}': reference is empty string")

        means_components = symbol.split(RID.means_delimiter)
        if len(means_components) != 2:
            raise InvalidRidFormatError(
                f"Error processing string '{rid_str}': the means component"
                f"'{symbol}' should contain exactly one means delimiter" 
                f"'{RID.means_delimiter}'")
        
        space, format = means_components
        if not space:
            raise InvalidRidFormatError(
                f"Error processing string '{rid_str}': space is empty string")
        if not format:
            raise InvalidRidFormatError(
                f"Error processing string '{rid_str}': format is empty string")

        Type = RID.table.get((space, format))

        if Type is None:
            raise UndefinedMeansError(
                f"Error processing string '{rid_str}': the means '{symbol}'"
                "does not have a class definition"
            )

        rid = Type.from_reference(reference)

        if not isinstance(rid, Type):
            raise TypeImplementationError(
                f"{Type.__name__} must return a class instance in the"
                "'from_reference' function"
            )

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

@dataclass
class DataObject:
    """Container storing data returned from RID dereference functions.

    Two optional fields for storing JSON and file data. File data should
    be formatted like this:

        {
            "file_name1": "text string",
            "file_name2": bytes()
        }
    
    """

    json_data: dict | None = None
    files: dict[str, bytes | str] | None = None

    def __bool__(self) -> bool:
        return bool(self.json_data) or bool(self.files)
    
    def to_dict(self) -> dict:
        return {
            "json_data": self.json_data,
            "files": self.files
        }