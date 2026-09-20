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
    during_surge: bool = False      # True if they arrived during an emergency surge
    mortality_chance: int = 0       # 0-100, chance of dying, set from urgency
    downgraded: bool = False        # icu guy who got a regular bed insted
    died: bool = False              # rolled once when treatment ends

    @property
    def wait(self):
        """Minutes waited. None if treatment not started yet."""
        return None if self.start is None else self.start - self.arrival

    def regular_bed_needs(self):
        # same needs but with a normal bed, doesnt change anything
        return {("bed" if r == "icu_bed" else r): n for r, n in self.needs.items()}

    def move_to_regular_bed(self):
        # no icu bed left so they take a normal one, worse odds tho
        self.needs = self.regular_bed_needs()
        self.mortality_chance = min(100, self.mortality_chance + ICU_FALLBACK_MORTALITY_BONUS)
        self.downgraded = True

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

WAIT_BONUS = 0.5                 # priority points per minute waited (0 = urgency only)
AGE_BONUS = 10              # extra priority points for the youngest and oldest patients
CHILD_AGE = 12              # younger than this gets the bonus
ELDERLY_AGE = 65            # this age or older gets the bonus

# ------------------------------------------------- staffing by time of day
STAFFING = {                         # doctors and nurses on duty in each period
    "dead":   {"doctor": 6,  "nurse": 11},
    "normal": {"doctor": 8,  "nurse": 14},
    "peak":   {"doctor": 10, "nurse": 17},
}
PEAK_HOURS = [(9, 13), (17, 21)]     # 09:00-13:00 and 17:00-21:00
DEAD_HOURS = [(0, 6), (22, 24)]      # 22:00-06:00; every other hour is "normal"

# beds are fixed; **STAFFING["normal"] copies in the doctor and nurse numbers
CAPACITY = {"bed": 6, "icu_bed": 4, **STAFFING["normal"]}

NEEDS_BY_URGENCY = {
    1: {"icu_bed": 1, "doctor": 1, "nurse": 2},
    2: {"icu_bed": 1, "doctor": 1, "nurse": 2},
    3: {"bed": 1, "doctor": 1, "nurse": 1},
    4: {"bed": 1, "nurse": 1},
}

# ------------------------------------------------------ emergency surges
SURGE_CHANCE = 0.10                  # chance of a surge in each check period
SURGE_CHECK_MINUTES = 720            # roll the dice once every 12 hours
SURGE_DURATION_MINUTES = (120, 240)  # a surge lasts between 2 and 4 hours
SURGE_ARRIVAL_MULTIPLIER = 1.5       # patients arrive this many times faster (1 = no change)
SURGE_URGENCY_MIX = {1: 0.15, 2: 0.25, 3: 0.35, 4: 0.25}   # levels 1-2 = 40%, up from 30%

# ------------------------------------------------------------- mortality
MORTALITY_RANGE = {                 # (lowest, highest) chance of dying per urgency level
    1: (40, 60),                    # more urgent = way more likly to die
    2: (25, 40),
    3: (10, 20),
    4: (5, 10),
}
ICU_FALLBACK_MORTALITY_BONUS = 20   # icu guy in a normal bed = worse odds

# ------------------------------------------------------------- clock time
START = datetime(2026, 9, 19, 8, 0)     # simulation minute 0 = 8:00 AM


def to_clock(minute):
    """Turn a simulation minute into a clock string, e.g. 75 -> '09:15'."""
    return (START + timedelta(minutes=minute)).strftime("%H:%M")


def period_at(minute):
    """'peak', 'dead' or 'normal' for a simulation minute."""
    hour = (START + timedelta(minutes=minute)).hour
    if any(a <= hour < b for a, b in PEAK_HOURS):
        return "peak"
    if any(a <= hour < b for a, b in DEAD_HOURS):
        return "dead"
    return "normal"