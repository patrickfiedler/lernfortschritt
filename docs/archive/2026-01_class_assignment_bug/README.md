# Class Assignment Bug Fix (January 2026)

## Summary
Fixed bug where students saw "Keine Teilaufgaben definiert" after class-wide task assignment.

## Problem
When tasks were assigned to entire class (not individual students), the `current_subtask_id` was set but the subtask didn't exist in the database, causing an error.

## Root Cause
Logic checked if `current_subtask_id` was set and tried to show that specific subtask, but didn't handle the case where the ID was invalid.

## Solution
Added fallback logic: if `current_subtask_id` is set but subtask doesn't exist, show all subtasks instead of error message.

## Related Commits
- `06eb4af` - fix: show all subtasks when current subtask doesn't exist

## Files
- `class_assignment_bug_plan.md` - Investigation plan
- `class_assignment_notes.md` - Debugging notes
