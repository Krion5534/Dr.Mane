import copy
import random
from patient import URGENCY_WEIGHT, WAIT_BONUS, AGE_BONUS, CHILD_AGE, ELDERLY_AGE, CAPACITY, STAFFING, SIM_MINUTES, period_at, to_clock
from generator import generate_patients, in_surge
from resources import ResourcePool
from patient import Patient

def priority_score(patient, clock):
    score = URGENCY_WEIGHT[patient.urgency]
    score += WAIT_BONUS*(clock - patient.arrival)
    if patient.age < CHILD_AGE or patient.age >= ELDERLY_AGE:
        score += AGE_BONUS

    return score

def priority_schedule(waiting, pool, clock):
    ordered = sorted(waiting, key=lambda p: priority_score(p, clock), reverse=True)
    admitted = []
    for p in ordered:
        if pool.can_allocate(p.needs):
            pool.allocate(p.needs)
            admitted.append(p)
        elif p.urgency <= 2 and pool.can_allocate(p.regular_bed_needs()):
            p.move_to_regular_bed()
            pool.allocate(p.needs)
            admitted.append(p)
    return admitted


def fcfs_schedule(waiting, pool, clock):
    # baseline, first come first served
    admitted = []
    for p in sorted(waiting, key=lambda p: p.arrival):
        if pool.can_allocate(p.needs):
            pool.allocate(p.needs)
            admitted.append(p)
    return admitted


def run_simulation(patients, schedule_fn, seed=0, surge_windows=None):
    patients = copy.deepcopy(patients)      # fresh copy so runs dont mess w each other
    surge_windows = surge_windows or []

    rng = random.Random(seed)               # death luck rolled once, same for every strategy
    luck = {p.id: rng.randint(30, 100) for p in patients}

    pool = ResourcePool(CAPACITY)
    incoming = sorted(patients, key=lambda p: p.arrival)
    next_i = 0
    waiting, in_treatment, finished, timeline = [], [], [], []

    for clock in range(SIM_MINUTES):
        period = period_at(clock)           # staff for this time of day
        for r, cap in STAFFING[period].items():
            pool.set_capacity(r, cap)

        for p in [p for p in in_treatment if p.end == clock]:   # done guys leave
            pool.release(p.needs)
            p.died = luck[p.id] <= p.death_chance
            in_treatment.remove(p)
            finished.append(p)

        while next_i < len(incoming) and incoming[next_i].arrival <= clock:   # new arrivals
            waiting.append(incoming[next_i])
            next_i += 1

        for p in schedule_fn(waiting, pool, clock):     # scheduler picks who starts
            p.start = clock
            p.end = clock + p.duration
            waiting.remove(p)
            in_treatment.append(p)

        assert pool.free["bed"] >= 0 and pool.free["icu_bed"] >= 0   # beds cant go negative

        timeline.append({                   # snapshot for charts
            "minute": clock,
            "time": to_clock(clock),
            "period": period,
            "surge": in_surge(clock, surge_windows),
            "queue_len": len(waiting),
            "capacity": dict(pool.capacity),
            "in_use": {r: pool.capacity[r] - pool.free[r] for r in pool.capacity},
        })

    return {
        "summary": summarize(patients, finished, waiting, in_treatment, timeline),
        "timeline": timeline,
        "patients": patients,
    }


def summarize(patients, finished, waiting, in_treatment, timeline):
    waits = {u: [] for u in URGENCY_WEIGHT}
    for p in patients:
        # never started = waited till end of day
        w = (p.start - p.arrival) if p.start is not None else (SIM_MINUTES - p.arrival)
        waits[p.urgency].append(w)

    util = {}                               # utilzation = used / available
    for r in CAPACITY:
        used = sum(min(t["in_use"][r], t["capacity"][r]) for t in timeline)
        total = sum(t["capacity"][r] for t in timeline)
        util[r] = round(used / total, 2)

    return {
        "patients": len(patients),
        "completed": len(finished),
        "in_treatment_at_end": len(in_treatment),
        "still_waiting": len(waiting),
        "deaths": sum(p.died for p in finished),
        "downgraded_to_regular_bed": sum(p.downgraded for p in patients),
        "avg_wait_by_urgency": {u: round(sum(v) / len(v), 1) if v else None for u, v in waits.items()},
        "max_wait_by_urgency": {u: max(v) if v else None for u, v in waits.items()},
        "utilization": util,
        "peak_queue": max(t["queue_len"] for t in timeline),
    }


if __name__ == "__main__":
    SURGE = [(60, 240)]                     # surge 09:00-12:00
    patients = generate_patients(1000, 408, surge_windows=SURGE)

    strategies = {"fcfs": fcfs_schedule, "priority": priority_schedule}

    for name, fn in strategies.items():
        result = run_simulation(patients, fn, surge_windows=SURGE)
        print(f"\n=== {name} ===")
        for key, value in result["summary"].items():
            print(f"{key}: {value}")