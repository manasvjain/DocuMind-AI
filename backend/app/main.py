from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import admin,analytics,auth,buildings,export,features,imagery,jobs,layer_aliases,models,projects
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.rate_limit import rate_limiter
configure_logging(); settings=get_settings()
app=FastAPI(title=settings.app_name,version="1.0.0",description="AI + GIS platform for extracting geospatial features from drone orthophotos.")
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.middleware("http")(rate_limiter)
for router in (auth.router,projects.router,imagery.router,jobs.router,models.router,features.router,analytics.router,export.router,admin.router,buildings.router,layer_aliases.router): app.include_router(router)
@app.get("/health",tags=["system"])
def health(): return {"status":"ok","service":"svamitrai-api"}
@app.get("/ready",tags=["system"])
def ready():
    from app.db.session import engine
    try:
        with engine.connect() as conn: conn.exec_driver_sql("SELECT 1")
        return {"status":"ready","database":"ok"}
    except Exception: return JSONResponse(status_code=503,content={"status":"not_ready","database":"unavailable"})
@app.exception_handler(ValueError)
async def value_error_handler(request:Request,exc:ValueError): return JSONResponse(status_code=400,content={"detail":str(exc)})
