from pydantic import BaseModel, Field

class EventCreate(BaseModel):
    lon: float = Field(..., ge=-180, le=180)
    lat: float = Field(..., ge=-90, le=90)