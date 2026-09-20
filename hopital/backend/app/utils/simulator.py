import csv
import json
import random
import threading
import time as time_module
from typing import Optional, Tuple
from app.models.patient import (
    Patient, CAPACITY, STAFFING, SIM_MINUTES, SEED,
    URGENCY_WEIGHT, WAIT_BONUS, AGE_BONUS, CHILD_AGE, ELDERLY_AGE,
    NEEDS_BY_URGENCY, TREATMENT_MINUTES, MORTALITY_RANGE, DOCTOR_COUNT_PEAK,
    DIAGNOSIS_TO_SPECIALTY, DIAGNOSIS_OPTIONS, URGENCY_LABELS,
    period_at, generate_doctors
)
from app.handlers.generator import generate_patients, generate_surge_windows
from app.models.resources import HospitalResourceManager


def admit_patient(
    patient: Patient,
    manager: HospitalResourceManager,
    clock: int,
    allow_fallback: bool = True
) -> Tuple[bool, Optional[int]]:
    """
    Tries to start treatment for one patient.
    Returns (admitted, doctor_id). Nothing changes unless it fully works.
    """
    target_needs = dict(patient.needs)
    is_fallback = False

    if not manager.can_allocate(target_needs):
        # urgent guy, no icu bed -> try a regular bed instead
        if allow_fallback and patient.urgency <= 2 and "icu_bed" in target_needs:
            target_needs = patient.regular_bed_needs()
            if not manager.can_allocate(target_needs):
                return False, None
            is_fallback = True
        else:
            return False, None

    doc_id = None
    if target_needs.get("doctor", 0) > 0:
        doc = manager.get_available_doctor(patient.required_specialty)
        if doc is None:
            return False, None
        doc_id = doc.id

    if is_fallback:
        patient.move_to_regular_bed()       # only after everything is confirmed

    manager.allocate_generic(patient.needs)
    if doc_id is not None:
        manager.assign_doctor(doc_id, patient.id)

    patient.start = clock
    patient.end = clock + patient.duration
    return True, doc_id


def release_patient(patient: Patient, doctor_id: Optional[int], manager: HospitalResourceManager, rng):
    manager.release_generic(patient.needs)
    if doctor_id is not None:
        manager.release_doctor(doctor_id)

    patient.died = rng.randint(1, 100) <= patient.death_chance


def priority_score(patient: Patient, clock: int) -> float:
    score = URGENCY_WEIGHT.get(patient.urgency, 0) + (WAIT_BONUS * (clock - patient.arrival))
    if patient.age <= CHILD_AGE or patient.age >= ELDERLY_AGE:
        score += AGE_BONUS
    return score


def create_manual_patient(name, age, urgency, diagnosis, clock, patient_id, rng) -> Patient:
    """Only name, age, urgency, diagnosis come from the form. rest is auto generated."""
    try:
        age = int(age)              # html dropdowns / inputs send strings
        urgency = int(urgency)
    except (TypeError, ValueError):
        raise ValueError("age and urgency must be whole numbers")
    diagnosis = diagnosis or None   # empty dropdown option = no diagnosis yet
    if urgency not in NEEDS_BY_URGENCY:
        raise ValueError(f"urgency must be one of {list(NEEDS_BY_URGENCY)}")
    if not (0 <= age <= 120):
        raise ValueError("age must be between 0 and 120")
    if diagnosis is not None and diagnosis not in DIAGNOSIS_TO_SPECIALTY:
        raise ValueError(f"unknown diagnosis: {diagnosis}")

    return Patient(
        id=patient_id,
        name=(name or "").strip(),          # empty -> "Patient <id>"
        age=age,
        arrival=clock,
        urgency=urgency,
        needs=dict(NEEDS_BY_URGENCY[urgency]),
        duration=rng.randint(*TREATMENT_MINUTES[urgency]),
        diagnosis=diagnosis,
        mortality_chance=rng.randint(*MORTALITY_RANGE[urgency]),
    )


def load_patients_from_file(path, clock, start_id, rng):
    """bulk load starting patients from csv or json. same fields/validation as manual add.
    csv needs headers: name,age,urgency,diagnosis (diagnosis col can be blank)"""
    if path.endswith(".json"):
        with open(path) as f:
            records = json.load(f)
    elif path.endswith(".csv"):
        with open(path, newline="") as f:
            records = list(csv.DictReader(f))
    else:
        raise ValueError("only .csv or .json import files supported")

    patients = []
    pid = start_id
    for rec in records:
        p = create_manual_patient(
            rec.get("name", ""), rec.get("age"), rec.get("urgency"),
            rec.get("diagnosis"), clock, pid, rng
        )
        patients.append(p)
        pid += 1
    return patients, pid


