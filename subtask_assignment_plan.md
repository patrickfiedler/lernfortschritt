# Task Plan: Subtask-Level Assignment Control

## Goal
Implement granular subtask control: students see only their current subtask, admins can assign specific subtasks to entire classes or individual students.

## Phases
- [x] Phase 1: Research current implementation (student task view, admin assignment logic, database schema)
- [x] Phase 2: Implement database schema changes (add current_subtask_id to student_task)
- [x] Phase 3: Implement student view changes (show only current subtask)
- [x] Phase 4: Implement admin class-level subtask assignment
- [x] Phase 5: Implement admin individual student subtask assignment (lower priority)
- [x] Phase 6: Implementation complete - ready for testing

## Key Questions
1. ✅ How are tasks currently assigned to students? → Via assign_task_to_klasse() or assign_task_to_student(), no subtask control
2. ✅ How are subtasks tracked in the database? → student_subtask table tracks completion (erledigt), linked to student_task_id
3. ✅ What determines the "current" subtask for a student? → Currently none - all subtasks shown
4. ✅ How does the UI currently display subtasks to students? → All subtasks shown in numbered list (templates/student/klasse.html)
5. ✅ Where do admins assign tasks to classes/students? → Class detail page and student detail page

## Decisions Made

### Phase 1: Research Complete
- **Current behavior:** Students see ALL subtasks at once - no filtering
- **Database:** student_task links student to task, student_subtask tracks completion
- **No current subtask concept:** Need to add current_subtask_id to student_task table
- **Assignment flow:** Admin assigns entire task (not specific subtasks)

### Phase 2: Database Design
- Add `current_subtask_id INTEGER` to student_task table
- Foreign key to subtask(id) with ON DELETE SET NULL
- Nullable: NULL means "show all subtasks" (backward compatible)
- Migration: Set current_subtask_id to first incomplete subtask for existing records

### Implementation Approach
1. **Database:** Add current_subtask_id column with migration
2. **Student view:** Filter subtasks if current_subtask_id is set
3. **Auto-advance:** When current subtask completed, advance to next
4. **Admin UI:** Add subtask dropdown to assignment forms
5. **Backward compatible:** NULL current_subtask_id = show all (current behavior)

## Errors Encountered
- None yet

## Status
**ALL PHASES COMPLETE** ✅

Implementation finished and ready for testing. See `subtask_implementation_summary.md` for complete overview.

### Phase 2 Summary: Database Changes
**Files modified:**
- models.py:192-204 - Added current_subtask_id column to student_task table
- models.py:391-435 - Added migrate_add_current_subtask() function
- models.py:1033-1083 - Updated assign_task_to_student() and assign_task_to_klasse() to support subtask_id parameter
- models.py:1112-1201 - Added helper functions: set_current_subtask(), advance_to_next_subtask(), get_current_subtask()
- models.py:1112-1120 - Modified toggle_student_subtask() to auto-advance when subtask completed
- app.py:1375 - Added migrate_add_current_subtask() call in init_app()

**New functions:**
- `migrate_add_current_subtask()` - One-time migration to add column and set defaults
- `set_current_subtask(student_task_id, subtask_id)` - Set current subtask
- `advance_to_next_subtask(student_task_id, current_subtask_id)` - Auto-advance logic
- `get_current_subtask(student_task_id)` - Retrieve current subtask

**Modified functions:**
- `assign_task_to_student()` - Now accepts optional subtask_id parameter
- `assign_task_to_klasse()` - Now accepts optional subtask_id parameter
- `toggle_student_subtask()` - Now calls advance_to_next_subtask() when marking complete

### Phase 3 Summary: Student View Changes
**Files modified:**
- app.py:998-1026 - Modified student_klasse route to filter subtasks based on current_subtask_id
- templates/student/klasse.html:43-109 - Updated subtask display to show current subtask or all subtasks

**Features implemented:**
- Students see only their current subtask (if current_subtask_id is set)
- Completed subtasks shown in collapsible section
- Progress bar reflects all subtasks (not just current)
- Backward compatible: if current_subtask_id is NULL, show all subtasks
- Auto-advance: when current subtask completed, automatically advance to next incomplete subtask

### Phase 4 Summary: Admin Class-Level Subtask Assignment
**Files modified:**
- templates/admin/klasse_detail.html:50-68 - Added subtask selector to task assignment form
- templates/admin/klasse_detail.html:127-163 - Added JavaScript to load subtasks dynamically
- app.py:483-495 - Modified admin_aufgabe_teilaufgaben route to support GET (JSON API)
- app.py:281-294 - Updated admin_klasse_aufgabe_zuweisen to handle subtask_id parameter

**Features implemented:**
- Admin can select specific subtask when assigning task to entire class
- Dynamic subtask dropdown populated via AJAX
- Subtask selection is optional (defaults to "show all")
- Flash message confirms whether subtask was assigned

### Phase 5 Summary: Admin Individual Student Subtask Assignment
**Files modified:**
- templates/admin/schueler_detail.html:74-110 - Added subtask selector to individual task assignment form
- templates/admin/schueler_detail.html:113-148 - Added "Manage Current Subtask" section
- templates/admin/schueler_detail.html:153-189 - Added JavaScript to load subtasks for student
- app.py:299-322 - Modified admin_schueler_detail to fetch student tasks with current subtask info
- app.py:365-379 - Updated admin_schueler_aufgabe_zuweisen to handle subtask_id parameter
- app.py:382-399 - Added admin_schueler_teilaufgabe_setzen route for updating current subtask

**Features implemented:**
- Admin can select specific subtask when assigning task to individual student
- Admin can update current subtask for student's existing task
- UI shows which subtask is currently visible to student
- Subtask selection dropdown shows completion status (✓)
- Can remove filter to show all subtasks again
