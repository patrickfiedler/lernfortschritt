# Subtask Advancement Bug - Investigation Notes

## Issue Description
- Students can mark subtasks complete (they turn green)
- App does NOT advance to next subtask automatically
- No errors in server logs or JavaScript console

## Code Flow Analysis

### 1. Frontend (templates/student/klasse.html:259-287)
```javascript
function toggleSubtask(studentTaskId, subtaskId, checked) {
    // POST request to server
    fetch(`/schueler/aufgabe/${studentTaskId}/teilaufgabe/${subtaskId}`, {...})
    .then(r => r.json()).then(data => {
        // Update UI: add/remove 'completed' class
        // Update progress bar
        // Reload if task_complete
    });
}
```

**Problem**: The JavaScript doesn't reload the page or update the view when the subtask advances!

### 2. Backend (app.py:1100-1136)
```python
def student_toggle_subtask(student_task_id, subtask_id):
    # Mark subtask complete
    models.toggle_student_subtask(student_task_id, subtask_id, erledigt)
    # Returns JSON: {'status': 'ok', 'task_complete': False}
```

### 3. Model (models.py:1112-1122)
```python
def toggle_student_subtask(student_task_id, subtask_id, erledigt):
    with db_session() as conn:
        # Update student_subtask table
        conn.execute('INSERT OR REPLACE INTO student_subtask...')

        # Auto-advance
        if erledigt:
            _advance_to_next_subtask_internal(conn, student_task_id, subtask_id)
```

The auto-advance DOES happen in the database!

### 4. Advancement Logic (models.py:1139-1196)
```python
def _advance_to_next_subtask_internal(conn, student_task_id, current_subtask_id):
    # Gets task_id
    # Gets all subtasks ordered by reihenfolge
    # Finds next incomplete subtask after current
    # Updates: UPDATE student_task SET current_subtask_id = ?
```

This updates the database correctly.

## Root Cause

**The database is updated correctly (current_subtask_id advances), but the frontend doesn't refresh to show the new current subtask.**

The JavaScript only:
1. Marks current subtask green ✅
2. Updates progress bar ✅
3. Reloads if ENTIRE TASK complete ✅

But it does NOT:
- Reload the page to show the new current subtask ❌
- Make an AJAX call to get the new subtask ❌

## Solution Options

### Option A: Reload on Subtask Complete (Simple)
When `checked === true`, always reload the page after successful toggle.

**Pros:**
- Simple, 1-line change
- Guaranteed to show new state
- Works like task completion already does

**Cons:**
- Page reload might feel jarring
- Loses scroll position

### Option B: AJAX Update (Better UX)
Return the new current_subtask_id in JSON response, then update DOM dynamically.

**Pros:**
- No page reload
- Smooth user experience

**Cons:**
- More complex
- Need to handle DOM updates for hiding old/showing new subtask

### Option C: Check if current_subtask_id is set
Only reload if the student_task has a current_subtask_id set (filtered mode).
In legacy mode (all subtasks visible), no reload needed.

**Pros:**
- Best of both worlds
- Backward compatible

**Cons:**
- Slightly more complex

## Recommendation

**Option A (reload on complete) is the best choice** because:
1. Matches existing behavior (task completion already reloads)
2. Simplest to implement
3. Most reliable
4. Students are used to page reloads in this app
5. The page load is fast enough that it won't be jarring

## Issue Found After First Fix

Using `location.reload()` causes browser form state restoration - the checkbox state is preserved across the reload, making the NEW subtask appear checked even though it isn't completed.

**Solution**: Use `location.href = location.href` instead of `location.reload()` to force a fresh page load without form state restoration.
