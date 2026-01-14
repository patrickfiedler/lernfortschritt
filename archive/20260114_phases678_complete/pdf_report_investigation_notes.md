# Investigation Notes: Database Schema and Model Functions

## Database Schema Investigation

### Actual Table Schemas

**klasse table:**
```
id INTEGER PRIMARY KEY
name TEXT NOT NULL
```
- ❌ NO stufe column
- ❌ NO subject column
- ✅ Only id and name

**task table:**
```
id, name, beschreibung, lernziel, fach, stufe, kategorie, quiz_json, number
```
- ✅ HAS fach and stufe (on task, not klasse!)
- ✅ HAS 'number' field (NOT 'order_num')

**student_task table:**
```
id, student_id, klasse_id, task_id, abgeschlossen, manuell_abgeschlossen
```
- ❌ NO completed_subtasks column
- ❌ NO total_subtasks column
- ❌ NO quiz_passed column
- ❌ NO is_completed column
- ✅ Only has 'abgeschlossen' (0/1 boolean)

**subtask table:**
```
id, task_id, beschreibung, reihenfolge
```

**student_subtask table:**
```
id, student_task_id, subtask_id, erledigt
```
- This is the JOIN table to track which subtasks are done

**quiz_attempt table:**
```
id, student_task_id, punkte, max_punkte, bestanden, antworten_json, timestamp
```

**student table:**
```
id, nachname, vorname, username, password_hash
```

## Existing Model Functions

### Functions That Compute Progress

**`get_students_in_klasse(klasse_id)`** - Line 656
- Returns: Basic student info + task_name + abgeschlossen flag
- Does NOT compute subtask progress
- SQL: Joins student, student_klasse, student_task, task
- Returns: `{id, nachname, vorname, username, task_id, task_name, abgeschlossen, manuell_abgeschlossen}`

**`get_student_task(student_id, klasse_id)`** - Line 1004
- Returns: Full student_task info + task details
- Does NOT compute subtask counts
- SQL: Joins student_task with task
- Returns: `{st.*, name, beschreibung, lernziel, fach, stufe, kategorie, quiz_json}`
- Key fields: `id` (student_task_id), `task_id`, `abgeschlossen`

**`get_student_subtask_progress(student_task_id)`** - Line 1016
- Returns: List of ALL subtasks with completion status
- SQL: Joins subtask with student_subtask
- Returns: `[{subtask.*, erledigt}]`
- This is what you COUNT to get completed_subtasks / total_subtasks

**`get_quiz_attempts(student_task_id)`** - Needs to be found
- Should return quiz attempts with 'bestanden' field

### How Progress Is Actually Computed

**In templates (app.py routes):**
```python
# Example from student_klasse route (line ~962):
task = models.get_student_task(student_id, klasse_id)
subtasks = models.get_student_subtask_progress(task['id'])  # <- student_task_id
# Then count:
task['total_subtasks'] = len(subtasks)
task['completed_subtasks'] = sum(1 for s in subtasks if s['erledigt'])
```

**Quiz pass status:**
```python
quiz_attempts = models.get_quiz_attempts(task['id'])
# Check if latest attempt has 'bestanden' = 1
```

## Report Function Analysis

### Functions with SQL Errors

**❌ `get_report_data_for_class()` - Line 1663**
- Error 1: Queries `klasse.stufe, klasse.subject` (don't exist)
- Error 2: Uses `current_task['task_name']` but get_student_task() returns `name`
- Error 3: Uses `current_task['task_order']` but should use `number`
- Error 4: Tries to get `completed_subtasks` from student dict but not computed

**❌ `get_report_data_for_student()` - Line 1720**
- Error 1: Queries `klasse.stufe, klasse.subject` (don't exist)
- Error 2: Uses old WHERE clause with stufe/subject matching
- Error 3: Queries `st.completed_subtasks, st.total_subtasks` (don't exist)
- Error 4: Queries `t.order_num` (should be `t.number`)

**✅ `generate_class_report_pdf()` - utils.py**
- Expects data structure with computed fields
- If we fix the data functions, PDF generation should work

**✅ `generate_student_report_pdf()` - utils.py**
- Same as above

## Fix Strategy

### Phase 1: Fix `get_report_data_for_class()`

**Current broken code:**
```python
klasse = SELECT name, stufe, subject FROM klasse  # ❌ stufe/subject don't exist
current_task = get_student_task()  # Returns wrong field names
student_data uses: current_task['task_name'], current_task['task_order']  # ❌ Wrong keys
```

**Fixed approach:**
```python
klasse = SELECT id, name FROM klasse  # ✅ Only fields that exist
current_task = get_student_task(student['id'], klasse_id)
if current_task:
    # Get subtask progress
    subtasks = get_student_subtask_progress(current_task['id'])
    completed = sum(1 for s in subtasks if s['erledigt'])
    total = len(subtasks)

    # Get quiz status
    quiz_attempts = get_quiz_attempts(current_task['id'])
    quiz_passed = bool(quiz_attempts and quiz_attempts[-1]['bestanden'])

    task_name = current_task['name']  # ✅ Correct key
else:
    task_name = 'Keine Aufgabe'
    completed = total = 0
    quiz_passed = False
```

### Phase 2: Fix `get_report_data_for_student()`

**Current broken code:**
```python
klassen = SELECT k.name, k.stufe, k.subject  # ❌ stufe/subject don't exist
task = SELECT ... WHERE name=? AND stufe=? AND subject=?  # ❌ Bad WHERE
task = SELECT t.order_num, st.completed_subtasks  # ❌ Wrong fields
```

**Fixed approach:**
```python
klassen = SELECT k.id, k.name FROM klasse  # ✅ Only fields that exist
for klasse in klassen:
    task = get_student_task(student_id, klasse['id'])  # ✅ Use existing function
    if task:
        subtasks = get_student_subtask_progress(task['id'])
        completed = sum(1 for s in subtasks if s['erledigt'])
        total = len(subtasks)
        quiz_attempts = get_quiz_attempts(task['id'])
        quiz_passed = bool(quiz_attempts and quiz_attempts[-1]['bestanden'])
```

### Phase 3: Update PDF Functions

**No changes needed** - they expect the data structure we'll provide.

### Phase 4: Test Each Report Type

1. Class report with real data
2. Student summary report
3. Student complete report
4. Student self-report
