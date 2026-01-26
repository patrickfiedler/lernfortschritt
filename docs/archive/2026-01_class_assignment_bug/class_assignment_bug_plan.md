# Task Plan: Fix Class-Wide Task Assignment Bug

## Goal
Students should see active subtasks when tasks are assigned to entire classes in the admin view.

## Phases
- [x] Phase 1: Understand current assignment flow (admin → database → student view)
- [x] Phase 2: Identify where class-wide assignment breaks
- [x] Phase 3: Implement fix
- [x] Phase 4: Commit and push

## Key Questions
1. How does the admin assign tasks to classes vs individual students?
2. What database records are created for class-wide assignments?
3. How does the student view query for active tasks/subtasks?
4. Is the issue in assignment creation or student retrieval?

## Decisions Made
- Starting with code reading to understand the flow
- **Solution chosen**: Fallback to all subtasks (Option A)
  - If `current_subtask_id` is set but subtask doesn't exist, show all subtasks
  - Most user-friendly approach - students always see their work

## Errors Encountered
(None yet)

## Fix Implementation

**File changed:** app.py:1134-1137

Added fallback logic:
- If `current_subtask_id` is set but `get_current_subtask()` returns None
- Fall back to showing all subtasks (`subtasks = all_subtasks`)
- This handles cases where subtasks are deleted or tasks have no subtasks

## Deployment

**Commit:** 06eb4af - "fix: show all subtasks when current subtask doesn't exist"
**Pushed to:** GitHub main branch
**Date:** 2026-01-19

To deploy to production:
```bash
ssh user@server 'sudo /opt/lernmanager/deploy/update.sh'
```

## Status
**COMPLETE** - Bug fixed, committed, and pushed to GitHub.
