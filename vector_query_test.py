from server import graph, vectorstore, cache
from rid_lib import RID

rids = [RID.from_string(rid) for rid in vectorstore.query("What is Metagov's data policy?")]

for rid in rids:
    print(cache.read(rid))
