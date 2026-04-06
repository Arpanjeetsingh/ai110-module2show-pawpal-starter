from typing import List


class Task:
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
        self.time = time
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.frequency = frequency
        self.is_completed = False
        self.pet_name = pet_name

    def mark_complete(self) -> None:
        self.is_completed = True

    def reschedule(self, new_date: str) -> None:
        self.time = new_date


class Pet:
    def __init__(self, name: str, species: str, breed: str, age: int):
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_description: str) -> None:
        self.tasks = [t for t in self.tasks if t.description != task_description]

    def get_tasks(self) -> List[Task]:
        return self.tasks


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_all_tasks(self) -> List[Task]:
        return [task for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_daily_schedule(self) -> List[Task]:
        return self.owner.get_all_tasks()

    def sort_by_time(self) -> List[Task]:
        return sorted(self.get_daily_schedule(), key=lambda t: t.time)

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        return [t for t in self.get_daily_schedule() if t.pet_name == pet_name]

    def filter_by_status(self, completed: bool) -> List[Task]:
        return [t for t in self.get_daily_schedule() if t.is_completed == completed]

    def detect_conflicts(self) -> List[Task]:
        tasks = self.sort_by_time()
        conflicts = []
        for i in range(len(tasks) - 1):
            current = tasks[i]
            next_task = tasks[i + 1]
            if current.time == next_task.time:
                if current not in conflicts:
                    conflicts.append(current)
                conflicts.append(next_task)
        return conflicts

    def handle_recurring_tasks(self) -> None:
        for task in self.get_daily_schedule():
            if task.frequency != "once" and task.is_completed:
                task.is_completed = False
