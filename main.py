from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date

TODAY = date.today().strftime("%Y-%m-%d")

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
STATUS_ICON = {True: "[DONE]", False: "[    ]"}


def print_schedule(scheduler: Scheduler, title: str = "Today's Schedule") -> None:
    tasks = scheduler.sort_by_time()

    print()
    print("=" * 52)
    print(f"  PawPal+ | {title}")
    print(f"  {TODAY}")
    print("=" * 52)

    if not tasks:
        print("  No tasks scheduled for today.")
        print("=" * 52)
        return

    current_pet = None
    for task in tasks:
        if task.pet_name != current_pet:
            current_pet = task.pet_name
            print(f"\n  {current_pet}")
            print("  " + "-" * 48)

        time_part = task.time.split(" ")[1] if " " in task.time else task.time
        status = STATUS_ICON[task.is_completed]
        priority_tag = f"[{task.priority.upper()}]"
        print(f"  {status}  {time_part}  {priority_tag:<8}  {task.description}")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print()
        print("  WARNINGS")
        print("  " + "-" * 48)
        for warning in conflicts:
            print(f"  ! {warning}")

    print()
    print("=" * 52)


# ── Setup ──────────────────────────────────────────
owner = Owner(name="Alex")

max_dog = Pet(name="Max", species="Dog", breed="Labrador", age=3)
luna_cat = Pet(name="Luna", species="Cat", breed="Siamese", age=5)

owner.add_pet(max_dog)
owner.add_pet(luna_cat)

# ── Tasks for Max ──────────────────────────────────
max_dog.add_task(Task(
    description="Morning Walk",
    time=f"{TODAY} 07:00",
    duration_minutes=30,
    priority="high",
    frequency="daily",
    pet_name="Max",
))
max_dog.add_task(Task(
    description="Feeding",
    time=f"{TODAY} 08:00",
    duration_minutes=10,
    priority="high",
    frequency="daily",
    pet_name="Max",
))
max_dog.add_task(Task(
    description="Flea Medication",
    time=f"{TODAY} 10:00",
    duration_minutes=5,
    priority="medium",
    frequency="weekly",
    pet_name="Max",
))

# ── Tasks for Luna ─────────────────────────────────
luna_cat.add_task(Task(
    description="Feeding",
    time=f"{TODAY} 07:30",
    duration_minutes=10,
    priority="high",
    frequency="daily",
    pet_name="Luna",
))
luna_cat.add_task(Task(
    description="Vet Appointment",
    time=f"{TODAY} 14:00",
    duration_minutes=60,
    priority="high",
    frequency="once",
    pet_name="Luna",
))
luna_cat.add_task(Task(
    description="Playtime",
    time=f"{TODAY} 18:00",
    duration_minutes=20,
    priority="low",
    frequency="daily",
    pet_name="Luna",
))

# ── Scheduler ──────────────────────────────────────
scheduler = Scheduler(owner=owner)

# Print the initial schedule
print_schedule(scheduler, title="Today's Schedule")

# Mark Max's Morning Walk as complete
morning_walk = max_dog.get_tasks()[0]
morning_walk.mark_complete()

print(f"  Marked '{morning_walk.description}' for {morning_walk.pet_name} as complete.")

# Print the updated schedule
print_schedule(scheduler, title="Updated Schedule")
