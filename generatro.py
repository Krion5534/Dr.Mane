import random
from patient import Patient, URGENCY_MIX, TREATMENT_MINUTES, ARRIVALS_PER_HOUR, NEEDS_BY_URGENCY


def generate_patients(n, seed):
    """Create n random patients, sorted by arrival time. Same seed = same patients."""
    random.seed(seed)

    urgency_levels = list(URGENCY_MIX.keys())
    urgency_probs = list(URGENCY_MIX.values())

    patients = []
    time = 0.0

    for i in range(1, n + 1):
        age = random.randint(1, 90)
        time += random.expovariate(ARRIVALS_PER_HOUR / 60)
        urgency = random.choices(urgency_levels, weights=urgency_probs)[0]
        low, high = TREATMENT_MINUTES[urgency]
        needs = dict(NEEDS_BY_URGENCY[urgency])     # copy, so patients don't share one dict
        duration = random.randint(low, high)

        patients.append(Patient(
            id=i,
            age=age,
            arrival=int(time),
            urgency=urgency,
            needs=needs,
            duration=duration,
        ))

    return patients


if __name__ == "__main__":      # only runs when you run this file directly, not on import
    for p in generate_patients(5, 42):
        print(p.id, p.arrival_time, "urgency", p.urgency, "age", p.age, p.needs)