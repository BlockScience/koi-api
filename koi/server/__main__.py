import uvicorn

uvicorn.run(
    "koi.server:app", 
    reload=True, 
    reload_dirs=["koi", "rid_lib"], 
    log_level="debug"
)