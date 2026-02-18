from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time

class SlotBase(BaseModel):
    doctor_id: str
    doctor_email: str
    date: str  # Format: YYYY-MM-DD
    start_time: str # Format: HH:MM:SS
    end_time: str   # Format: HH:MM:SS

class SlotCreate(SlotBase):
    pass

class SlotInDB(SlotBase):
    id: str = Field(alias="_id")
    slot_id: str  # e.g., slot001
    status: str = "free"
    patient_id: Optional[str] = None
    patient_email: Optional[str] = None
    calendar_uid: Optional[str] = None

class BookingRequest(BaseModel):
    patient_id: str
    patient_email: str
