import uvicorn

uvicorn.run("server:app", reload=True, log_level="debug")