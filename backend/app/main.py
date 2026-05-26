import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .features.counties.routes import router as counties_router
from .features.events.routes import router as events_router
from .features.migration.routes import metadata_router, router as migration_router


app = FastAPI(title="Spatial Intel API")


def _get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if not raw:
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    if raw == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


cors_origins = _get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=(cors_origins != ["*"]),
    allow_methods={"*"},
    allow_headers={"*"},
)

app.include_router(events_router)
app.include_router(counties_router)
app.include_router(metadata_router)
app.include_router(migration_router)

@app.get("/")
def root():
    return {"service": "spatial-intel", "status": "running"}
