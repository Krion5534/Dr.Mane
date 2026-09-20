from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import random
import asyncio

from app.models.patient import (
    Patient,
    NEEDS_BY_URGENCY,
    MORTALITY_RANGE,
    TREATMENT_MINUTES,
    CAPACITY,
    DOCTOR_COUNT_NORMAL,
    sample_diagnosis,
    to_clock,
    generate_doctors,
)

from app.models.resources import HospitalResourceManager

# ------------------------------------------------------------------
# Resource manager (beds, ICU beds, doctors, nurses)
# ------------------------------------------------------------------

doctors = generate_doctors(DOCTOR_COUNT_NORMAL, seed=42)
resource_manager = HospitalResourceManager(CAPACITY, doctors)

# Track which doctor is treating which patient so we can release them later
patient_doctor: dict[int, int] = {}


TICK_SECONDS = 60     # 1 real minute = 1 sim minute, so a 27-min duration takes 27 real minutes
MINUTES_PER_TICK = 1


router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)



async def simulation_loop():
    global hospital_clock

    while True:
        await asyncio.sleep(TICK_SECONDS)
        hospital_clock += MINUTES_PER_TICK

        changed = False

        # --------------------------------------------------------
        # 1. Finish anyone whose treatment duration has elapsed
        # --------------------------------------------------------
        for patient in patients.values():
            if patient.died or patient.end is not None:
                continue

            if patient.start is not None and hospital_clock - patient.start >= patient.duration:
                patient.end = hospital_clock
                changed = True

                # release resources back to the pool
                resource_manager.release_generic(patient.needs)
                doc_id = patient_doctor.pop(patient.id, None)
                if doc_id is not None:
                    resource_manager.release_doctor(doc_id)

                # roll for death now that treatment's over
                if random.uniform(0, 100) < patient.death_chance:
                    patient.died = True

        # --------------------------------------------------------
        # 2. Admit from the waiting queue, most urgent first
        #    (urgency 1 = most critical, then earliest arrival)
        # --------------------------------------------------------
        waiting = [
            p for p in patients.values()
            if p.start is None and not p.died
        ]
        waiting.sort(key=lambda p: (p.urgency, p.arrival))

        for patient in waiting:
            if not resource_manager.can_allocate(patient.needs):
                continue

            doctor = resource_manager.get_available_doctor(patient.required_specialty)

            if doctor is None:
                # no bed/nurse shortage, just no doctor free yet, try next patient
                continue

            # allocate everything
            resource_manager.allocate_generic(patient.needs)
            resource_manager.assign_doctor(doctor.id, patient.id)
            patient_doctor[patient.id] = doctor.id

            patient.start = hospital_clock
            changed = True

        if changed:
            await broadcast_patients()


@router.on_event("startup")
async def start_simulation():
    asyncio.create_task(simulation_loop())


@router.get("/resources/status")
async def get_resources():
    docs = list(resource_manager.doctors.values())

    doctor_available = sum(1 for d in docs if d.is_available)
    doctor_total = len(docs)

    by_specialty = {}
    for state in docs:
        spec = state.doctor.speciality
        by_specialty.setdefault(spec, {"total": 0, "available": 0})
        by_specialty[spec]["total"] += 1
        if state.is_available:
            by_specialty[spec]["available"] += 1

    # exclude "doctor" from the generic free/capacity dict since doctors
    # are tracked via DoctorState, not resource_manager.free
    generic_resources = {
        r: {"free": resource_manager.free.get(r, 0), "capacity": cap}
        for r, cap in resource_manager.capacity.items()
        if r != "doctor"
    }
    generic_resources["doctor"] = {"free": doctor_available, "capacity": doctor_total}

    return {
        "clock": hospital_clock,
        "clock_time": to_clock(hospital_clock),
        "resources": generic_resources,
        "doctors": {
            "total": doctor_total,
            "available": doctor_available,
            "busy": doctor_total - doctor_available,
            "by_specialty": by_specialty,
        },
        "waiting_count": sum(1 for p in patients.values() if p.start is None and not p.died),
    }

    
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

@router.on_event("startup")
async def start_simulation():
    asyncio.create_task(simulation_loop())

    
    
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



