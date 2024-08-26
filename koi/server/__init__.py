from fastapi import FastAPI, Request, Response
import logging

from .routers import (
    conversation,
    knowledge_object,
    link,
    set
)

app = FastAPI()
app.include_router(knowledge_object.router)
app.include_router(set.router)
app.include_router(link.router)
app.include_router(conversation.router)

@app.middleware("http")
async def middleware(request: Request, call_next):    
    print(await request.json())
    response = await call_next(request)
    return response

logging.basicConfig(filename='info.log', level=logging.DEBUG)
