from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler
import streamlit as st

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

TODAY = date.today().strftime("%Y-%m-%d")

# ── Session state bootstrap ────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None


# ── Helpers ────────────────────────────────────────────────────────────────
def get_pet_names() -> list[str]:
    if st.session_state.owner is None:
        return []
    return [p.name for p in st.session_state.owner.pets]


def find_pet(name: str) -> Pet | None:
    if st.session_state.owner is None:
        return None
    for pet in st.session_state.owner.pets:
        if pet.name == name:
            return pet
    return None


# ── Header ─────────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption(f"Today: {TODAY}")
st.divider()


# ── Section 1: Owner setup ─────────────────────────────────────────────────
st.subheader("1. Owner")

owner_name = st.text_input("Owner name", value="Alex")

if st.button("Set Owner"):
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
    st.success(f"Owner set to **{owner_name}**.")

if st.session_state.owner:
    st.info(f"Current owner: **{st.session_state.owner.name}**")

st.divider()


# ── Section 2: Add a pet ───────────────────────────────────────────────────
st.subheader("2. Add a Pet")

if st.session_state.owner is None:
    st.warning("Set an owner first.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_pet_name = st.text_input("Pet name", value="Max")
    with col2:
        species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"])
    with col3:
        breed = st.text_input("Breed", value="Labrador")
    with col4:
        age = st.number_input("Age", min_value=0, max_value=30, value=3)

    if st.button("Add Pet"):
        if new_pet_name.strip() == "":
            st.error("Pet name cannot be empty.")
        elif new_pet_name in get_pet_names():
            st.error(f"A pet named **{new_pet_name}** already exists.")
        else:
            pet = Pet(name=new_pet_name, species=species, breed=breed, age=int(age))
            st.session_state.owner.add_pet(pet)
            st.success(f"Added **{new_pet_name}** the {species}.")

    if get_pet_names():
        st.write("**Pets:**", ", ".join(get_pet_names()))

st.divider()


# ── Section 3: Add a task ──────────────────────────────────────────────────
st.subheader("3. Add a Task")

if not get_pet_names():
    st.warning("Add at least one pet first.")
else:
    col1, col2 = st.columns(2)
    with col1:
        task_pet = st.selectbox("Assign to pet", get_pet_names())
        task_title = st.text_input("Task title", value="Morning Walk")
        task_time = st.time_input("Time", value=None)
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add Task"):
        if task_title.strip() == "":
            st.error("Task title cannot be empty.")
        elif task_time is None:
            st.error("Please pick a time.")
        else:
            time_str = f"{TODAY} {task_time.strftime('%H:%M')}"
            task = Task(
                description=task_title,
                time=time_str,
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
                pet_name=task_pet,
            )
            pet = find_pet(task_pet)
            pet.add_task(task)
            st.success(f"Added **{task_title}** to {task_pet} at {task_time.strftime('%H:%M')}.")

st.divider()


# ── Section 4: Schedule ────────────────────────────────────────────────────
st.subheader("4. Today's Schedule")

if st.session_state.scheduler is None:
    st.warning("Set an owner to activate the scheduler.")
else:
    scheduler: Scheduler = st.session_state.scheduler
    sorted_tasks = scheduler.sort_by_time()

    if not sorted_tasks:
        st.info("No tasks scheduled for today. Add some tasks above.")
    else:
        # Build display table
        for task in sorted_tasks:
            time_display = task.time.split(" ")[1] if " " in task.time else task.time
            status_icon = "✅" if task.is_completed else "🔲"
            priority_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "")

            col1, col2, col3, col4 = st.columns([1, 2, 4, 2])
            with col1:
                st.write(status_icon)
            with col2:
                st.write(f"**{time_display}**")
            with col3:
                st.write(f"{priority_badge} {task.description} *(for {task.pet_name})*")
            with col4:
                btn_key = f"complete_{task.pet_name}_{task.description}_{task.time}"
                if not task.is_completed:
                    if st.button("Mark done", key=btn_key):
                        task.mark_complete()
                        st.rerun()
                else:
                    st.caption("Done")

        # Conflicts
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.divider()
            st.error("**Scheduling Conflicts Detected**")
            for warning in conflicts:
                st.warning(warning)

    # Stats
    all_tasks = scheduler.get_daily_schedule()
    if all_tasks:
        done = sum(1 for t in all_tasks if t.is_completed)
        st.divider()
        st.progress(done / len(all_tasks), text=f"{done} / {len(all_tasks)} tasks completed today")
