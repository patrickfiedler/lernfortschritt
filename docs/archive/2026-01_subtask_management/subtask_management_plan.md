# Task Plan: Robust Subtask Management Redesign

## Goal
Replace dropdown-based subtask assignment with an organized checkbox interface that allows flexible enable/disable of specific subtasks for classes and individual students, while making the student view more robust.

## Executive Summary

**Current Problems:**
1. Dropdown interface only shows truncated descriptions, can't see all at once
2. Can only set ONE starting subtask per student/class
3. No way to enable/disable specific subtasks selectively
4. No bulk operations for multiple students
5. No visual hierarchy or task organization
6. Student view relies on brittle `current_subtask_id` logic with confusing fallbacks

**Proposed Solution:**
- Unified checkbox-based interface for task/subtask management
- Enable/disable individual subtasks per class or per student
- Visual hierarchy showing task → subtasks relationships
- Robust student view that shows enabled subtasks only
- Bulk operations support

## Phases
- [x] Phase 1: Research and design (investigate current system)
- [x] Phase 2: Database schema design
- [ ] Phase 3: Design admin UI mockup
- [ ] Phase 4: Implement backend (models + routes)
- [ ] Phase 5: Implement admin UI
- [ ] Phase 6: Update student view
- [ ] Phase 7: Testing and refinement
- [ ] Phase 8: Documentation and deployment

## Phase 1: Research and Design ✅

### Current System Analysis (COMPLETE)

**Database Schema:**
- `student_task` table has `current_subtask_id` (single subtask focus)
- `student_subtask` tracks completion per subtask
- `subtask` table has task relationship and order

**Assignment Mechanisms:**
1. Class-wide: `assign_task_to_klasse()` - all students get same starting subtask
2. Individual: `assign_task_to_student()` - one student at a time
3. After assignment: `set_current_subtask()` - change which subtask is shown

**Admin Interface:**
- Dropdowns in `templates/admin/klasse_detail.html` (lines 52-72)
- Dropdowns in `templates/admin/schueler_detail.html` (lines 75-155)
- JavaScript loads subtasks via API

**Student View:**
- Route: `student_klasse()` at line 1099 in app.py
- Template: `templates/student/klasse.html`
- Logic: Shows only `current_subtask_id` OR all subtasks (fallback)
- Has prev/next navigation for subtasks

**Key Limitations:**
1. ❌ Only one subtask can be "current"
2. ❌ No way to hide/show specific subtasks
3. ❌ No per-student customization in class assignments
4. ❌ Dropdown UI doesn't scale well
5. ❌ Confusing fallback behavior (shows all if current_subtask invalid)

### Files to Modify:
- `models.py` - Database schema and functions (lines 1118-1169)
- `app.py` - Admin routes (lines 317, 399-435) and student route (line 1099)
- `templates/admin/klasse_detail.html` - Class assignment UI
- `templates/admin/schueler_detail.html` - Student assignment UI
- `templates/student/klasse.html` - Student display logic
- New migration script needed

---

## Phase 2: Database Schema Design

### Option A: Extend Current System (Recommended)

**Approach:** Add new table to track which subtasks are enabled for which contexts.

**New table: `subtask_visibility`**
```sql
CREATE TABLE subtask_visibility (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subtask_id INTEGER NOT NULL,

    -- Context: class-wide OR individual student
    klasse_id INTEGER,
    student_id INTEGER,

    -- Visibility flag
    enabled INTEGER DEFAULT 1,

    -- Metadata
    set_by_admin_id INTEGER,
    set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (subtask_id) REFERENCES subtask(id) ON DELETE CASCADE,
    FOREIGN KEY (klasse_id) REFERENCES klasse(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
    FOREIGN KEY (set_by_admin_id) REFERENCES admin(id),

    -- Constraint: either class-wide OR individual
    CHECK ((klasse_id IS NOT NULL AND student_id IS NULL) OR
           (klasse_id IS NULL AND student_id IS NOT NULL))
)
```

**Lookup logic:**
1. Check if student has individual subtask visibility rules → use those
2. Else check if class has subtask visibility rules → use those
3. Else default to showing all subtasks of assigned task

