from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import date

TODAY = date.today().strftime("%Y-%m-%d")
STATUS_ICON = {True: "[DONE]", False: "[    ]"}


def print_schedule(scheduler: Scheduler, title: str = "Today's Schedule") -> None:
    """Print a formatted schedule table to the terminal."""
    tasks = scheduler.sort_by_time()

    print()
    print("=" * 56)
    print(f"  PawPal+ | {title}")
    print(f"  {TODAY}")
    print("=" * 56)

    if not tasks:
        print("  No tasks scheduled for today.")
        print("=" * 56)
        return

    current_pet = None
    for task in tasks:
        if task.pet_name != current_pet:
            current_pet = task.pet_name
            print(f"\n  {current_pet}")
            print("  " + "-" * 52)

        time_part = task.time.split(" ")[1] if " " in task.time else task.time
        status = STATUS_ICON[task.is_completed]
        priority_tag = f"[{task.priority.upper()}]"
        print(f"  {status}  {time_part}  {priority_tag:<8}  {task.description}")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print()
        print("  !! WARNINGS")
        print("  " + "-" * 52)
        for warning in conflicts:
            print(f"  ! {warning}")

    print()
    print("=" * 56)


def print_section(title: str) -> None:
    print(f"\n{'=' * 56}")
    print(f"  {title}")
    print(f"{'=' * 56}")


# ── Setup ──────────────────────────────────────────────
owner = Owner(name="Alex")

max_dog = Pet(name="Max", species="Dog", breed="Labrador", age=3)
luna_cat = Pet(name="Luna", species="Cat", breed="Siamese", age=5)

owner.add_pet(max_dog)
owner.add_pet(luna_cat)

# Tasks added intentionally OUT OF ORDER to prove sort_by_time works
max_dog.add_task(Task("Flea Medication", f"{TODAY} 10:00", 5,  "medium", "weekly", "Max"))
max_dog.add_task(Task("Morning Walk",    f"{TODAY} 07:00", 30, "high",   "daily",  "Max"))
max_dog.add_task(Task("Feeding",         f"{TODAY} 08:00", 10, "high",   "daily",  "Max"))

luna_cat.add_task(Task("Vet Appointment", f"{TODAY} 14:00", 60, "high",  "once",   "Luna"))
luna_cat.add_task(Task("Feeding",         f"{TODAY} 07:30", 10, "high",  "daily",  "Luna"))
luna_cat.add_task(Task("Playtime",        f"{TODAY} 18:00", 20, "low",   "daily",  "Luna"))

# Conflict: two tasks for Max at the same time
max_dog.add_task(Task("Grooming", f"{TODAY} 10:00", 15, "medium", "weekly", "Max"))

scheduler = Scheduler(owner=owner)

# ── 1. Full sorted schedule (includes conflict warning) ─
print_schedule(scheduler, "Today's Schedule (Sorted)")

# ── 2. Filter by pet ────────────────────────────────────
print_section("Filter: Max's tasks only")
for t in scheduler.filter_by_pet("Max"):
    time_part = t.time.split(" ")[1]
    print(f"  {time_part}  [{t.priority.upper()}]  {t.description}")

print_section("Filter: Luna's tasks only")
for t in scheduler.filter_by_pet("Luna"):
    time_part = t.time.split(" ")[1]
    print(f"  {time_part}  [{t.priority.upper()}]  {t.description}")

# ── 3. Mark tasks complete and show filter_by_status ───
print_section("Marking 'Morning Walk' and 'Feeding' (Max) complete...")
max_dog.get_tasks()[1].mark_complete()   # Morning Walk
max_dog.get_tasks()[2].mark_complete()   # Feeding (Max)

print("\n  Pending tasks:")
for t in scheduler.filter_by_status(completed=False):
    print(f"  [ ]  {t.time.split(' ')[1]}  {t.description} ({t.pet_name})")

print("\n  Completed tasks:")
for t in scheduler.filter_by_status(completed=True):
    print(f"  [x]  {t.time.split(' ')[1]}  {t.description} ({t.pet_name})")

# ── 4. Recurring task demo ──────────────────────────────
print_section("Recurring task demo: handle_recurring_tasks()")
before = len(owner.get_all_tasks())
scheduler.handle_recurring_tasks()
after = len(owner.get_all_tasks())
print(f"  Tasks before: {before}  |  Tasks after: {after}")
print(f"  {after - before} new recurring task(s) created for the next occurrence.")

# ── 5. Updated full schedule ────────────────────────────
print_schedule(scheduler, "Updated Schedule")
