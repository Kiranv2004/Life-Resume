from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, github, analysis, reports
from app.core.database import Base, engine
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
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}