**Benefits:**
- ✅ Explicit enable/disable per subtask
- ✅ Supports both class-wide and individual overrides
- ✅ Individual rules can override class rules
- ✅ Maintains backward compatibility (NULL = show all)
- ✅ Easy to audit (who enabled what, when)

**Considerations:**
- Need migration to create table
- Need to handle inheritance (class → individual)
- Cleanup needed when tasks/students/classes are deleted (CASCADE)

### Option B: Simpler Approach (Alternative)

**Approach:** Add `visible_subtasks` JSON column to `student_task` table.

```sql
ALTER TABLE student_task ADD COLUMN visible_subtasks TEXT;
-- Stores JSON array of subtask IDs: "[1, 3, 5]"
```

**Benefits:**
- ✅ Simpler schema (one column)
- ✅ No new table needed
- ✅ Fast lookups (one row per student_task)

**Drawbacks:**
- ❌ Less flexible (harder to manage class-wide defaults)
- ❌ JSON in SQL (less normalized)
- ❌ No audit trail
- ❌ Harder to bulk-update across students

**Decision:** Recommend Option A (subtask_visibility table) for flexibility and maintainability.

---

## Phase 3: Admin UI Design

### Unified Subtask Management Interface

**Location:** New page or enhanced section in existing admin pages

**Layout Concept:**

```
┌─────────────────────────────────────────────┐
│ Aufgaben und Teilaufgaben verwalten        │
├─────────────────────────────────────────────┤
│                                             │
│ Kontext: [Klasse 5A ▼] oder [Schüler ▼]   │
│                                             │
│ ┌─ 📚 Thema 1: Textverarbeitung ─────────┐ │
│ │  ☑ Gesamtes Thema aktiviert            │ │
│ │  ┌──────────────────────────────────┐  │ │
│ │  │ ☑ Aufgabe 1: Dokument erstellen  │  │ │
│ │  │ ☑ Aufgabe 2: Text formatieren    │  │ │
│ │  │ ☑ Aufgabe 3: Bilder einfügen     │  │ │
│ │  │ ☐ Aufgabe 4: Tabellen (Bonus)    │  │ │
│ │  └──────────────────────────────────┘  │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ ┌─ 📊 Thema 2: Tabellenkalkulation ──────┐ │
│ │  ☐ Gesamtes Thema inaktiv              │ │
│ │  (Klicken zum Aktivieren)               │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ [Änderungen speichern]  [Zurücksetzen]    │
└─────────────────────────────────────────────┘
```

**Features:**

1. **Context Selector:**
   - Dropdown: Select class OR individual student
   - Shows "Klasse: [name]" or "Schüler: [name] in Klasse [X]"

2. **Task Accordion:**
   - Collapsible cards for each task
   - Task-level checkbox: Enable/disable all subtasks at once
   - Shows subtask count: "(3 von 5 aktiviert)"

3. **Subtask Checkboxes:**
   - Each subtask has checkbox + description
   - Ordered by `reihenfolge`
   - Show completion status if student context: "✓ Erledigt" badge
   - Visual indicators:
     - ☑ Enabled (green)
     - ☐ Disabled (gray)
     - ✓ Completed (gold/success color)

4. **Inheritance Indicators (for individual students):**
   - Show if setting inherits from class: "⚙ Von Klasse geerbt"
   - Allow overriding: Click checkbox to set individual rule

5. **Bulk Actions:**
   - "Alle aktivieren" / "Alle deaktivieren" buttons
   - "Standard wiederherstellen" (reset to class defaults)

6. **Save Behavior:**
   - Explicit save button (not auto-save)
   - Show unsaved changes indicator
   - Confirm before discarding changes

### Alternative: Enhanced Current UI

**Simpler option:** Add checkbox interface to EXISTING assignment pages

**Location:** `templates/admin/klasse_detail.html` and `schueler_detail.html`

**Changes:**
- Replace dropdown with expandable task list
- Show checkboxes for each subtask
- Keep existing "Aufgabe zuweisen" flow but enhance it

**Benefits:**
- Less disruption to current workflow
- Faster to implement
- Familiar location for admins

**Drawbacks:**
- Less space for large task lists
- Might feel cramped in sidebar

**Decision:** Recommend NEW unified page for better UX, but can start with enhanced current UI if faster.

