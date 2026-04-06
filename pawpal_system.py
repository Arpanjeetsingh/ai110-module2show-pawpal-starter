from datetime import date, datetime, timedelta
from typing import List


class Task:
    """Represents a single pet care activity with scheduling metadata."""

    def __init__(
        self,
        description: str,
        time: str,
        duration_minutes: int,
        priority: str,
        frequency: str,
        pet_name: str,
    ):
        self.description = description
        self.time = time              # format: "YYYY-MM-DD HH:MM"
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.frequency = frequency    # "once", "daily", or "weekly"
        self.is_completed = False
        self.pet_name = pet_name

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def reschedule(self, new_date: str) -> None:
        """Update the task's scheduled time to new_date."""
        self.time = new_date


class Pet:
    """Represents a pet and its associated care tasks."""

    def __init__(self, name: str, species: str, breed: str, age: int):
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_description: str) -> None:
        """Remove a task from the list by matching its description."""
        self.tasks = [t for t in self.tasks if t.description != task_description]

    def get_tasks(self) -> List[Task]:
        """Return the full list of tasks for this pet."""
        return self.tasks


class Owner:
    """Represents a pet owner who manages one or more pets."""

    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from the list by matching its name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of every task across all pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    """Organises, filters, and manages tasks for an Owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_daily_schedule(self) -> List[Task]:
        """Return all tasks whose date matches today."""
        today = date.today().strftime("%Y-%m-%d")
        return [t for t in self.owner.get_all_tasks() if t.time.startswith(today)]

    def sort_by_time(self) -> List[Task]:
        """Return today's tasks sorted chronologically by their time attribute."""
        return sorted(self.get_daily_schedule(), key=lambda t: t.time)

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return today's tasks belonging to the specified pet."""
        return [t for t in self.get_daily_schedule() if t.pet_name == pet_name]

    def filter_by_status(self, completed: bool) -> List[Task]:
        """Return today's tasks filtered by completion status."""
        return [t for t in self.get_daily_schedule() if t.is_completed == completed]

    def detect_conflicts(self) -> List[str]:
        """Return warning strings for any two tasks of the same pet at the same time."""
        pet_tasks: dict = {}
        for task in self.get_daily_schedule():
            pet_tasks.setdefault(task.pet_name, []).append(task)

        warnings = []
        for pet_name, tasks in pet_tasks.items():
            for i in range(len(tasks)):
                for j in range(i + 1, len(tasks)):
                    if tasks[i].time == tasks[j].time:
                        warnings.append(
                            f"Conflict: '{tasks[i].description}' and "
                            f"'{tasks[j].description}' for {pet_name} "
                            f"are both scheduled at {tasks[i].time}"
                        )
        return warnings

    def handle_recurring_tasks(self) -> None:
        """For every completed daily/weekly task, create a new task for its next occurrence."""
        pet_lookup = {pet.name: pet for pet in self.owner.pets}

        for task in self.owner.get_all_tasks():
            if not task.is_completed or task.frequency not in ("daily", "weekly"):
                continue

            task_datetime = datetime.strptime(task.time, "%Y-%m-%d %H:%M")
            if task.frequency == "daily":
                next_datetime = task_datetime + timedelta(days=1)
            else:
                next_datetime = task_datetime + timedelta(weeks=1)

            new_task = Task(
                description=task.description,
                time=next_datetime.strftime("%Y-%m-%d %H:%M"),
                duration_minutes=task.duration_minutes,
                priority=task.priority,
                frequency=task.frequency,
                pet_name=task.pet_name,
            )

            pet = pet_lookup.get(task.pet_name)
            if pet:
                pet.add_task(new_task)