def get_form_options():
    # what the frontend needs for the dropdowns
    return {
        "urgency": [{"value": k, "label": v} for k, v in URGENCY_LABELS.items()],
        "diagnosis": [{"value": d, "specialty": DIAGNOSIS_TO_SPECIALTY[d]} for d in DIAGNOSIS_OPTIONS],
    }


class HospitalSimulation:
    """One minute per step(), so the frontend can add patients while it runs."""

    def __init__(self, seed=SEED, auto_patients=True, import_path=None):
        self.rng = random.Random(seed)
        self.manager = HospitalResourceManager(CAPACITY, generate_doctors(DOCTOR_COUNT_PEAK, seed=seed))
        self.clock = 0
        self.waiting = []
        self.in_treatment = []      # list of (patient, doctor_id)
        self.finished = []
        self.incoming = []
        self.next_i = 0
        if auto_patients:
            surges = generate_surge_windows(seed=seed)
            self.incoming = sorted(generate_patients(500, seed=seed, surge_windows=surges),
                                   key=lambda p: p.arrival)
        self.next_id = max((p.id for p in self.incoming), default=0) + 1

        if import_path:
            # bulk starting patients from csv/json, dropped straight into the waiting room at t=0
            bulk, self.next_id = load_patients_from_file(import_path, self.clock, self.next_id, self.rng)
            self.waiting.extend(bulk)

        # for the real-time clock, see start()/stop()
        self._lock = threading.RLock()
        self._running = False
        self._thread = None

    def add_manual_patient(self, name, age, urgency, diagnosis=None) -> Patient:
        with self._lock:
            p = create_manual_patient(name, age, urgency, diagnosis, self.clock, self.next_id, self.rng)
            self.next_id += 1
            self.waiting.append(p)      # picked up on the next step
        return p

    def start(self, minute_seconds=1.0):
        """kick off a background thread that calls step() every `minute_seconds` real
        seconds, so the clock keeps moving on its own instead of waiting on manual step() calls.
        runs forever (no SIM_MINUTES cap) since patients now come from manual entry / import,
        not the auto-generator which stops at 1440."""
        if self._running:
            return
        self._running = True

        def loop():
            while self._running:
                with self._lock:
                    self.step()
                time_module.sleep(minute_seconds)

        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def step(self):
        clock = self.clock

        # staff for this time of day
        for r, cap in STAFFING[period_at(clock)].items():
            if r == "doctor":
                self.manager.set_doctors_on_shift(cap)
            else:
                self.manager.set_capacity(r, cap)

        # finished patients leave
        still = []
        for p, doc_id in self.in_treatment:
            if p.end == clock:
                release_patient(p, doc_id, self.manager, self.rng)
                self.finished.append(p)
            else:
                still.append((p, doc_id))
        self.in_treatment = still

        # new arrivals
        while self.next_i < len(self.incoming) and self.incoming[self.next_i].arrival <= clock:
            self.waiting.append(self.incoming[self.next_i])
            self.next_i += 1

        # highest priority first, admit whoever fits
        self.waiting.sort(key=lambda p: priority_score(p, clock), reverse=True)
        for p in list(self.waiting):
            admitted, doc_id = admit_patient(p, self.manager, clock)
            if admitted:
                self.waiting.remove(p)
                self.in_treatment.append((p, doc_id))

        self.clock += 1

    def run(self, until=SIM_MINUTES):
        while self.clock < until:
            self.step()

    def snapshot(self):
        with self._lock:
            return self.manager.snapshot_for_frontend(self.clock, self.waiting, [p for p, _ in self.in_treatment])


def run_manual_step_simulation(seed=SEED):
    sim = HospitalSimulation(seed)
    sim.run()
    return sim.finished, sim.manager


if __name__ == "__main__":
    sim = HospitalSimulation()
    sim.run()
    print(f"treated: {len(sim.finished)} | died: {sum(p.died for p in sim.finished)} | "
          f"still waiting: {len(sim.waiting)} | in treatment: {len(sim.in_treatment)}")