---

## Phase 4: Backend Implementation

### 4.1 Database Migration

**File:** `migrate_subtask_visibility.py`

```python
def migrate():
    # Create subtask_visibility table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subtask_visibility (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtask_id INTEGER NOT NULL,
            klasse_id INTEGER,
            student_id INTEGER,
            enabled INTEGER DEFAULT 1,
            set_by_admin_id INTEGER,
            set_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subtask_id) REFERENCES subtask(id) ON DELETE CASCADE,
            FOREIGN KEY (klasse_id) REFERENCES klasse(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
            FOREIGN KEY (set_by_admin_id) REFERENCES admin(id),
            CHECK ((klasse_id IS NOT NULL AND student_id IS NULL) OR
                   (klasse_id IS NULL AND student_id IS NOT NULL))
        )
    """)

    # Create indexes for fast lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sv_subtask ON subtask_visibility(subtask_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sv_klasse ON subtask_visibility(klasse_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sv_student ON subtask_visibility(student_id)")
```

### 4.2 New Models Functions

**File:** `models.py`

```python
def get_visible_subtasks_for_student(student_id, klasse_id, task_id):
    """
    Get list of subtasks that are visible to a student.

    Priority:
    1. Individual student rules (subtask_visibility with student_id)
    2. Class rules (subtask_visibility with klasse_id)
    3. Default: all subtasks of the task

    Returns: List of subtask dicts with 'id', 'beschreibung', 'reihenfolge', 'erledigt'
    """
    pass

def set_subtask_visibility_for_class(klasse_id, subtask_id, enabled, admin_id):
    """Set visibility of a subtask for entire class."""
    pass

def set_subtask_visibility_for_student(student_id, subtask_id, enabled, admin_id):
    """Set visibility of a subtask for individual student (overrides class)."""
    pass

def get_subtask_visibility_settings(klasse_id=None, student_id=None, task_id=None):
    """
    Get current visibility settings for context.
    Returns dict mapping subtask_id -> {enabled, source: 'class'|'individual'|'default'}
    """
    pass

def bulk_set_subtask_visibility(context, subtask_ids, enabled, admin_id):
    """Bulk enable/disable multiple subtasks."""
    pass

def reset_subtask_visibility_to_class_default(student_id):
    """Remove individual overrides, fall back to class settings."""
    pass
```

### 4.3 New Admin Routes

**File:** `app.py`

```python
@app.route('/admin/teilaufgaben-verwaltung')
@admin_required
def admin_subtask_management():
    """Unified subtask management page."""
    # Show interface to select class or student
    # Default view or redirect to specific context
    pass

@app.route('/admin/teilaufgaben-verwaltung/klasse/<int:klasse_id>')
@admin_required
def admin_subtask_management_class(klasse_id):
    """Manage subtask visibility for a class."""
    # Get all tasks
    # Get all subtasks per task
    # Get current visibility settings for class
    # Render checkbox interface
    pass

@app.route('/admin/teilaufgaben-verwaltung/schueler/<int:student_id>')
@admin_required
def admin_subtask_management_student(student_id):
    """Manage subtask visibility for individual student."""
    # Similar to class but show inheritance indicators
    pass

@app.route('/admin/teilaufgaben-verwaltung/speichern', methods=['POST'])
@admin_required
def admin_subtask_management_save():
    """Save visibility settings."""
    # Get context (class or student)
    # Get checked/unchecked subtasks from form
    # Call appropriate models functions
    # Redirect with success message
    pass
```

### 4.4 Update Existing Routes

**Modify:** `student_klasse()` route (line 1099 in app.py)

**Changes:**
- Replace `current_subtask_id` filtering logic
- Use new `get_visible_subtasks_for_student()` function
- Show only enabled subtasks (no "show all" fallback)
- Handle case where no subtasks enabled (show message)

```python
# OLD:
if student_task['current_subtask_id']:
    subtasks = [s for s in subtasks if s['id'] == student_task['current_subtask_id']]
else:
    # Fallback: show all
    pass

# NEW:
visible_subtasks = models.get_visible_subtasks_for_student(
    student_id=session['student_id'],
    klasse_id=klasse_id,
    task_id=student_task['task_id']
)
subtasks = visible_subtasks  # Only show enabled ones
```

