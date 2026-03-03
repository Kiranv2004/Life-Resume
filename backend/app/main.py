from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, github, analysis, reports
from app.core.database import init_db, close_db
from app.core.config import settings

app = FastAPI(title="Life Resume API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(github.router, prefix="/github", tags=["github"])
app.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])


@app.on_event("startup")
def on_startup():
    init_db()


@app.middleware("http")
async def ensure_db_connection(request, call_next):
    init_db()
    return await call_next(request)


@app.on_event("shutdown")
def on_shutdown():
    close_db()


@app.get("/health")
def health_check():
    return {"status": "ok"}
