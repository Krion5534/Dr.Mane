import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List


@dataclass
class Doctor:
    id: int
    speciality: str


@dataclass
class Patient:
    id: int
    age: int
    arrival: int
    urgency: int
    needs: dict
    duration: int
    diagnosis: Optional[str] = None
    start: Optional[int] = None
    end: Optional[int] = None
    during_surge: bool = False
    mortality_chance: int = 0
    downgraded: bool = False
    died: bool = False
    name: str = ""      # typed in for manual patients, auto for generated ones

    def __post_init__(self):
        if not self.name:
            self.name = f"Patient {self.id}"

    @property
    def required_specialty(self) -> str:
        # kids always need ped, general doc if diagnosis missing
        if self.age < PEDIATRIC_AGE_LIMIT:
            return "Pediatrician"
        if self.diagnosis is None:
            return "General Doctor"
        return DIAGNOSIS_TO_SPECIALTY.get(self.diagnosis, "General Doctor")

    @property
    def wait(self):
        return None if self.start is None else self.start - self.arrival

    def regular_bed_needs(self):
        return {("bed" if r == "icu_bed" else r): n for r, n in self.needs.items()}

    @property
    def death_chance(self):
        waited = 0 if self.start is None else self.start - self.arrival
        risk_per_min = WAIT_RISK_PER_MINUTE.get(self.urgency, 0.0)
        return min(100, self.mortality_chance + risk_per_min * waited)

    def move_to_regular_bed(self):
        self.needs = self.regular_bed_needs()
        self.mortality_chance = min(100, self.mortality_chance + ICU_FALLBACK_MORTALITY_BONUS)
        self.downgraded = True

    @property
    def arrival_time(self):
        return to_clock(self.arrival)

    @property
    def start_time(self):
        return None if self.start is None else to_clock(self.start)

    @property
    def end_time(self):
        return None if self.end is None else to_clock(self.end)


# ---------------------------------------------------------------- settings
PEDIATRIC_AGE_LIMIT = 16

DIAGNOSIS_POOL = {
    "high_urgency": [
        ("Heart Attack", "Cardiologist"),
        ("Cardiac Arrest", "Cardiologist"),
        ("Stroke", "Neurologist"),
        ("Brain Hemorrhage", "Neurologist"),
    ],
    "low_urgency": [
        ("Fracture", "Orthopedic"),
        ("Joint Dislocation", "Orthopedic"),
        ("Severe Rash", "Dermatologist"),
        ("Skin Infection", "Dermatologist"),
    ],
    "pediatric": [
        ("Pediatric Fever", "Pediatrician"),
        ("Childhood Asthma", "Pediatrician"),
    ]
}

DIAGNOSIS_TO_SPECIALTY = {
    diag: spec
    for category in DIAGNOSIS_POOL.values()
    for diag, spec in category
}

# for the dropdowns in the manual add form
URGENCY_LABELS = {1: "Critical", 2: "High", 3: "Medium", 4: "Low"}
DIAGNOSIS_OPTIONS = list(DIAGNOSIS_TO_SPECIALTY.keys())

URGENCY_MIX = {1: 0.10, 2: 0.20, 3: 0.40, 4: 0.30}
URGENCY_WEIGHT = {1: 100, 2: 50, 3: 20, 4: 5}
TREATMENT_MINUTES = {
    1: (60, 180),
    2: (45, 120),
    3: (30, 90),
    4: (15, 45),
}

SIM_MINUTES = 1440
SEED = 42
ARRIVALS_PER_HOUR = 12

WAIT_BONUS = 0.5
AGE_BONUS = 10
CHILD_AGE = 12
ELDERLY_AGE = 65

WAIT_RISK_PER_MINUTE = {
    1: 0.3,
    2: 0.15,
    3: 0.05,
    4: 0.0,
}

DOCTOR_SPECIALITIES = {
    'General Doctor': 0.4,
    'Pediatrician': 0.2,
    'Orthopedic': 0.2,
    'Neurologist': 0.05,
    'Dermatologist': 0.1,
    'Cardiologist': 0.05
}

DOCTOR_COUNT_NORMAL = 40
DOCTOR_COUNT_PEAK = 60
DOCTOR_COUNT_DEAD = 30

STAFFING = {
    "dead":   {"doctor": DOCTOR_COUNT_DEAD,   "nurse": 20},
    "normal": {"doctor": DOCTOR_COUNT_NORMAL, "nurse": 24},
    "peak":   {"doctor": DOCTOR_COUNT_PEAK,   "nurse": 30},
}
PEAK_HOURS = [(9, 13), (17, 21)]
DEAD_HOURS = [(0, 6), (22, 24)]

CAPACITY = {"bed": 25, "icu_bed": 20, **STAFFING["normal"]}

NEEDS_BY_URGENCY = {
    1: {"icu_bed": 1, "doctor": 1, "nurse": 2},
    2: {"icu_bed": 1, "doctor": 1, "nurse": 2},
    3: {"bed": 1, "doctor": 1, "nurse": 1},
    4: {"bed": 1, "nurse": 1},
}

SURGE_CHANCE = 0.10
SURGE_CHECK_MINUTES = 720
SURGE_DURATION_MINUTES = (120, 240)
SURGE_ARRIVAL_MULTIPLIER = 1.5
SURGE_URGENCY_MIX = {1: 0.15, 2: 0.25, 3: 0.35, 4: 0.25}

MORTALITY_RANGE = {1: (10, 17), 2: (5, 12), 3: (2, 5), 4: (0, 2)}
ICU_FALLBACK_MORTALITY_BONUS = 7

START = datetime(2026, 9, 19, 8, 0)


def to_clock(minute):
    return (START + timedelta(minutes=minute)).strftime("%H:%M")


def period_at(minute):
    hour = (START + timedelta(minutes=minute)).hour
    if any(a <= hour < b for a, b in PEAK_HOURS):
        return "peak"
    if any(a <= hour < b for a, b in DEAD_HOURS):
        return "dead"
    return "normal"


def sample_diagnosis(age: int, urgency: int, rng=None) -> Optional[str]:
    r = rng if rng is not None else random      # pass the seeded rng so runs repeat
    if age < PEDIATRIC_AGE_LIMIT:
        return r.choice([d for d, _ in DIAGNOSIS_POOL["pediatric"]])
    if urgency in (1, 2):
        return r.choice([d for d, _ in DIAGNOSIS_POOL["high_urgency"]])
    elif urgency in (3, 4):
        return r.choice([d for d, _ in DIAGNOSIS_POOL["low_urgency"]])
    return None


def generate_doctors(count: int, seed: Optional[int] = None) -> List[Doctor]:
    rng = random.Random(seed)       # own rng, dont touch the global one
    specs = list(DOCTOR_SPECIALITIES.keys())
    weights = list(DOCTOR_SPECIALITIES.values())
    sampled_specs = rng.choices(specs, weights=weights, k=count)
    return [Doctor(id=i + 1, speciality=spec) for i, spec in enumerate(sampled_specs)]