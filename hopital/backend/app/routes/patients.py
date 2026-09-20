from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import random
import asyncio

TICK_SECONDS = 1        # real seconds per tick
MINUTES_PER_TICK = 1    # sim minutes advanced per tick

def patient_to_json(patient: Patient) -> dict:
    if patient.died:
        status = "Died"
    elif patient.end is not None:
        status = "Diagnosed"
    elif patient.start is not None:
        status = "In Treatment"
    else:
        status = "Waiting"

    return {
        "id": patient.id,
        "name": patient.name,
        "age": patient.age,
        "urgency": patient.urgency,
        "diagnosis": patient.diagnosis,
        "required_specialty": patient.required_specialty,
        "status": status,          # <-- add this line
        "arrival": patient.arrival,
        "arrival_time": patient.arrival_time,
        "start": patient.start,
        "start_time": patient.start_time,
        "end": patient.end,
        "end_time": patient.end_time,
        "wait": patient.wait,
        "death_chance": round(patient.death_chance, 1),
        "needs": patient.needs,
        "duration": patient.duration,
        "during_surge": patient.during_surge,
        "mortality_chance": patient.mortality_chance,
        "downgraded": patient.downgraded,
        "died": patient.died,
    }
    


async def simulation_loop():
    global hospital_clock

    while True:
        await asyncio.sleep(TICK_SECONDS)
        hospital_clock += MINUTES_PER_TICK

        changed = False

        for patient in patients.values():

            if patient.died:
                continue

            # no resource checks, everyone starts immediately for demo purposes
            if patient.start is None:
                patient.start = hospital_clock
                changed = True
                continue

            if patient.end is None and hospital_clock - patient.start >= patient.duration:
                patient.end = hospital_clock
                changed = True

                # roll for death based on death_chance at completion
                if random.uniform(0, 100) < patient.death_chance:
                    patient.died = True

        if changed:
            await broadcast_patients()


@router.on_event("startup")
async def start_simulation():
    asyncio.create_task(simulation_loop())

    
from app.models.patient import (
    Patient,
    NEEDS_BY_URGENCY,
    MORTALITY_RANGE,
    TREATMENT_MINUTES,
    sample_diagnosis,
    to_clock,
)


router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)


# ------------------------------------------------------------------
# Request models
# ------------------------------------------------------------------

class AdmitPatientRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=120)
    urgency: int = Field(..., ge=1, le=4)
    diagnosis: Optional[str] = None


class UpdatePatientRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=120)
    urgency: Optional[int] = Field(None, ge=1, le=4)
    diagnosis: Optional[str] = None

# ------------------------------------------------------------------
# In-memory hospital state
# ------------------------------------------------------------------

patients: dict[int, Patient] = {}

next_patient_id = 1

# Current simulation clock.
# Change this from your simulation engine when the simulation advances.
hospital_clock = 0


def advance_clock(new_time: int):
    """
    Call this from your simulation engine to move the clock forward.
    Module-level globals can't be mutated from outside by reassigning
    the imported name, so this setter is the correct way to do it.
    """
    global hospital_clock
    hospital_clock = new_time


# Connected frontend clients
connected_clients: set[WebSocket] = set()


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def patient_to_json(patient: Patient) -> dict:
    """
    Convert Patient into JSON-safe data for the frontend.
    """

    return {
        "id": patient.id,
        "name": patient.name,
        "age": patient.age,
        "urgency": patient.urgency,
        "diagnosis": patient.diagnosis,
        "required_specialty": patient.required_specialty,

        "arrival": patient.arrival,
        "arrival_time": patient.arrival_time,

        "start": patient.start,
        "start_time": patient.start_time,

        "end": patient.end,
        "end_time": patient.end_time,

        "wait": patient.wait,
        "death_chance": round(patient.death_chance, 1),

        "needs": patient.needs,

        "duration": patient.duration,

        "during_surge": patient.during_surge,
        "mortality_chance": patient.mortality_chance,

        "downgraded": patient.downgraded,
        "died": patient.died,
    }


async def broadcast_patients():
    """
    Send the current patient list to every connected frontend.
    """

    message = {
        "type": "patients_update",
        "patients": [
            patient_to_json(patient)
            for patient in patients.values()
        ],
    }

    dead_clients = []

    for websocket in connected_clients:
        try:
            await websocket.send_json(message)
        except Exception:
            dead_clients.append(websocket)

    for websocket in dead_clients:
        connected_clients.discard(websocket)


