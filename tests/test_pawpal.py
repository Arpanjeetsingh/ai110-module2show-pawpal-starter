from pawpal_system import Task, Pet


def make_task(description="Morning Walk", time="2026-04-05 07:00"):
    return Task(
        description=description,
        time=time,
        duration_minutes=30,
        priority="high",
        frequency="daily",
        pet_name="Max",
    )


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