---

## Phase 5: Admin UI Implementation

### 5.1 New Template

**File:** `templates/admin/teilaufgaben_verwaltung.html`

**Structure:**
```html
{% extends 'base.html' %}

{% block content %}
<h1>Aufgaben und Teilaufgaben verwalten</h1>

<!-- Context selector -->
<form method="get" class="context-selector">
    <label>Kontext:</label>
    <select name="context_type" onchange="updateContext()">
        <option value="class">Klasse</option>
        <option value="student">Einzelner Schüler</option>
    </select>

    <select name="klasse_id" id="klasse-select">
        {% for k in klassen %}
        <option value="{{ k.id }}">{{ k.name }}</option>
        {% endfor %}
    </select>

    <select name="student_id" id="student-select" style="display:none;">
        <!-- Populated by JS -->
    </select>

    <button type="submit">Anzeigen</button>
</form>

<!-- Task/Subtask checkboxes -->
<form method="post" action="{{ url_for('admin_subtask_management_save') }}" id="visibility-form">
    <input type="hidden" name="context_type" value="{{ context_type }}">
    <input type="hidden" name="context_id" value="{{ context_id }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">

    {% for task in tasks %}
    <div class="task-card">
        <div class="task-header">
            <h2>
                <label>
                    <input type="checkbox" class="task-toggle" data-task-id="{{ task.id }}"
                           onchange="toggleAllSubtasks({{ task.id }}, this.checked)">
                    {{ task.name }}
                </label>
            </h2>
            <span class="subtask-count">{{ task.enabled_count }} von {{ task.total_count }}</span>
        </div>

        <div class="subtasks-list">
            {% for subtask in task.subtasks %}
            <div class="subtask-item">
                <label>
                    <input type="checkbox" name="subtask_{{ subtask.id }}"
                           value="1" {% if subtask.enabled %}checked{% endif %}
                           data-task-id="{{ task.id }}">
                    <span class="subtask-description">{{ subtask.beschreibung }}</span>

                    {% if subtask.completed %}
                    <span class="badge badge-success">✓ Erledigt</span>
                    {% endif %}

                    {% if subtask.source == 'class' and context_type == 'student' %}
                    <span class="badge badge-info">⚙ Von Klasse</span>
                    {% endif %}
                </label>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}

    <div class="actions">
        <button type="submit" class="btn btn-primary">Änderungen speichern</button>
        <button type="button" class="btn btn-secondary" onclick="resetForm()">Zurücksetzen</button>
        {% if context_type == 'student' %}
        <button type="button" class="btn btn-outline" onclick="resetToClassDefaults()">Klassenstandard wiederherstellen</button>
        {% endif %}
    </div>
</form>

<script>
function toggleAllSubtasks(taskId, enabled) {
    document.querySelectorAll(`input[data-task-id="${taskId}"]`).forEach(cb => {
        if (!cb.classList.contains('task-toggle')) {
            cb.checked = enabled;
        }
    });
    updateTaskToggleStates();
}

function updateTaskToggleStates() {
    document.querySelectorAll('.task-toggle').forEach(toggle => {
        const taskId = toggle.dataset.taskId;
        const subtaskBoxes = document.querySelectorAll(`input[data-task-id="${taskId}"]:not(.task-toggle)`);
        const allChecked = Array.from(subtaskBoxes).every(cb => cb.checked);
        toggle.checked = allChecked;
    });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', updateTaskToggleStates);
</script>
{% endblock %}
```

### 5.2 Styling

**File:** `static/css/style.css`

```css
.task-card {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-bottom: 1rem;
    padding: 1rem;
}

.task-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 0.5rem;
    margin-bottom: 0.5rem;
}

.task-header h2 {
    margin: 0;
    font-size: 1.25rem;
}

.task-toggle {
    margin-right: 0.5rem;
    transform: scale(1.2);
}

.subtask-count {
    font-size: 0.875rem;
    color: #666;
}

.subtasks-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding-left: 2rem;
}

.subtask-item label {
    display: flex;
    align-items: center;
    padding: 0.5rem;
    border-radius: 4px;
    transition: background 0.2s;
}

.subtask-item label:hover {
    background: #f8f8f8;
}

.subtask-item input[type="checkbox"] {
    margin-right: 0.75rem;
}

.badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 3px;
    margin-left: 0.5rem;
}

.badge-success {
    background: #d4edda;
    color: #155724;
}

.badge-info {
    background: #d1ecf1;
    color: #0c5460;
}

.actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #ddd;
}
```

