# Diagnostic Queries for Task Visibility Bug

## Questions for Patrick

To help debug this, I need to understand the exact state after editing:

1. **After you edit the task and save**, can you run this query on the database:
   ```sql
   SELECT * FROM subtask WHERE task_id = [YOUR_TASK_ID];
   ```
   How many subtasks exist? What are their IDs?

2. **Check student_task record**:
   ```sql
   SELECT * FROM student_task WHERE task_id = [YOUR_TASK_ID];
   ```
   Does the record exist? What is current_subtask_id?

3. **Check visibility records**:
   ```sql
   SELECT sv.*, s.reihenfolge
   FROM subtask_visibility sv
   JOIN subtask s ON sv.subtask_id = s.id
   WHERE s.task_id = [YOUR_TASK_ID];
   ```
   Are there any visibility records after editing?

4. **What exactly are you editing?**
   - Are you editing the subtask text/descriptions?
   - Are you editing the time estimates?
   - Are you adding/removing subtasks?
   - Or are you editing something else (task name, description, etc.)?

## Hypothesis

I suspect the issue might be:
- The code changes aren't being loaded (app not restarted?)
- OR the edit is happening through a different route
- OR there's a caching issue
- OR the subtasks are being filtered out for a different reason

Please provide the query results and clarify what exactly you're editing when the bug occurs.
