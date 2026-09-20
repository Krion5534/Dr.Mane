import random
from app.models.patient import (Patient, URGENCY_MIX, SURGE_URGENCY_MIX, TREATMENT_MINUTES,
                     ARRIVALS_PER_HOUR, SURGE_ARRIVAL_MULTIPLIER, SURGE_CHANCE,
                     SURGE_CHECK_MINUTES, SURGE_DURATION_MINUTES, SIM_MINUTES,
                     NEEDS_BY_URGENCY, MORTALITY_RANGE)


def in_surge(minute, surge_windows):
    """True if this minute falls inside any (start, end) surge window."""
    return any(start <= minute < end for start, end in surge_windows)


def generate_patients(n, seed, surge_windows=None):
    """Create up to n random patients, stopping at the end of the simulation.
    Same seed = same patients.
    surge_windows: optional list of (start_minute, end_minute) to force surges,
    e.g. [(60, 240)] = 09:00-12:00. Leave as None to let chance decide."""
    random.seed(seed)

    if surge_windows is None:
        surge_windows = []
        for period_start in range(0, SIM_MINUTES, SURGE_CHECK_MINUTES):
            if random.random() < SURGE_CHANCE:                       # 10% roll for this period
                start = period_start + random.randint(0, SURGE_CHECK_MINUTES - 1)
                length = random.randint(*SURGE_DURATION_MINUTES)
                surge_windows.append((start, start + length))

    patients = []
    time = 0.0

    for i in range(1, n + 1):
        # gap until the next arrival (shorter during a surge)
        rate = ARRIVALS_PER_HOUR * (SURGE_ARRIVAL_MULTIPLIER if in_surge(time, surge_windows) else 1)
        time += random.expovariate(rate / 60)
        if time >= SIM_MINUTES:
            break

        surge = in_surge(time, surge_windows)      # surge status when this patient arrives
        mix = SURGE_URGENCY_MIX if surge else URGENCY_MIX

        age = random.randint(1, 90)
        urgency = random.choices(list(mix.keys()), weights=list(mix.values()))[0]
        low, high = TREATMENT_MINUTES[urgency]
        needs = dict(NEEDS_BY_URGENCY[urgency])     # copy, so patients don't share one dict
        duration = random.randint(low, high)
        mortality = random.randint(*MORTALITY_RANGE[urgency])   # risk depends on urgency

        patients.append(Patient(
            id=i,
            age=age,
            arrival=int(time),
            urgency=urgency,
            needs=needs,
            duration=duration,
            during_surge=surge,
            mortality_chance=mortality,
        ))

    return patients


if __name__ == "__main__":      # only runs when you run this file directly, not on import
    ps = generate_patients(1000, 42, surge_windows=[(60, 240)])   # forced surge 09:00-12:00
    print(len(ps), "patients,", sum(p.during_surge for p in ps), "during the surge")
    for p in ps[:5]:
        print(p.id, p.arrival_time, "urgency", p.urgency, "age", p.age, p.needs)