### 5.3 JavaScript Enhancements

**Features needed:**
- Dynamic context switching (class ↔ student)
- Load students when class is selected
- Toggle all subtasks when task checkbox clicked
- Update task checkbox state when subtasks change
- Unsaved changes warning
- Reset to class defaults (AJAX call)

---

## Phase 6: Update Student View

### 6.1 Modify Student Route

**File:** `app.py` line 1099

**Current logic:**
```python
# Show current_subtask OR all subtasks
if student_task['current_subtask_id']:
    # Filter to one subtask
else:
    # Show all
```

**New logic:**
```python
# Get visible subtasks using new function
visible_subtasks = models.get_visible_subtasks_for_student(
    student_id=session['student_id'],
    klasse_id=klasse_id,
    task_id=student_task['task_id']
)

# If no visible subtasks, show helpful message
if not visible_subtasks:
    flash('Keine Aufgaben freigeschaltet. Wende dich an deine Lehrkraft.', 'info')
    return redirect(url_for('student_dashboard'))

# Pass to template
return render_template('student/klasse.html',
                      subtasks=visible_subtasks,
                      ...)
```

### 6.2 Update Student Template (Optional)

**File:** `templates/student/klasse.html`

**Minor changes:**
- Remove logic for "current" vs "all" subtasks
- Always use `subtasks` list from backend
- Update progress calculation to use visible subtasks only
- Handle empty case with message (already handled by route)

**Benefits of new system:**
- Simpler template logic
- No confusing fallbacks
- Clear which subtasks are available
- Better error messages

---

## Phase 7: Testing and Refinement

### 7.1 Unit Testing

**Test cases for models:**
1. ✓ Visibility inheritance (individual overrides class)
2. ✓ Default behavior (no rules = all visible)
3. ✓ Bulk operations work correctly
4. ✓ CASCADE deletes clean up visibility rules
5. ✓ Reset to class defaults removes individual overrides

### 7.2 Integration Testing

**Test scenarios:**
1. ✓ Assign task to class, set visibility rules
2. ✓ Override for individual student
3. ✓ Student sees only enabled subtasks
4. ✓ Completion still tracked for disabled subtasks
5. ✓ Navigation works with subset of subtasks
6. ✓ Progress calculations correct

### 7.3 UI Testing

**Admin interface:**
1. ✓ Context switching works (class ↔ student)
2. ✓ Checkboxes reflect current state
3. ✓ Bulk toggle (task-level checkbox) works
4. ✓ Save persists changes
5. ✓ Inheritance indicators show correctly
6. ✓ Reset to defaults works

**Student interface:**
1. ✓ Only enabled subtasks visible
2. ✓ Progress accurate
3. ✓ Navigation skips disabled subtasks
4. ✓ Helpful message if no subtasks enabled

### 7.4 Edge Cases

**Test:**
- Task with no subtasks
- Task with all subtasks disabled
- Student with mixed individual/class rules
- Deleting task/class/student (CASCADE cleanup)
- Concurrent admin edits (rare but possible)

---

## Phase 8: Documentation and Deployment

### 8.1 Update Documentation

**Files to update:**
- `CLAUDE.md` - Document new subtask management system
- Code comments in new functions
- Admin user guide (if exists)

### 8.2 Migration Path

**For existing data:**
1. Run migration to create `subtask_visibility` table
2. Existing assignments keep working (default = show all)
3. Admins can start setting visibility rules
4. No disruption to students

**Backward compatibility:**
- Keep `current_subtask_id` column for now (deprecate later)
- If no visibility rules, default to showing all subtasks
- Gradual migration: admins enable new system per class

### 8.3 Deployment Checklist

- [ ] Run database migration
- [ ] Deploy new code
- [ ] Test on production with one class
- [ ] Monitor for errors
- [ ] Roll out to all classes
- [ ] Gather admin feedback
- [ ] Iterate on UI based on usage

