# RID Protocol

Reference IDs (RIDs) identify and reference arbitrary knowledge 
objects. They are composed of a space, a type, and a reference 
arranged in the following way: 
    
    {space}.{format}:{reference}

Examples:
- `substack.post:metagov/metagov-project-spotlight-koi-pond`
- `slack.message:TMQ3PKXT9/C06DMGNV7E0/1718870811.756359`
- `koi.set:TEEHCqd2AOlvpf2a7olTw`

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

In addition to the basic magic methods defined (`__str__`, `__repr__`,
`__eq__`, `__hash__`), the following properties are defined:

    means: str
    params: dict

Finally, the RID class is called directly in two cases, accessing
the following static methods:

    def from_string(rid_str: str) -> RIDType: ...
    def _add_type(Type: RIDType) -> None: ...

`RID.from_string` is a global RID validator and constructor, which
accepts any RID string and returns an instance of the corresponding
RID type if that type has a definition. If the string is improperly
formatted, or the type is unknown, an exception will be raised.

In order to bind new types to be handled by `RID.from_string`, the 
`RID._add_type` method should be called, passing in the RID type class.


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
---
    # my_rid_types/spaces/__init__.py

    from . import simpletext
---
    # my_rid_types/types.py

    from .spaces.simpletext import *
---
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