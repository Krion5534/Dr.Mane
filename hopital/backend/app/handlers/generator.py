import random
from app.models.patient import (
    Patient, URGENCY_MIX, TREATMENT_MINUTES, MORTALITY_RANGE,
    NEEDS_BY_URGENCY, ARRIVALS_PER_HOUR, SIM_MINUTES,
    SURGE_CHANCE, SURGE_CHECK_MINUTES, SURGE_DURATION_MINUTES,
    SURGE_ARRIVAL_MULTIPLIER, SURGE_URGENCY_MIX, sample_diagnosis
)


def in_surge(minute, surge_windows):
    return any(start <= minute < end for start, end in surge_windows)


def generate_surge_windows(rng=None, seed=None):
    r = rng if rng is not None else random.Random(seed)

    surges = []
    # roll the dice once per check period, surge starts at a random moment inside it
    for check in range(0, SIM_MINUTES, SURGE_CHECK_MINUTES):
        if r.random() < SURGE_CHANCE:
            start = check + r.randint(0, SURGE_CHECK_MINUTES - 1)
            dur = r.randint(*SURGE_DURATION_MINUTES)
            surges.append((start, min(SIM_MINUTES, start + dur)))
    return surges


def generate_patients(n=1000, seed=42, surge_windows=None):
    rng = random.Random(seed)

    if surge_windows is None:
        surge_windows = generate_surge_windows(rng=rng)

    patients = []
    time = 0.0
    i = 1

    while time < SIM_MINUTES and len(patients) < n:
        # gap to next arrival, faster during a surge
        rate = ARRIVALS_PER_HOUR * (SURGE_ARRIVAL_MULTIPLIER if in_surge(time, surge_windows) else 1)
        time += rng.expovariate(rate / 60.0)
        if time >= SIM_MINUTES:
            break

        surge = in_surge(time, surge_windows)       # status when they actually arrive
        mix = SURGE_URGENCY_MIX if surge else URGENCY_MIX
        urgency = rng.choices(list(mix.keys()), weights=list(mix.values()))[0]

        age = rng.randint(1, 90)
        needs = dict(NEEDS_BY_URGENCY[urgency])
        duration = rng.randint(*TREATMENT_MINUTES[urgency])
        mortality = rng.randint(*MORTALITY_RANGE[urgency])
        diag = sample_diagnosis(age, urgency, rng)

        patients.append(Patient(
            id=i,
            age=age,
            arrival=int(time),
            urgency=urgency,
            needs=needs,
            duration=duration,
            diagnosis=diag,
            during_surge=surge,
            mortality_chance=mortality,
        ))
        i += 1

    return patients


if __name__ == '__main__':
    pts = generate_patients(10, 42)
    print(f"Generated {len(pts)} patients successfully:")
    for p in pts:
        print(p)