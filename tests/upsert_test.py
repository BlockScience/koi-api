from koi import graph, vectorstore
from rid_lib import RID, SlackChannel

link = graph.base_interface.read_link(
    SlackChannel("metagov/C06DMGNV7E0")
)
sources, targets = graph.link_interface.read(link)

vectorstore.embed_objects([RID.from_string(t) for t in targets])