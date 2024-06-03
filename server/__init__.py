from fastapi import FastAPI
from server.routers import (
    knowledge_object,
    undirected_relation
)

app = FastAPI()
app.include_router(knowledge_object.router)
app.include_router(undirected_relation.router)