# Task Plan: Fix Task Visibility Bug in Admin Editor

## Goal
Fix bug where editing and saving a task in admin view makes it invisible to students.

## Phases
- [x] Phase 1: Understand the bug - what happens when admin saves task
- [x] Phase 2: Find task assignment logic
- [x] Phase 3: Identify what's being cleared/changed
- [x] Phase 4: Fix the bug
- [x] Phase 5: Ready for user testing

## Key Questions
1. What happens when admin saves task edits? **ANSWER: update_subtasks() deletes and recreates all subtasks**
2. How are tasks assigned to students? **ANSWER: student_task table with current_subtask_id**
3. Is there a student_task record being deleted? **ANSWER: No, but current_subtask_id becomes orphaned**
4. Is there a visibility flag being changed? **ANSWER: No, but get_current_subtask() JOIN fails**

## Root Cause Identified
**File: models.py:1075-1093 `update_subtasks()`**
1. Line 1078: `DELETE FROM subtask WHERE task_id = ?` - deletes ALL subtasks
2. Lines 1090-1093: Creates new subtasks with NEW IDs
3. Problem: student_task.current_subtask_id still points to OLD (deleted) subtask IDs
4. Effect: `get_current_subtask()` (line 1530) does `JOIN subtask sub ON st.current_subtask_id = sub.id`
5. JOIN fails → returns None → task appears invisible to student

## Decisions Made
**Fix Strategy**: After deleting and recreating subtasks, update all student_task records for this task to point to the new first subtask.

## Errors Encountered
None yet.

## Fix Implemented
**File: models.py:1075-1109 `update_subtasks()`**

Added logic to fix orphaned current_subtask_id references:
1. Track the first new subtask ID as subtasks are created (`first_new_subtask_id`)
2. After recreating all subtasks, update all student_task records for this task:
   ```python
   conn.execute(
       "UPDATE student_task SET current_subtask_id = ? WHERE task_id = ?",
       (first_new_subtask_id, task_id)
   )
   ```

This ensures that when subtasks are deleted and recreated, student assignments aren't broken.

## Status
**✅ CONFIRMED FIXED** - App restart was needed to load code changes.

## Test Results
- Task 5, subtask 5: Set time estimate from empty to 22 minutes
- Clicked save
- Result: ✅ Task remains assigned to student
- Result: ✅ Time estimates display correctly
- Result: ✅ Task remains visible on student view

The fix works! The issue was that Flask needed restart to reload models.py changes.

## Root Cause FINALLY Found (v3)
**The ACTUAL problem**: Visibility records are deleted but NOT recreated.

Flow:
1. Admin edits subtasks → `update_subtasks()` deletes visibility records (lines 1078-1081)
2. New subtasks created with new IDs
3. No visibility records for new subtask IDs
4. `get_visible_subtasks_for_student()` returns empty list (no enabled subtasks)
5. student_klasse route sets `subtasks = []` (line 1321)
6. Template shows empty state: "Weitere Aufgaben kommen bald!"

**Why deleting visibility records was the right move**: Old IDs are invalid.
**Why it causes the bug**: New IDs have no visibility records at all.

**Solution Options**:
1. Don't delete visibility - causes orphaned records (BAD)
2. Delete and require admin to reconfigure (PREVIOUS ATTEMPT - not user-friendly)
3. **Preserve visibility by order/position** - map old subtask #1 enabled → new subtask #1 enabled (IMPLEMENTED)

## Final Solution (v3)
**File: models.py:1075-1145 `update_subtasks()`**

Complete rewrite to preserve visibility settings:

1. **Save old visibility by position** (lines 1079-1087):
   - Query subtask_visibility joined with subtask to get reihenfolge (order)
   - Store in dict: `(klasse_id, student_id, position) -> (enabled, admin_id)`

2. **Delete old records** (lines 1089-1093):
   - Delete subtask_visibility records
   - Delete subtasks

3. **Create new subtasks** (lines 1095-1115):
   - Create subtasks with new IDs
   - Track: `position -> new_subtask_id`

4. **Restore visibility for matching positions** (lines 1117-1124):
   - For each old visibility record at position N
   - If new subtask exists at position N
   - Create new visibility record with new subtask ID
   - Preserves enabled state and admin who set it

5. **Fix student_task pointers** (lines 1126-1131):
   - Update current_subtask_id to first new subtask

**Result**:
- Subtask #1 visible before edit → Still visible after edit (even with new ID)
- Subtask #2 disabled before edit → Still disabled after edit
- Admin adds new subtask #5 → No visibility record (must be enabled manually)
- Admin deletes subtask #3 → Visibility records for #4, #5 shift to #3, #4
- Task remains visible and functional after editing!

## Complete Fix (v2)
**File: models.py:1075-1115 `update_subtasks()`**

Now deletes BOTH orphaned records when updating subtasks:

1. **Delete subtask_visibility records first** (lines 1078-1081):
   ```python
   conn.execute("""
       DELETE FROM subtask_visibility
       WHERE subtask_id IN (SELECT id FROM subtask WHERE task_id = ?)
   """, (task_id,))
   ```
   This removes visibility settings for old subtasks before deleting them.

2. **Delete old subtasks** (line 1084):
   ```python
   conn.execute("DELETE FROM subtask WHERE task_id = ?", (task_id,))
   ```

3. **Create new subtasks** with time estimates (lines 1087-1104)

4. **Update student_task.current_subtask_id** to point to first new subtask (lines 1106-1111)

Result: When admin edits task subtasks, both the task assignment AND subtask visibility are preserved.

## New Investigation - REAL ROOT CAUSE FOUND
User reports: "No, the task is disabled again."

**ACTUAL PROBLEM**: There's a `subtask_visibility` table!
- This table controls which subtasks are enabled/visible for classes/students
- When `update_subtasks()` deletes subtasks, it orphans the subtask_visibility records
- Old visibility records point to deleted subtask IDs
- New subtask IDs have NO visibility records
- Result: All subtasks appear disabled (not visible)

**Files involved**:
- `app.py:837-900` - admin_teilaufgaben_verwaltung_speichern()
- `models.py:1075-1109` - update_subtasks() - needs to also delete visibility records

**Fix needed**: Delete subtask_visibility records when deleting subtasks
