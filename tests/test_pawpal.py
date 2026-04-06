from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler

TODAY = date.today().strftime("%Y-%m-%d")
TOMORROW = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")


# ── Shared helpers ─────────────────────────────────────────────────────────

def make_task(description="Morning Walk", time=None, frequency="daily", pet_name="Max"):
    return Task(
        description=description,
        time=time or f"{TODAY} 07:00",
        duration_minutes=30,
        priority="high",
        frequency=frequency,
        pet_name=pet_name,
    )


def make_scheduler_with_tasks(tasks: list[Task]) -> tuple[Scheduler, Pet]:
    """Return a Scheduler and the Pet that owns all the given tasks."""
    owner = Owner(name="Alex")
    pet = Pet(name="Max", species="Dog", breed="Labrador", age=3)
    owner.add_pet(pet)
    for t in tasks:
        pet.add_task(t)
    return Scheduler(owner=owner), pet


# ── Phase 2 tests ──────────────────────────────────────────────────────────

def test_mark_complete():
    task = make_task()
    assert task.is_completed is False
    task.mark_complete()
    assert task.is_completed is True


def test_add_task_to_pet():
    pet = Pet(name="Max", species="Dog", breed="Labrador", age=3)
    assert len(pet.get_tasks()) == 0

    pet.add_task(make_task("Morning Walk"))
    assert len(pet.get_tasks()) == 1

    pet.add_task(make_task("Feeding"))
    assert len(pet.get_tasks()) == 2


# ── Phase 5 tests ──────────────────────────────────────────────────────────

def test_sort_by_time():
    """Tasks added out of order must come back in chronological order."""
    tasks = [
        make_task("Flea Medication", f"{TODAY} 10:00"),
        make_task("Morning Walk",    f"{TODAY} 07:00"),
        make_task("Feeding",         f"{TODAY} 08:00"),
    ]
    scheduler, _ = make_scheduler_with_tasks(tasks)

    sorted_tasks = scheduler.sort_by_time()
    times = [t.time.split(" ")[1] for t in sorted_tasks]
    assert times == ["07:00", "08:00", "10:00"]


def test_recurring_task_creates_new_task():
    """Completing a daily task and calling handle_recurring_tasks() must
    create exactly one new task scheduled for the following day."""
    task = make_task("Morning Walk", f"{TODAY} 07:00", frequency="daily")
    scheduler, pet = make_scheduler_with_tasks([task])

    task.mark_complete()
    before = len(pet.get_tasks())
    scheduler.handle_recurring_tasks()
    after = len(pet.get_tasks())

    assert after == before + 1
    new_task = pet.get_tasks()[-1]
    assert new_task.time.startswith(TOMORROW)
    assert new_task.description == "Morning Walk"
    assert new_task.is_completed is False


def test_detect_conflicts():
    """Two tasks for the same pet at the same time must trigger a warning."""
    tasks = [
        make_task("Morning Walk", f"{TODAY} 08:00"),
        make_task("Grooming",     f"{TODAY} 08:00"),
    ]
    scheduler, _ = make_scheduler_with_tasks(tasks)

    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Max" in warnings[0]


def test_no_conflict_different_times():
    """Tasks at different times must not raise any conflict warnings."""
    tasks = [
        make_task("Morning Walk", f"{TODAY} 07:00"),
        make_task("Feeding",      f"{TODAY} 08:00"),
    ]
    scheduler, _ = make_scheduler_with_tasks(tasks)
    assert scheduler.detect_conflicts() == []


def test_once_task_not_recurred():
    """A 'once' frequency task must NOT generate a follow-up task."""
    task = make_task("Vet Appointment", f"{TODAY} 14:00", frequency="once")
    scheduler, pet = make_scheduler_with_tasks([task])

    task.mark_complete()
    before = len(pet.get_tasks())
    scheduler.handle_recurring_tasks()
    assert len(pet.get_tasks()) == before
