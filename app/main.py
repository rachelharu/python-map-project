from fastapi import FastAPI
from app.features.events.routes import router as events_router
from app.features.events.models import Base
from app.db import engine

app = FastAPI(title="Spatial Intel API")

# Create tables on startup (fine for dev; later use migrations)
Base.metadata.create_all(bind=engine)

app.include_router(events_router)

@app.get("/")
def root():
    return {"service": "spatial-intel", "status": "running"}
