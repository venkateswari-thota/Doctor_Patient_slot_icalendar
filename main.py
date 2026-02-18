from fastapi import FastAPI, HTTPException
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from bson import ObjectId

from database import db
from models import SlotCreate, SlotInDB, BookingRequest
from ical_utils import generate_appointment_ics
from email_utils import send_calendar_email

app = FastAPI(title="Doctor Appointment System")

@app.post("/slots/create", response_model=dict)
async def create_slot(slot: SlotCreate):
    """Manager endpoint to create a single free slot with auto-generated slot_id."""
    # Check for time conflicts
    existing = await db.slots.find_one({
        "doctor_id": slot.doctor_id,
        "date": slot.date,
        "start_time": slot.start_time
    })
    if existing:
        raise HTTPException(status_code=400, detail="Slot already exists at this time.")
    
    # Auto-generate slot_id (e.g., slot001)
    count = await db.slots.count_documents({})
    slot_id = f"slot{str(count + 1).zfill(3)}"
    
    # Ensure uniqueness in case of deletions
    while await db.slots.find_one({"slot_id": slot_id}):
        count += 1
        slot_id = f"slot{str(count + 1).zfill(3)}"

    new_slot = slot.dict()
    new_slot["slot_id"] = slot_id
    new_slot["status"] = "free"
    new_slot["patient_id"] = None
    new_slot["patient_email"] = None
    new_slot["calendar_uid"] = None
    
    result = await db.slots.insert_one(new_slot)
    return {"message": "Slot created successfully", "id": str(result.inserted_id), "slot_id": slot_id}

@app.get("/slots/free", response_model=List[dict])
async def get_free_slots():
    """Returns all slots that are currently free."""
    cursor = db.slots.find({"status": "free"})
    slots = []
    async for document in cursor:
        document["_id"] = str(document["_id"])
        slots.append(document)
    return slots

@app.get("/slots/status/{slot_id}", response_model=dict)
async def get_slot_status(slot_id: str):
    """Returns the status of a specific slot using the human-readable slot_id (e.g., slot001)."""
    slot = await db.slots.find_one({"slot_id": slot_id})
    if not slot:
        # Fallback to check if it's an ObjectId
        try:
            slot = await db.slots.find_one({"_id": ObjectId(slot_id)})
        except:
            pass
            
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    slot["_id"] = str(slot["_id"])
    return slot

@app.post("/slots/book/{slot_id}", response_model=dict)
async def book_slot(slot_id: str, request: BookingRequest):
    """Patient endpoint to book a specific slot using either _id or slot_id."""
    query = {"status": "free"}
    try:
        query["_id"] = ObjectId(slot_id)
    except:
        query["slot_id"] = slot_id

    calendar_uid = f"{uuid.uuid4()}@hospital.com"

    # Atomic update to prevent double booking
    result = await db.slots.find_one_and_update(
        query,
        {
            "$set": {
                "status": "booked",
                "patient_id": request.patient_id,
                "patient_email": request.patient_email,
                "calendar_uid": calendar_uid
            }
        },
        return_document=True
    )

    if not result:
        raise HTTPException(status_code=400, detail="Slot is unavailable, already booked, or does not exist")

    # Generate iCalendar Invite
    ics_content = generate_appointment_ics(
        uid=calendar_uid,
        summary=f"Doctor Appointment - {request.patient_id}",
        description="Medical checkup with the doctor.",
        start_time=result["start_time"],
        end_time=result["end_time"],
        date_str=result["date"]
    )
    
    # Send Real Email
    await send_calendar_email(
        subject=f"Appointment Confirmation: Doctor & Patient ({slot_id})",
        recipients=[request.patient_email, result["doctor_email"]],
        body=(
            f"Your appointment ({slot_id}) is confirmed for {result['date']} at {result['start_time']}.\n"
            "Please add this appointment to your calendar.\n\n"
            "Best Regards,\n"
            "Hospital Appointment System"
        ),
        ics_content=ics_content,
        filename="appointment.ics",
        method="REQUEST"
    )

    return {
        "message": "Appointment booked successfully. Emails sent.",
        "slot_id": result["slot_id"],
        "calendar_uid": calendar_uid
    }

@app.delete("/slots/cancel/{slot_id}", response_model=dict)
async def cancel_slot(slot_id: str):
    """Endpoint to cancel a booking using either _id or slot_id."""
    query = {"status": "booked"}
    try:
        query["_id"] = ObjectId(slot_id)
    except:
        query["slot_id"] = slot_id

    slot = await db.slots.find_one(query)
    if not slot:
        raise HTTPException(status_code=404, detail="Booked slot not found")

    await db.slots.update_one(
        {"_id": slot["_id"]},
        {"$set": {"status": "free", "patient_id": None, "patient_email": None, "calendar_uid": None}}
    )

    # Generate Cancellation iCalendar
    cancel_ics = generate_appointment_ics(
        uid=slot["calendar_uid"],
        summary="CANCELLED: Doctor Appointment",
        description="This appointment has been cancelled.",
        start_time=slot["start_time"],
        end_time=slot["end_time"],
        date_str=slot["date"],
        method="CANCEL",
        sequence=1
    )

    # Send Real Cancellation Email
    await send_calendar_email(
        subject=f"Appointment Cancelled: {slot['slot_id']}",
        recipients=[slot["patient_email"], slot["doctor_email"]],
        body=(
            f"The appointment on {slot['date']} ({slot['slot_id']}) has been cancelled.\n\n"
            "Best Regards,\n"
            "Hospital Appointment System"
        ),
        ics_content=cancel_ics,
        filename="cancellation.ics",
        method="CANCEL"
    )
    
    return {"message": "Appointment cancelled and slot is now free", "slot_id": slot["slot_id"]}
