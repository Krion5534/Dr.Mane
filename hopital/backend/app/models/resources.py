from dataclasses import dataclass
from typing import Dict, List, Optional
from app.models.patient import Doctor, Patient, to_clock


def _patient_summary(p: Patient) -> dict:
    # one patient, flattened to json-safe fields for the frontend
    return {
        "id": p.id,
        "name": p.name,
        "age": p.age,
        "urgency": p.urgency,
        "diagnosis": p.diagnosis,
        "required_specialty": p.required_specialty,
        "arrival_time": p.arrival_time,
        "start_time": p.start_time,
        "end_time": p.end_time,
        "wait": p.wait,
        "death_chance": round(p.death_chance, 1),
        "downgraded": p.downgraded,
    }


@dataclass
class DoctorState:
    doctor: Doctor
    assigned_patient_id: Optional[int] = None
    is_on_shift: bool = True

    @property
    def is_available(self) -> bool:
        return self.is_on_shift and self.assigned_patient_id is None


class HospitalResourceManager:
    def __init__(self, generic_capacity: dict, doctors: List[Doctor]):
        self.capacity = dict(generic_capacity)
        self.free = dict(generic_capacity)
        # maps doc ids to their trackin states
        self.doctors: Dict[int, DoctorState] = {
            doc.id: DoctorState(doctor=doc) for doc in doctors
        }

    def can_allocate(self, needs: dict) -> bool:
        # doctors are checked separately (get_available_doctor), so skip them here
        return all(self.free.get(r, 0) >= n for r, n in needs.items() if r != "doctor")

    def allocate_generic(self, needs: dict):
        for r, n in needs.items():
            if r != "doctor":
                self.free[r] -= n

    def release_generic(self, needs: dict):
        for r, n in needs.items():
            if r != "doctor":
                self.free[r] += n
                if self.free[r] > self.capacity[r]:
                    raise ValueError(f"released too many {r}")

    def set_capacity(self, resource: str, cap: int):
        # free can go negative if staff leave while busy, that just blocks new admissions
        diff = cap - self.capacity.get(resource, 0)
        self.capacity[resource] = cap
        self.free[resource] = self.free.get(resource, 0) + diff

    def set_doctors_on_shift(self, n: int):
        # first n doctors are on shift. busy ones finish their patient first
        for i, state in enumerate(self.doctors.values()):
            state.is_on_shift = i < n

    def get_available_doctor(self, required_specialty: str) -> Optional[Doctor]:
        # look for exact specialty match first
        for state in self.doctors.values():
            if state.is_available and state.doctor.speciality == required_specialty:
                return state.doctor

        # fallback to genral doc if needed
        if required_specialty != "General Doctor":
            for state in self.doctors.values():
                if state.is_available and state.doctor.speciality == "General Doctor":
                    return state.doctor

        return None

    def assign_doctor(self, doctor_id: int, patient_id: int):
        if doctor_id in self.doctors:
            self.doctors[doctor_id].assigned_patient_id = patient_id

    def release_doctor(self, doctor_id: int):
        if doctor_id in self.doctors:
            self.doctors[doctor_id].assigned_patient_id = None

    def snapshot_for_frontend(self, clock: int, waiting: List[Patient], in_treatment: List[Patient]) -> dict:
        """one json-safe dict describing the whole hospital at this minute."""
        docs = list(self.doctors.values())
        return {
            "clock": clock,
            "clock_time": to_clock(clock),
            "resources": {
                r: {"free": self.free.get(r, 0), "capacity": cap}
                for r, cap in self.capacity.items()
            },
            "doctors": {
                "on_shift": sum(1 for d in docs if d.is_on_shift),
                "available": sum(1 for d in docs if d.is_available),
                "busy": sum(1 for d in docs if d.is_on_shift and not d.is_available),
            },
            "waiting": [_patient_summary(p) for p in waiting],
            "in_treatment": [_patient_summary(p) for p in in_treatment],
        }