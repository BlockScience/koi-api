import uvicorn

uvicorn.run("koi:app", reload=True, log_level="debug")