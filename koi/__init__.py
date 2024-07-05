from fastapi import FastAPI

from koi.routers import (
    conversation,
    knowledge_object,
    link,
    set
)
from koi import rid_extensions

rid_extensions.patch_rid()

app = FastAPI()
app.include_router(knowledge_object.router)
app.include_router(set.router)
app.include_router(link.router)
app.include_router(conversation.router)