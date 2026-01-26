# Notes: Class-Wide Assignment Bug Investigation

## Assignment Flow

### Individual Assignment (`assign_task_to_student`)
**File:** models.py:1118-1140

1. Gets first subtask if not provided (lines 1129-1134)
2. Inserts into `student_task` with `current_subtask_id` (lines 1137-1140)

### Class Assignment (`assign_task_to_klasse`)
**File:** models.py:1143-1168

1. Gets first subtask if not provided (lines 1153-1158)
2. Gets all students in class (lines 1160-1163)
3. Loops through students and inserts into `student_task` with `current_subtask_id` (lines 1165-1168)

**Both functions appear identical in logic** - they both set `current_subtask_id`.

## Student View Logic

**File:** app.py:1122-1136

The student view checks `task.get('current_subtask_id')`:
- If it exists: Shows only current subtask (lines 1123-1133)
- If None/missing: Shows all subtasks (lines 1134-1136)

The `current_subtask` is fetched via `models.get_current_subtask(task['id'])` (line 1125)

**Query:** models.py:1317-1330
```sql
SELECT sub.*
FROM student_task st
JOIN subtask sub ON st.current_subtask_id = sub.id
WHERE st.id = ?
```

## Hypothesis

The assignment functions look correct. The issue might be:

1. **Null subtask_id**: If a task has NO subtasks, `first_subtask` query returns None, and `current_subtask_id` is set to NULL
2. **Student view expects subtask**: The JOIN in `get_current_subtask` would return NULL if `current_subtask_id` is NULL
3. **Result**: Students see nothing because `current_subtask` is None and `subtasks = []`

## BUG FOUND!

**Location:** app.py:1122-1136 in student class view route

**The Problem:**
When `current_subtask_id` is set but the subtask doesn't exist in database:
1. `task.get('current_subtask_id')` returns a value (line 1123) ✓
2. `get_current_subtask()` performs JOIN and returns None (line 1125)
3. `if current_subtask:` block doesn't execute (line 1126)
4. `subtasks` stays empty `[]`

**Template Rendering:**
- `{% if current_subtask %}` (line 52) - False, skipped
- `{% elif subtasks %}` (line 97) - False (empty list), skipped
- `{% else %}` (line 124) - Shows "Keine Teilaufgaben definiert"

**Root Cause:**
The JOIN in `get_current_subtask()` (models.py:1327) returns NULL when:
- `current_subtask_id` is NULL, OR
- The subtask referenced by `current_subtask_id` doesn't exist

**Why Class Assignments Fail:**
Need to verify if subtasks exist when class-wide assignment happens. If a task has NO subtasks, or if the subtask was deleted after assignment, students see nothing.

## Solution Options

### Option A: Fallback to all subtasks if current doesn't exist
If `current_subtask_id` is set but query returns None, fall back to showing all subtasks.

### Option B: Clear invalid current_subtask_id
If the subtask doesn't exist, set `current_subtask_id` to NULL in database.

### Option C: Defensive assignment
In `assign_task_to_klasse()`, verify subtasks exist before assigning.
