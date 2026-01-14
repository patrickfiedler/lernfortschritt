# Task Plan: Fix Subtask Auto-Advancement Bug

## Goal
Fix the issue where students can mark subtasks as completed (they turn green) but the app doesn't advance to the next incomplete subtask, even though no errors appear in logs.

## Phases
- [x] Phase 1: Reproduce and understand the issue
- [x] Phase 2: Trace the code flow from checkbox toggle to advancement
- [x] Phase 3: Identify why advancement isn't working
- [x] Phase 4: Implement fix
- [ ] Phase 5: Test and verify

## Key Questions
1. Is the checkbox POST request succeeding? → YES
2. Is `_advance_to_next_subtask_internal()` being called? → YES
3. Is there a next subtask to advance to? → Likely yes
4. Is the database being updated but the UI not refreshing? → **YES, THIS IS THE ISSUE**

## Root Cause Found
The database IS being updated correctly. The `current_subtask_id` advances to the next incomplete subtask. However, the JavaScript doesn't reload the page to show the new current subtask. It only:
- Marks the current subtask green (local UI update)
- Updates progress bar
- Reloads if ENTIRE task complete

## Decisions Made
- **Fix approach**: Reload page after successful subtask completion (Option A)
- **Rationale**: Simple, reliable, matches existing task-completion behavior

## Errors Encountered
- None yet (symptom: subtask turns green but doesn't advance)

## Status
**Currently in Phase 5** - User testing the fix (iteration 2)

## Fix Implemented (Iteration 1)
Modified `templates/student/klasse.html` line 285-287:
- Added `else if (checked)` branch to reload page after marking subtask complete
- This ensures the new current_subtask_id is displayed immediately

## Issue with Iteration 1
Checkbox remained checked after reload due to browser form state restoration.

## Fix Implemented (Iteration 2)
Modified `templates/student/klasse.html` to:
- Reload immediately when marking complete using `location.href = location.href` (prevents form state restoration)
- Skip local UI updates when reloading (avoid visual inconsistencies)
- Only update UI locally when unchecking (no reload needed)
