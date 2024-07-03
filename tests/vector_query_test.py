from koi import graph, vectorstore, cache
from rid_lib import RID

print("Enter a query:")
query = input("> ")

print("Matched the following objects:\n")
for rid, score in vectorstore.query(query):
    rid = RID.from_string(rid)
    text = cache.read(rid).data["description"]
    print(f"({score}) {str(rid)}")
    print(text)
    print()