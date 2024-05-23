from fastapi import FastAPI
from server.routers import objects

app = FastAPI()
app.include_router(objects.router)