# Subtask Assignment Implementation Summary

## Overview
Successfully implemented granular subtask control for the Lernmanager application. Students now see only their current subtask, and admins can assign specific subtasks to entire classes or individual students.

## Key Features Implemented

### 1. Student Experience
- **Focused learning**: Students see only one subtask at a time (if assigned)
- **Progress tracking**: Completed subtasks shown in collapsible "✓ X already completed" section
- **Auto-advancement**: When current subtask is completed, automatically advance to next incomplete subtask
- **Backward compatible**: If no current subtask is set, all subtasks are shown (original behavior)

### 2. Admin Class Management
- **Bulk assignment**: Assign task + specific subtask to entire class at once
- **Dynamic UI**: Subtask dropdown loads via AJAX when task is selected
- **Flexible control**: Can choose to show all subtasks or start with specific one

### 3. Admin Individual Student Management
- **Granular control**: Set specific subtask for individual student
- **Update existing tasks**: Change current subtask for student's active task
- **Visual feedback**: Shows which subtask is currently visible to student
- **Completion status**: Subtask dropdown shows ✓ for completed subtasks

## Database Schema Changes

### New Column: student_task.current_subtask_id
```sql
ALTER TABLE student_task ADD COLUMN current_subtask_id INTEGER;
-- Foreign key to subtask(id) with ON DELETE SET NULL
```

**Migration strategy:**
- Automatically runs on app startup via `migrate_add_current_subtask()`
- Sets current_subtask_id to first incomplete subtask for existing records
- NULL value means "show all subtasks" (backward compatible)

## New Model Functions

### Core Functions
- `set_current_subtask(student_task_id, subtask_id)` - Update current subtask
- `get_current_subtask(student_task_id)` - Retrieve current subtask
- `advance_to_next_subtask(student_task_id, current_subtask_id)` - Auto-advance logic

### Modified Functions
- `assign_task_to_student(student_id, klasse_id, task_id, subtask_id=None)` - Now accepts optional subtask
- `assign_task_to_klasse(klasse_id, task_id, subtask_id=None)` - Now accepts optional subtask
- `toggle_student_subtask(...)` - Triggers auto-advance when subtask completed

## Routes Added/Modified

### New Routes
- `GET /admin/aufgabe/<task_id>/teilaufgaben` - JSON API for fetching subtasks
- `POST /admin/schueler/<student_id>/teilaufgabe-setzen` - Update current subtask for student

### Modified Routes
- `POST /admin/klasse/<klasse_id>/aufgabe-zuweisen` - Now accepts subtask_id parameter
- `POST /admin/schueler/<student_id>/aufgabe-zuweisen` - Now accepts subtask_id parameter
- `GET /admin/schueler/<student_id>` - Now fetches student tasks with current subtask info
- `GET /schueler/klasse/<klasse_id>` - Now filters subtasks based on current_subtask_id

## UI Changes

### Student Views
**templates/student/klasse.html:**
- Shows only current subtask when current_subtask_id is set
- Displays completed subtasks in collapsible <details> element
- Progress bar shows total progress (all subtasks, not just current)
- Backward compatible: shows all subtasks if current_subtask_id is NULL

### Admin Views

**templates/admin/klasse_detail.html:**
- Subtask dropdown in task assignment form
- AJAX loading of subtasks when task is selected
- Optional selection: defaults to "Alle Teilaufgaben zeigen"

**templates/admin/schueler_detail.html:**
- Subtask dropdown in individual task assignment form
- "Manage Current Subtask" section showing student's active tasks
- Visual indicator of which subtask is currently visible
- Update form for changing current subtask

## Testing Checklist

### Phase 6: Testing Tasks

- [ ] **Database Migration**
  - [ ] Run app on fresh database - migration creates column
  - [ ] Run app on existing database - migration runs successfully
  - [ ] Verify existing student_task records get current_subtask_id set

- [ ] **Student View**
  - [ ] Student with current_subtask_id set sees only current subtask
  - [ ] Student with NULL current_subtask_id sees all subtasks
  - [ ] Completed subtasks shown in collapsible section
  - [ ] Progress bar shows correct total progress
  - [ ] Completing current subtask auto-advances to next

- [ ] **Admin Class Assignment**
  - [ ] Task dropdown populates correctly
  - [ ] Selecting task loads subtasks via AJAX
  - [ ] Assigning task without subtask: all students see all subtasks
  - [ ] Assigning task with subtask: all students see only that subtask
  - [ ] Flash message confirms assignment

- [ ] **Admin Individual Assignment**
  - [ ] Task dropdown populates correctly
  - [ ] Selecting task loads subtasks via AJAX
  - [ ] Assigning task without subtask works
  - [ ] Assigning task with subtask works
  - [ ] Flash message confirms assignment

- [ ] **Admin Current Subtask Management**
  - [ ] "Manage Current Subtask" section shows active tasks
  - [ ] Dropdown shows all subtasks with completion status
  - [ ] Updating current subtask works
  - [ ] Setting to "Alle Teilaufgaben zeigen" removes filter
  - [ ] Flash message confirms update

- [ ] **Edge Cases**
  - [ ] Task with no subtasks: current_subtask_id stays NULL
  - [ ] All subtasks completed: doesn't advance further
  - [ ] Admin changes current subtask backward: student sees older subtask
  - [ ] Student completes all subtasks: task marked complete

## Files Modified

### Backend (Python)
- **models.py**: 7 locations modified (schema, migration, assignment functions, helper functions)
- **app.py**: 6 routes modified/added

### Frontend (Templates)
- **templates/student/klasse.html**: Major update to subtask display logic
- **templates/admin/klasse_detail.html**: Added subtask selector + JavaScript
- **templates/admin/schueler_detail.html**: Added subtask selector + management section + JavaScript

### Documentation
- **subtask_assignment_plan.md**: Complete task plan with phase summaries
- **subtask_assignment_notes.md**: Research notes from Phase 1
- **subtask_implementation_summary.md**: This summary document

## Backward Compatibility

All changes are **fully backward compatible**:
- Existing databases migrate automatically
- NULL current_subtask_id = show all subtasks (original behavior)
- Students with no current subtask set experience no change
- Admins can continue assigning tasks without specifying subtasks

## Next Steps

1. **Testing (Phase 6)**: Thoroughly test all features with real data
2. **User feedback**: Deploy to test environment and gather teacher/student feedback
3. **Documentation**: Update CLAUDE.md with new features
4. **Todo cleanup**: Update todo.md to mark this feature as complete
