from server import graph, vectorstore
from rid_lib import RID


sources, targets = graph.directed_relation.read(RID.from_string("internal+link:jI1RXTGX_8KOvRrVdUwv8"))

vectorstore.embed_objects([RID.from_string(t) for t in targets])