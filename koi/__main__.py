import uvicorn

uvicorn.run("koi:app", reload=True, reload_dirs=["koi", "rid_lib"], log_level="debug")