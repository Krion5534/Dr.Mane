from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Patient:
    id: int
    age: int
    arrival: int                    # minute the patient arrives
    urgency: int                    # 1-4, with 1 = most urgent
    needs: dict                     # what they need, e.g. {"bed": 1}
    duration: int                   # minutes of treatment
    start: Optional[int] = None     # minute treatment begins (None while waiting)
    end: Optional[int] = None       # minute treatment ends (None until done)

    @property
    def wait(self):
        """Minutes waited. None if treatment not started yet."""
        return None if self.start is None else self.start - self.arrival

    @property
    def arrival_time(self):
        """Arrival as a clock string, e.g. '09:15'."""
        return to_clock(self.arrival)

    @property
    def start_time(self):
        return None if self.start is None else to_clock(self.start)

    @property
    def end_time(self):
        return None if self.end is None else to_clock(self.end)


# ---------------------------------------------------------------- settings
URGENCY_MIX = {1: 0.10, 2: 0.20, 3: 0.40, 4: 0.30}   # share of patients per level (must sum to 1)
URGENCY_WEIGHT = {1: 100, 2: 50, 3: 20, 4: 5}        # starting priority points per level
TREATMENT_MINUTES = {                                # (shortest, longest) treatment time per level
    1: (60, 180),
    2: (45, 120),
    3: (30, 90),
    4: (15, 45),
}

SIM_MINUTES = 1440          # length of one run: 24 hours
SEED = 42                   # same seed = same patients every run
ARRIVALS_PER_HOUR = 6       # average new patients per hour

ALPHA = 0.5                 # priority points per minute waited (0 = urgency only)
AGE_BONUS = 10              # extra priority points for the youngest and oldest patients
CHILD_AGE = 12              # younger than this gets the bonus
ELDERLY_AGE = 65            # this age or older gets the bonus

CAPACITY = {"bed": 6, "icu_bed": 4, "doctor": 8, "nurse": 14}

NEEDS_BY_URGENCY = {
    1: {"icu_bed": 1, "doctor": 1, "nurse": 2},
    2: {"icu_bed": 1, "doctor": 1, "nurse": 2},
    3: {"bed": 1, "doctor": 1, "nurse": 1},
    4: {"bed": 1, "nurse": 1},
}

# ------------------------------------------------------------- clock time
START = datetime(2026, 9, 19, 8, 0)     # simulation minute 0 = 8:00 AM


def to_clock(minute):
    return (START + timedelta(minutes=minute)).strftime("%H:%M")