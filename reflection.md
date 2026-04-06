# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I started with four classes derived from the project scenario:

- **Task** — holds everything about a single care activity: what it is, when it happens, how long it takes, how urgent it is, whether it recurs, and which pet it belongs to. It also owns the two state-changing actions (`mark_complete`, `reschedule`).
- **Pet** — a container for pet identity (name, species, breed, age) and its list of tasks. Provides add/remove/get methods so callers never touch the internal list directly.
- **Owner** — a container for one person's collection of pets. `get_all_tasks()` flattens across all pets so the Scheduler never needs to know how many pets exist.
- **Scheduler** — the "brain." It holds a reference to the Owner and exposes all the algorithmic methods: daily filtering, time sorting, pet/status filtering, conflict detection, and recurring-task creation.

Relationships: `Owner` has many `Pet`s (composition), each `Pet` has many `Task`s (composition), and `Scheduler` references an `Owner` (association).

**b. Design changes**

During implementation I added two methods that were not in the original skeleton:

1. `filter_by_pet(pet_name)` and `filter_by_status(completed)` were added to `Scheduler` after realising the Streamlit UI needed a way to slice the schedule without exposing the raw task list to the view layer. These were not in the initial UML.
2. The `detect_conflicts()` return type changed from `List[Task]` (the skeleton's implied design) to `List[str]`. Returning human-readable warning strings is more useful in both the terminal demo and the Streamlit UI, and it avoids the caller needing to know how to format conflict information.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

- **Time** — `get_daily_schedule()` filters tasks to today's date only, so the owner only sees what is relevant right now.
- **Chronological order** — `sort_by_time()` ensures the displayed list matches the natural flow of a day, making it easy to scan.
- **Conflict** — `detect_conflicts()` catches double-bookings for a single pet at an exact start time, preventing the owner from accidentally committing to two things at once.

Time was the most important constraint because a daily care schedule is fundamentally time-driven. Priority is displayed as a label but does not reorder tasks — the owner decides how to respond to priority information.

**b. Tradeoffs**

The conflict detector only flags tasks with an **exact** start-time match. Two tasks that merely *overlap* — for example, a 60-minute walk starting at 07:00 and a 30-minute grooming starting at 07:30 — are not flagged even though they can't both be performed simultaneously.

This tradeoff is reasonable for this scenario because:
- Most pet care tasks (feeding, medication, a quick walk) are short and sequential, not truly concurrent.
- Duration-overlap detection would require comparing `time + duration_minutes` for every pair, which adds complexity and would generate false positives for tasks a different person could handle in parallel.
- For a single-owner starter app, exact-time conflicts are the most actionable and least ambiguous kind of warning.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used across all phases:

- **Design brainstorming** — asked for a Mermaid.js class diagram based on my verbal description of the four classes and their relationships. The diagram gave me a visual sanity-check before writing any code.
- **Scaffolding** — used Agent Mode to generate the class skeletons (attributes and empty stubs) from the UML, which saved time on boilerplate.
- **Implementation** — used AI to fill in the method bodies, especially `handle_recurring_tasks()` (the `timedelta` arithmetic) and the Streamlit session state pattern in `app.py`.
- **Testing** — asked AI to suggest edge cases for a pet scheduler, which surfaced the "once frequency should not recur" and "no conflict at different times" tests that I might have overlooked.
- **Formatting** — asked AI to suggest a readable terminal output format for `main.py`, which led to the `[DONE]` / `[    ]` status column and the grouped-by-pet layout.

The most useful prompt pattern was: *"Based on #file:pawpal_system.py, implement X. Return only the updated method, not the whole file."* This kept suggestions focused and easy to review.

**b. Judgment and verification**

The original AI suggestion for `detect_conflicts()` returned a list of `Task` objects — the conflicting tasks themselves. I changed this to return `List[str]` (warning messages) because:

1. The Streamlit UI just calls `st.warning(message)` — it can't usefully receive a Task object without extra formatting code.
2. The terminal demo already printed tasks; a second list of the same tasks would confuse the output.
3. Returning strings makes the method self-documenting: the caller knows immediately what to do with the result.

I verified the change by writing `test_detect_conflicts()`, which asserts that the returned string contains both the time and the pet name — confirming the message carries the information a user actually needs.

---

## 4. Testing and Verification

**a. What you tested**

Seven behaviors are covered:

1. `mark_complete()` flips `is_completed` from False to True.
2. `add_task()` increments a pet's task count correctly.
3. `sort_by_time()` returns tasks in chronological order even when added out of order.
4. `handle_recurring_tasks()` creates exactly one new task dated tomorrow for a completed daily task.
5. `detect_conflicts()` returns one warning when two tasks share a pet and start time.
6. `detect_conflicts()` returns no warnings when tasks are at different times.
7. `handle_recurring_tasks()` does nothing for a `"once"` frequency task.

These tests matter because they verify the three promises the app makes to the user: the schedule is in order, recurring tasks are never forgotten, and double-bookings are caught.

**b. Confidence**

**★★★★☆** — I'm confident the core scheduling logic is correct. Edge cases not yet tested:

- A pet with zero tasks (does `sort_by_time()` return an empty list gracefully?).
- Tasks dated in the future (does `get_daily_schedule()` correctly exclude them?).
- Two tasks that overlap in duration but have different start times (known limitation; documented in tradeoffs).
- `remove_task()` and `remove_pet()` — no tests confirm deletion works correctly.

---

## 5. Reflection

**a. What went well**

The CLI-first workflow was the strongest decision in this project. By building and testing `pawpal_system.py` as a standalone module before touching `app.py`, every Streamlit wiring step was straightforward — the functions already worked and the only question was how to connect UI events to them. The tests also caught a return-type mismatch early (the `detect_conflicts` string vs. Task issue) that would have been harder to debug inside Streamlit.

**b. What you would improve**

The `time` attribute is stored as a plain string (`"YYYY-MM-DD HH:MM"`). This works, but it means every method that needs date arithmetic must call `datetime.strptime()` inline. In a next iteration I would store `time` as a `datetime` object internally and only format it as a string for display. This would make `handle_recurring_tasks()` simpler and prevent bugs if a task time is ever stored in a slightly different string format.

**c. Key takeaway**

The most important thing I learned is that **AI is a fast first draft, not a final answer**. In every phase, the AI-generated code was close but needed at least one deliberate change — a return type, a method signature, a formatting decision. The value of AI came from speed: it eliminated the blank-page problem and surfaced options I hadn't considered. But the correctness of those options required me to read the output critically, run the tests, and think about how each piece fit the broader design. The human role in this project was not writing code line by line — it was making judgment calls about what the code should do and why.
