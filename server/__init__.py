from fastapi import FastAPI
from server.routers import (
    knowledge_object,
    link,
    set
)

app = FastAPI()
app.include_router(knowledge_object.router)
app.include_router(set.router)
app.include_router(link.router)