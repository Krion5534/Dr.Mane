# MedFlow: Hospital Resource Allocation Simulator

Built for **Hack-a-Matics** by `Big P` (`Shanmukha, Pallav E, Prajwal Sathyaprakash`).

MedFlow simulates one day in a hospital's emergency and critical-care wing. Patients arrive at random, wait in a queue, and are given beds, ICU beds, nurses and a doctor of the right specialty. A priority-based scheduler decides who is treated next when resources run short. The simulation runs one minute at a time, so a live dashboard can watch it, and staff can add patients by hand while it is running.

## Features

- **Minute-by-minute simulation** of a 24-hour day starting at 08:00, with random (Poisson) arrivals, about 12 patients an hour.
- **Patients** have a name, age, urgency level (1 = critical to 4 = low), diagnosis, resource needs, treatment time and a base mortality risk.
- **Resources:** regular beds, ICU beds, nurses, and 60 individually tracked doctors with specialties (General 40%, Pediatrician 20%, Orthopedic 20%, Dermatologist 10%, Neurologist 5%, Cardiologist 5%).
- **Doctor matching:** children (under 16) always need a pediatrician. Otherwise the diagnosis decides the specialty. If no matching specialist is free, a general doctor steps in.
- **All-or-nothing allocation:** a patient starts treatment only if everything they need is available at once, so resources are never double-booked or half-assigned.
- **Priority scheduling:** each waiting patient gets a score of urgency weight + 0.5 points per minute waited + 10 points if age is 12 or under, or 65 or over. The highest score is admitted first. Example: a 70-year-old level 2 patient who has waited 30 minutes scores 50 + 15 + 10 = 75.
- **ICU fallback:** if a level 1 or 2 patient cannot get an ICU bed but a regular bed (with nurses and a doctor) is free, they take the regular bed. This raises their mortality risk by 7 points.
- **Staffing by time of day:** doctors and nurses on shift change between dead hours (22:00-06:00), normal hours, and peak hours (09:00-13:00 and 17:00-21:00). Staff who are busy when their shift ends finish their current patient first, and nobody is removed mid-treatment.
- **Emergency surges:** every 12 hours there is a 10% chance of a surge. It starts at a random moment, lasts 2-4 hours, makes patients arrive 1.5x as fast, and raises the share of urgent (level 1-2) patients from 30% to 40%.
- **Manual patient entry:** staff type a name and age and pick an urgency level and diagnosis from dropdowns. Everything else is generated automatically.
- **Frontend-ready:** `snapshot()` returns a JSON-serializable view of the whole hospital.

## Model at a glance

| Level | Meaning | Share of arrivals (surge) | Priority weight | Treatment time | Needs | Base mortality | Extra risk per minute waited |
|---|---|---|---|---|---|---|---|
| 1 | Critical | 10% (15%) | 100 | 60-180 min | ICU bed, doctor, 2 nurses | 10-17% | 0.3 points |
| 2 | High | 20% (25%) | 50 | 45-120 min | ICU bed, doctor, 2 nurses | 5-12% | 0.15 points |
| 3 | Medium | 40% (35%) | 20 | 30-90 min | bed, doctor, nurse | 2-5% | 0.05 points |
| 4 | Low | 30% (25%) | 5 | 15-45 min | bed, nurse | 0-2% | 0 |

| Resource | Dead hours | Normal | Peak |
|---|---|---|---|
| Regular beds | 25 | 25 | 25 |
| ICU beds | 20 | 20 | 20 |
| Doctors on shift | 30 | 40 | 60 |
| Nurses on shift | 20 | 24 | 30 |

**Mortality.** A patient's death chance is their base risk, plus the extra risk for every minute they waited, plus 7 points if they were moved from an ICU bed to a regular bed (capped at 100). It is rolled once, when treatment ends.

## Project structure

| File | What it does |
|---|---|
| `patient.py` | `Patient` and `Doctor` classes, all settings, clock helpers, diagnosis and doctor sampling |
| `generator.py` | Random patient generation and surge windows |
| `resources.py` | `HospitalResourceManager`: beds, ICU beds, nurses, doctor assignment and shifts, frontend snapshot |
| `simulator.py` | `admit_patient`, `priority_score`, manual patient creation, and the `HospitalSimulation` class |

Requires Python 3.8+ and nothing else (standard library only).

```
python simulator.py     # runs a full day and prints a short summary
python generator.py     # prints 10 generated patients
```

## Using the simulator

```python
from simulator import HospitalSimulation, get_form_options

sim = HospitalSimulation(seed=42)     # auto-generated patients; auto_patients=False starts empty
sim.step()                            # advance one minute (sim.run() runs the whole day)
p = sim.add_manual_patient("Aarav", 8, 1, "Childhood Asthma")   # name, age, urgency, diagnosis
state = sim.snapshot()                # JSON-ready dict
options = get_form_options()          # values for the urgency and diagnosis dropdowns
```

- **Manual patients** arrive at the current minute and join the queue; the scheduler admits them on the next step. Blank names become "Patient <id>". Ages and urgency may be given as strings (as HTML forms send them), and an empty diagnosis means "not yet diagnosed" (a general doctor is assigned). Invalid input raises `ValueError`.
- **`snapshot()`** contains the clock, free beds, ICU beds and nurses, every doctor's status and current patient, the waiting room (with wait times and required specialty) and patients in treatment.
- `admit_patient(patient, manager, clock)` returns `(admitted, doctor_id)` and changes nothing unless the patient can be fully admitted.

## Testing

During development we checked the following with ad-hoc scripts (they are not committed to the repo):

