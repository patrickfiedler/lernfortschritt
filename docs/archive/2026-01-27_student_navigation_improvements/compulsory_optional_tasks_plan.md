# Compulsory vs Optional Tasks Feature Plan

## Goal
Distinguish compulsory and optional subtasks with different colors in student view to help students prioritize their work.

## Current Status
**DEFERRED** - Requires database schema and task editor changes before frontend implementation.

## Design Specification (from todo.md)
- **Yellow dots**: Open compulsory tasks (not yet completed)
- **Green dots**: Completed tasks (both compulsory and optional)
- **Rainbow/spectrum colors**: Optional tasks (e.g., purple, orange, pink, cyan)

## Required Implementation Steps

### 1. Database Schema Changes
Add `is_compulsory` field to `subtask` table:
```sql
ALTER TABLE subtask ADD COLUMN is_compulsory INTEGER DEFAULT 1;
-- 1 = compulsory, 0 = optional
```

### 2. Backend Changes (models.py)
- Update `get_subtasks()` to include `is_compulsory` field
- Update `get_visible_subtasks_for_student()` to return compulsory status
- Update all subtask queries to include the new field

### 3. Task Editor UI (Admin View)
Add checkbox or toggle in task editor form:
- Location: `templates/admin/aufgabe_bearbeiten.html`
- Add field: "Pflichtaufgabe" (checkbox, default checked)
- Update save route to store `is_compulsory` value

### 4. Frontend Display (Student View)
Update progress dot colors in `templates/student/klasse.html`:

**Current logic**:
```html
<div class="dot {% if sub.erledigt %}completed{% elif sub.id == active_subtask.id %}current{% endif %}">
```

**New logic**:
```html
<div class="dot
    {% if sub.erledigt %}completed
    {% elif sub.id == active_subtask.id %}current
    {% elif sub.is_compulsory %}compulsory
    {% else %}optional optional-{{ loop.index0 % 4 }}{% endif %}">
```

### 5. CSS Styling (static/css/style.css)
Add new dot color classes:

```css
/* Compulsory task (open, not completed) */
.dot.compulsory {
    background: #fbbf24; /* yellow-400 */
}

/* Optional tasks - rainbow spectrum */
.dot.optional.optional-0 {
    background: #a78bfa; /* violet-400 */
}

.dot.optional.optional-1 {
    background: #fb923c; /* orange-400 */
}

.dot.optional.optional-2 {
    background: #ec4899; /* pink-400 */
}

.dot.optional.optional-3 {
    background: #22d3ee; /* cyan-400 */
}

/* Completed stays green for both types */
.dot.completed {
    background: #10b981; /* green-500 */
}
```

### 6. Testing Checklist
- [ ] Task editor shows compulsory checkbox
- [ ] Saving task stores is_compulsory correctly
- [ ] Student view shows yellow dots for open compulsory tasks
- [ ] Student view shows rainbow colors for optional tasks
- [ ] Completed tasks show green regardless of type
- [ ] Progress dots update correctly after completion
- [ ] Database migration runs successfully on existing data

## Estimated Time
- Database + backend: 30 minutes
- Task editor UI: 30 minutes
- Frontend display: 20 minutes
- CSS styling: 15 minutes
- Testing: 30 minutes
**Total**: ~2 hours

## Priority
Medium - UX enhancement that helps students prioritize work, but not blocking core functionality.

## Related Files
- `models.py` - Database queries
- `app.py` - Task editor save route
- `templates/admin/aufgabe_bearbeiten.html` - Task editor form
- `templates/student/klasse.html` - Progress dots display
- `static/css/style.css` - Dot color styles
