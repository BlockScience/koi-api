from fastapi import FastAPI
from base64 import urlsafe_b64decode
from neo4j import GraphDatabase
from rid_lib import RID
from server.config import (
    NEO4J_URI,
    NEO4J_AUTH
)

app = FastAPI()
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

@app.post("/object/{rid_str}")
def object_endpoint(rid_str, use_base64: bool = False):
    if use_base64:
        rid_bytes = rid_str.encode()
        rid_str = urlsafe_b64decode(rid_bytes).decode()

    rid = RID.from_string(rid_str)
    return str(rid)