---

## Key Questions

1. ✅ **Primary use case:** Enable/disable individual subtasks per class/student?
   - Yes, this is the main goal

2. ❓ **Deprecate current_subtask_id?**
   - Keep for backward compat initially
   - Migrate users to new system
   - Remove in future version

3. ❓ **Bulk operations scope:**
   - Enable all subtasks for a class?
   - Copy settings from one class to another?
   - Apply template (e.g., "beginner mode" with fewer subtasks)?

4. ❓ **Default behavior:**
   - When task first assigned, which subtasks are enabled?
   - All by default, then admin can disable?
   - Or none by default, admin must enable?

5. ❓ **UI placement:**
   - New standalone page (recommended)?
   - Or enhanced existing assignment UI?
   - Add link from class/student detail pages?

6. ❓ **Student navigation:**
   - Auto-skip disabled subtasks in prev/next?
   - Or hide prev/next if only one subtask visible?

## Decisions Made

- **Schema:** Option A (subtask_visibility table) chosen for flexibility
- **UI:** New unified page for better UX
- **Logic:** Individual settings override class settings
- **Default:** If no rules, show all subtasks (backward compatible)
- **Default on assignment:** All subtasks enabled by default (admin can disable)
- **Bulk operations:** Toggle all for task (Phase 1), copy between classes (future)
- **Keep current_subtask_id:** Yes, for backward compatibility, deprecate later
- **UI placement:** New standalone page with links from detail pages

## Errors Encountered

- (none yet)

## Status

**Phase 2 Complete ✅** - Moving to Phase 4: Backend Implementation

Completed:
- ✅ Phase 1: Research and investigation
- ✅ Phase 2: Database schema and migration script created

Created `migrate_subtask_visibility.py`:
- Creates subtask_visibility table with proper constraints
- Includes indexes for fast lookups
- SQLCipher compatible
- Idempotent (safe to run multiple times)
- Creates automatic backups

Implementation decisions:
- All subtasks enabled by default when task assigned
- New standalone admin page
- Keep current_subtask_id for backward compatibility

Next: Phase 4 - Implement backend models functions

---

## Implementation Effort Estimate

| Phase | Estimated Time |
|-------|---------------|
| Phase 1: Research | ✅ 2 hours (COMPLETE) |
| Phase 2: Schema design | 2-3 hours |
| Phase 3: UI mockup | 2 hours |
| Phase 4: Backend | 6-8 hours |
| Phase 5: Admin UI | 6-8 hours |
| Phase 6: Student view | 2-3 hours |
| Phase 7: Testing | 4-6 hours |
| Phase 8: Documentation | 2 hours |
| **TOTAL** | **26-34 hours** |

**Realistic estimate:** 30-35 hours (4-5 full work days)

---

## Benefits of New System

### For Admins
✅ See all tasks/subtasks at once (no dropdown hunting)
✅ Flexible enable/disable per class or individual
✅ Visual hierarchy and organization
✅ Bulk operations save time
✅ Clear inheritance model (class → individual)

### For Students
✅ Only see relevant subtasks (less overwhelming)
✅ Clear progression through enabled tasks
✅ No confusing "current subtask" limitations
✅ More robust (no fallback logic confusion)

### For System
✅ More explicit data model (no ambiguous fallbacks)
✅ Easier to debug and maintain
✅ Supports future features (templates, presets)
✅ Better audit trail (who enabled what, when)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing assignments | High | Backward compatible default (show all) |
| Complex UI confuses admins | Medium | User testing, clear labels, help text |
| Performance (many visibility rules) | Low | Indexed lookups, caching if needed |
| Migration issues | Medium | Test thoroughly, have rollback plan |
| Student confusion | Low | Gradual rollout, monitor feedback |

---

## Next Steps (After Approval)

1. Review and refine database schema (Phase 2)
2. Create UI mockup for feedback (Phase 3)
3. Get user input on default behavior and bulk operations
4. Implement backend (Phase 4)
5. Build admin interface (Phase 5)
6. Update student view (Phase 6)
7. Comprehensive testing (Phase 7)
8. Deploy with monitoring (Phase 8)

---

**End of Plan - Ready for Phase 2**
