import random
from concurrent.futures import ProcessPoolExecutor, as_completed
import app.utils.simulator as sim
from generator import generate_patients

SURGE = [(60, 240)]

def make_datasets(seeds):
    # Generates a realistic cohort count for a 24-hour simulation window
    return [(seed, generate_patients(100, seed, surge_windows=SURGE)) for seed in seeds]

def run_all(datasets, schedule_fn):
    deaths, worst = [], 0
    for seed, patients in datasets:
        r = sim.run_simulation(patients, schedule_fn, seed=seed, surge_windows=SURGE)["summary"]
        deaths.append(r["deaths"])
        max_waits = [v for v in r["max_wait_by_urgency"].values() if v is not None]
        if max_waits:
            worst = max(worst, max(max_waits))
    return sum(deaths) / len(deaths), worst

def evaluate(datasets, wait_bonus, weights, age_bonus):
    old = (sim.WAIT_BONUS, sim.URGENCY_WEIGHT, sim.AGE_BONUS)
    sim.WAIT_BONUS, sim.URGENCY_WEIGHT, sim.AGE_BONUS = wait_bonus, weights, age_bonus
    try:
        return run_all(datasets, sim.priority_schedule)
    finally:
        sim.WAIT_BONUS, sim.URGENCY_WEIGHT, sim.AGE_BONUS = old

def _eval_worker(params, datasets, max_wait_cap):
    i, wait_bonus, weights, age_bonus = params
    deaths, worst = evaluate(datasets, wait_bonus, weights, age_bonus)
    return {
        "trial": i,
        "wait_bonus": wait_bonus,
        "weights": weights,
        "age_bonus": age_bonus,
        "train_deaths": deaths,
        "worst_wait": worst,
        "valid": worst <= max_wait_cap
    }

def tune(n_tries=60, seed=0, max_wait_cap=1440):
    rng = random.Random(seed)
    print("Generating train (30) and test (40) datasets...")
    train = make_datasets(range(0, 30))
    test = make_datasets(range(100, 140))

    # Prepare parameter sets
    tasks = []
    for i in range(1, n_tries + 1):
        wait_bonus = round(rng.uniform(0, 2), 2)
        w = sorted([rng.randint(60, 200), rng.randint(20, 120), rng.randint(5, 60), rng.randint(0, 30)], reverse=True)
        weights = {1: w[0], 2: w[1], 3: w[2], 4: w[3]}
        age_bonus = rng.randint(0, 30)
        tasks.append((i, wait_bonus, weights, age_bonus))

    print(f"Running {n_tries} trials across available CPU cores...")
    best = None
    
    # Run trials in parallel
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(_eval_worker, task, train, max_wait_cap) for task in tasks]
        
        for future in as_completed(futures):
            res = future.result()
            print(f"Trial {res['trial']}/{n_tries} complete | Deaths: {res['train_deaths']:.2f} | Worst Wait: {res['worst_wait']} min | Valid: {res['valid']}")
            
            if res["valid"]:
                if best is None or res["train_deaths"] < best["train_deaths"]:
                    best = res

    if best is None:
        raise RuntimeError("No configurations met the max_wait_cap threshold. Try increasing max_wait_cap.")

    print("\nEvaluating best parameters against test set...")
    current = (sim.WAIT_BONUS, dict(sim.URGENCY_WEIGHT), sim.AGE_BONUS)
    
    report = {
        "best_settings": {
            "wait_bonus": best["wait_bonus"],
            "weights": best["weights"],
            "age_bonus": best["age_bonus"],
            "train_deaths": best["train_deaths"]
        },
        "test_deaths_fcfs": run_all(test, sim.fcfs_schedule)[0],
        "test_deaths_current": evaluate(test, *current)[0],
        "test_deaths_tuned": evaluate(test, best["wait_bonus"], best["weights"], best["age_bonus"])[0],
    }
    return report

if __name__ == "__main__":
    report = tune()
    print("\n=== FINAL REPORT ===")
    for key, value in report.items():
        print(f"{key}: {value}")