# ------------------------------------------------------------------
# Admit patient
# ------------------------------------------------------------------

@router.post("/admit")
async def admit_patient(request: AdmitPatientRequest):

    global next_patient_id

    # --------------------------------------------------------------
    # Validate diagnosis
    # --------------------------------------------------------------

    diagnosis = request.diagnosis

    # If frontend doesn't provide a diagnosis, generate one.
    if diagnosis is None:
        diagnosis = sample_diagnosis(
            age=request.age,
            urgency=request.urgency,
        )

    # --------------------------------------------------------------
    # Validate pediatric diagnosis
    # --------------------------------------------------------------

    if request.age < 16:

        pediatric_diagnoses = {
            "Pediatric Fever",
            "Childhood Asthma",
        }

        if diagnosis not in pediatric_diagnoses:
            raise HTTPException(
                status_code=400,
                detail="Patients under 16 must have a pediatric diagnosis.",
            )

    # --------------------------------------------------------------
    # Generate patient properties
    # --------------------------------------------------------------

    patient_id = next_patient_id
    next_patient_id += 1

    duration_min, duration_max = TREATMENT_MINUTES[request.urgency]

    duration = random.randint(
        duration_min,
        duration_max,
    )

    mortality_min, mortality_max = MORTALITY_RANGE[request.urgency]

    mortality_chance = random.randint(
        mortality_min,
        mortality_max,
    )

    needs = dict(
        NEEDS_BY_URGENCY[request.urgency]
    )

    # --------------------------------------------------------------
    # Create patient
    # --------------------------------------------------------------

    patient = Patient(
        id=patient_id,
        name=request.name,
        age=request.age,
        arrival=hospital_clock,
        urgency=request.urgency,
        needs=needs,
        duration=duration,
        diagnosis=diagnosis,
        mortality_chance=mortality_chance,
    )

    # --------------------------------------------------------------
    # Store
    # --------------------------------------------------------------

    patients[patient_id] = patient

    # --------------------------------------------------------------
    # Notify WebSocket clients
    # --------------------------------------------------------------

    await broadcast_patients()

    return {
        "success": True,
        "patient": patient_to_json(patient),
    }


# ------------------------------------------------------------------
# Get all patients
# ------------------------------------------------------------------

@router.get("/all")
async def get_all_patients():

    return {
        "patients": [
            patient_to_json(patient)
            for patient in patients.values()
        ]
    }



@router.patch("/{patient_id}")
async def update_patient(
    patient_id: int,
    request: UpdatePatientRequest,
):
    patient = patients.get(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found.",
        )

    if request.name is not None:
        patient.name = request.name

    if request.age is not None:
        patient.age = request.age

    if request.urgency is not None:
        patient.urgency = request.urgency
        patient.needs = dict(NEEDS_BY_URGENCY[request.urgency])

    if request.diagnosis is not None:
        patient.diagnosis = request.diagnosis

    await broadcast_patients()

    return {
        "success": True,
        "patient": patient_to_json(patient),
    }


@router.delete("/{patient_id}")
async def delete_patient(patient_id: int):

    patient = patients.pop(patient_id, None)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found.",
        )

    await broadcast_patients()

    return {
        "success": True,
        "patient_id": patient_id,
    }

# ------------------------------------------------------------------
# Get one patient
# ------------------------------------------------------------------

@router.get("/{patient_id}")
async def get_patient(patient_id: int):

    patient = patients.get(patient_id)

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found.",
        )

    return {
        "patient": patient_to_json(patient)
    }


# ------------------------------------------------------------------
# WebSocket - live patient list
# ------------------------------------------------------------------

@router.websocket("/view/all")
async def patient_websocket(websocket: WebSocket):

    await websocket.accept()

    connected_clients.add(websocket)

    try:

        # Send current state immediately after connecting
        await websocket.send_json({
            "type": "patients_update",
            "patients": [
                patient_to_json(patient)
                for patient in patients.values()
            ],
        })

        while True:

            # Keep connection alive and allow frontend messages.
            data = await websocket.receive_json()

            message_type = data.get("type")

            # Optional future messages
            if message_type == "ping":
                await websocket.send_json({
                    "type": "pong"
                })

    except WebSocketDisconnect:

        connected_clients.discard(websocket)

    except Exception:

        connected_clients.discard(websocket)


