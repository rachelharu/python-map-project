from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .features.events.routes import router as events_router
from .features.events.models import Base
from .db import engine

app = FastAPI(title="Spatial Intel API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods={"*"},
    allow_headers={"*"},
)

# Schema is managed by Alembic migrations
# Base.metadata.create_all(bind=engine)

app.include_router(events_router)

@app.get("/")
def root():
    return {"service": "spatial-intel", "status": "running"}