- **Resource accounting:** every simulated minute over 5 days (including manual patients added mid-run), resources in use matched the needs of patients in treatment exactly. No bed, ICU bed or nurse was ever double-booked or leaked.
- **Doctors:** no doctor was ever assigned to two patients, and no off-shift doctor started a new patient.
- **Reproducibility:** the same seed gives identical results.
- **Surges** (3,000 seeds): 19.4% of days had at least one surge, start times covered all 24 hours (not just the window boundaries), and durations stayed within 2-4 hours. Inside a surge, arrivals ran at about 1.5x and 40% of patients were urgent, against 30% outside.
- **Manual entry:** invalid input is rejected, string inputs are accepted, and the snapshot serializes to valid JSON.

## Results from the earlier prototype

These came from an **earlier version of the model** (a single pool of doctors with no specialties, a 30-arrivals-per-hour hospital with 35 doctors and 60 nurses, and slightly different mortality ranges). The comparison scripts were removed when doctors, specialties and diagnoses were added, so **the numbers below cannot be reproduced with the current code**. Treat them as findings about the scheduling idea, not about this exact model.

*Priority scheduling vs. first-come-first-served (FCFS), 24 simulated days per row, expected deaths per day (each patient's death chance summed, so there is no dice-roll noise).* In that version, level 1 patients could take a regular bed immediately and level 2 patients after waiting 120 minutes.

| Hospital load | Level 1 average wait, FCFS to priority | Deaths saved per day, literature-based waiting harm | Deaths saved per day, 4x that harm |
|---|---|---|---|
| Normal (25 beds, 20 ICU) | 21 to 1.4 min | -0.4 +/- 0.05 | +0.8 +/- 0.2 |
| Hot (20 beds, 16 ICU) | 78 to 1.8 min | +0.1 +/- 0.3 | +5.3 +/- 1.6 |
| Very hot (17 beds, 13 ICU) | 217 to 15 min | +1.4 +/- 0.3 (3%) | +13.0 +/- 1.9 (19%) |

(Each day had about 41-48 expected deaths. Plus/minus values are 95% confidence intervals. With the current 0.3-points-per-minute waiting harm, priority scheduling saved roughly 6 deaths a day, about 12%, at normal load.)

What we took from it:

- **Waiting time:** priority scheduling cut level 1 waits by 15 to 100 times at every load.
- **Deaths:** the effect depends on how crowded the hospital is and how harmful waiting is assumed to be (see Limitations). It was small or absent when the hospital was not crowded.
- **Downgrading to a regular bed** costs mortality. In a smaller hospital, level 1 patients benefited from immediate downgrading, but delaying it for level 2 patients reduced expected deaths a little further (31.2 vs 31.5 per day, 60 days), at the cost of longer level 2 waits.
- **Tuning** the priority weights with a random search (60 tries on 30 days, checked on 40 unseen days) found nothing better than the defaults (30.5 vs 30.6 deaths per day).
- **Exact optimization:** choosing the admit set each minute with an integer program (maximize total priority score under resource limits) picked the same patients as the greedy scheduler in 295 of 300 random queue states, at about 200x the run time. So greedy looks close to optimal for this objective.

## Assumptions and limitations

- **All data is synthetic.** No real hospital data was used.
- **Mortality rates are assumptions.** Level 1 base risk (10-17%) is anchored to studies of emergency patients transferred to the ICU (in-hospital mortality of roughly 13-17%). The other levels, the +7 fallback penalty and the treatment times are our estimates.
- **The waiting-harm rate is a placeholder.** The current 0.3 points per minute for level 1 is about 24 times larger than a rough conversion of published delay-mortality studies suggests (around 0.0125 points per minute for ICU-bound patients). The evidence itself is observational and mixed, and one small study found no link. With the larger rate, the death reduction from prioritizing looks bigger than the literature would support. Deaths saved is only as strong as this assumption.
- **The default hospital is lightly loaded.** Over 5 simulated days it ran at about 72% nurse use and about 27% bed and ICU use, with average waits of 1-3 minutes and no ICU fallbacks. Priority scheduling only matters when resources are contended. With 12 beds and 8 ICU beds instead, use rose to about 58-64% and there were about 5 fallbacks a day.
- **Staff are held for a whole treatment,** whereas real doctors and nurses split their time across patients, so the headcounts here are higher than real ratios.
- **Arrivals do not vary by time of day,** even though staffing does, so night shifts are busier relative to staff than in a real hospital.
- **Diagnosis and urgency are independent inputs.** Manual entry accepts, for example, a cardiac diagnosis with low urgency.
- **Not modelled:** operating rooms, multiple departments, a separate diagnosis stage, and a FCFS baseline in the current code.
- **Concurrency:** `HospitalSimulation` is not thread-safe. If the backend adds patients and steps the clock from different threads, guard them with a lock.

## Future work

- Bring back the FCFS baseline and a results summary (waits, utilization, deaths) on the current model.
- A load-aware fallback rule (downgrade only when the ICU queue is long) and an exact optimizer with the ICU-vs-regular-bed choice inside the model.
- Arrival rates that vary by time of day, operating rooms, and multiple departments.

## Sources 

- Chalfin et al., *Critical Care Medicine*, 2007: ICU transfer delays of 6 hours or more were associated with higher mortality (in-hospital mortality 17.4% vs 12.9%).
- A Taiwanese cohort study of mechanically ventilated emergency patients, and a Dutch national ICU registry study, both reported higher mortality with longer emergency-to-ICU waits.
- A national ICU survey in Korea (*Acute and Critical Care*), used as a rough guide to ICU bed share and occupancy.
- El Camino Hospital Records

