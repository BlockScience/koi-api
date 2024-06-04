from server import graph, vectorstore
from rid_lib import RID


sources, targets = graph.directed_relation.read(RID.from_string("internal+link:fPOx8eveA39C_8UKKI-KF"))

vectorstore.embed_objects([RID.from_string(t) for t in targets])