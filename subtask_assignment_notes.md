# Subtask Assignment Research Notes

## Current Implementation Analysis

### Database Schema

**student_task table (models.py:192-203):**
- Links: student_id, klasse_id, task_id
- One task per student per class (UNIQUE constraint)
- Tracks completion: abgeschlossen, manuell_abgeschlossen
- **No subtask assignment tracking**

**subtask table (models.py:173-179):**
- Links to task_id
- Has reihenfolge (order) field
- Stores beschreibung (description)

**student_subtask table (models.py:206-214):**
- Links: student_task_id, subtask_id
- Tracks completion: erledigt (0/1)
- UNIQUE(student_task_id, subtask_id)
- **No "current subtask" concept**

### Current Task Assignment Flow

**Class-level assignment (models.py:990-1001):**
- `assign_task_to_klasse(klasse_id, task_id)`
- Creates student_task record for each student in class
- All students get the same task_id
- No subtask specification

**Individual assignment (models.py:980-987):**
- `assign_task_to_student(student_id, klasse_id, task_id)`
- Creates/replaces student_task record
- No subtask specification

### Student View (Current Behavior)

**Dashboard (templates/student/dashboard.html:52-67):**
- Shows all subtasks for the active task
- Progress bar: completed/total subtasks
- No filtering - all subtasks visible

**Task detail page (templates/student/klasse.html:52-68):**
- Renders ALL subtasks in numbered list
- Students see all subtasks at once
- Checkbox for each subtask
- No concept of "current" vs "future" subtasks

### Admin Assignment UI

**Class detail page (app.py:286-288):**
- Form to assign task to entire class
- Only task_id selection, no subtask option

**Student detail page (app.py:347-349):**
- Form to assign task to individual student
- Only klasse_id and task_id, no subtask option

## Design Requirements

### 1. Student View: Show Only Current Subtask
**Goal:** Students see one subtask at a time instead of all subtasks

**Implementation approach:**
- Add `current_subtask_id` field to student_task table
- Default: first incomplete subtask (by reihenfolge)
- Student view filters subtasks to show only current one
- When current subtask is completed, auto-advance to next
- Option: Show completed subtasks in collapsed view

### 2. Admin: Class-Level Subtask Assignment
**Goal:** Assign a specific subtask to all students in a class

**Implementation approach:**
- Add UI to class detail page: select task + subtask
- When assigning, set current_subtask_id for all students
- If students already have the task, update their current_subtask_id
- If students don't have the task, assign task + set current subtask

### 3. Admin: Individual Student Subtask Assignment
**Goal:** Set a specific subtask for individual students

**Implementation approach:**
- Add UI to student detail page: update current subtask
- Dropdown showing subtasks for student's active task
- Update current_subtask_id in student_task

## Database Changes Needed

### Schema Modification

```sql
ALTER TABLE student_task ADD COLUMN current_subtask_id INTEGER;
ALTER TABLE student_task ADD FOREIGN KEY (current_subtask_id) REFERENCES subtask(id) ON DELETE SET NULL;
```

**Migration strategy:**
- Add column (defaults to NULL)
- For existing records, set current_subtask_id to first incomplete subtask
- If all complete, set to last subtask
- If no subtasks, leave NULL

### Model Function Changes

**New functions:**
- `set_current_subtask(student_task_id, subtask_id)` - Update current subtask
- `get_current_subtask(student_task_id)` - Get current subtask for student
- `advance_to_next_subtask(student_task_id)` - Auto-advance logic

**Modified functions:**
- `assign_task_to_klasse()` - Add optional subtask_id parameter
- `assign_task_to_student()` - Add optional subtask_id parameter
- `get_student_subtask_progress()` - Filter by current subtask if enabled

## UI Changes Needed

### Student Views

**templates/student/klasse.html:**
- Add logic to show only current subtask (if set)
- Show "Next subtask" button or auto-advance
- Optional: Show completed subtasks in collapsed section
- Show "X of Y subtasks completed" counter

**templates/student/dashboard.html:**
- Update progress display to reflect current subtask concept

### Admin Views

**templates/admin/klasse_detail.html:**
- Add subtask dropdown to task assignment form
- Show current subtask for each student in class
- Bulk update option: "Set subtask for all students"

**templates/admin/schueler_detail.html:**
- Add "Set current subtask" form
- Show current subtask indicator
- Dropdown filtered by student's active task

## Edge Cases to Handle

1. **No current subtask set:** Fall back to showing all subtasks (current behavior)
2. **Student completes current subtask:** Auto-advance to next incomplete subtask
3. **All subtasks complete:** Show all as completed, don't show "current"
4. **Task has no subtasks:** current_subtask_id stays NULL
5. **Admin changes current subtask backward:** Allow (student might need to redo)
6. **Student not yet started task:** Default to first subtask

## Implementation Priority

1. **High priority:**
   - Database schema change
   - Student view: show only current subtask
   - Admin: class-level subtask assignment

2. **Lower priority:**
   - Admin: individual student subtask assignment
   - Advanced UI features (collapsed view, etc.)
