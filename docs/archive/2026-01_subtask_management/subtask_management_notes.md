# Subtask Management Investigation Notes

## Executive Summary

Investigated current subtask assignment system to plan redesign from dropdown-based to checkbox-based interface. Found significant limitations in current approach and designed comprehensive solution.

---

## Current System Analysis

### Architecture

**Database:**
- `student_task.current_subtask_id` - Points to single "current" subtask
- `student_subtask` - Tracks completion per subtask
- No visibility/enable-disable mechanism

**Admin UI:**
- Dropdown selects in `klasse_detail.html` and `schueler_detail.html`
- JavaScript loads subtasks via API call
- Can only set ONE starting subtask per assignment

**Student View:**
- Route: `student_klasse()` at app.py:1099
- Logic: Shows ONLY `current_subtask_id` OR all subtasks (fallback)
- Has prev/next navigation buttons

### Limitations Identified

1. **Dropdown-only interface** - Can't see all options at once
2. **Single subtask focus** - Only one can be "current"
3. **No selective visibility** - Can't hide/show specific subtasks
4. **No per-student customization** in class assignments
5. **Confusing fallback logic** - Shows all if current_subtask invalid
6. **No bulk operations** - Must assign one at a time
7. **No visual hierarchy** - Just text, no organization

### File Locations

**Backend:**
- `models.py:1118-1169` - Assignment functions
- `app.py:317` - Class assignment route
- `app.py:399-435` - Student assignment route
- `app.py:1099` - Student view route

**Frontend:**
- `templates/admin/klasse_detail.html:52-72` - Class UI
- `templates/admin/schueler_detail.html:75-155` - Student UI
- `templates/student/klasse.html` - Student view

---

## Proposed Solution

### Database Schema

**New table: `subtask_visibility`**

```sql
CREATE TABLE subtask_visibility (
    id INTEGER PRIMARY KEY,
    subtask_id INTEGER NOT NULL,
    klasse_id INTEGER,        -- Class-wide rule
    student_id INTEGER,       -- Individual rule
    enabled INTEGER DEFAULT 1,
    set_by_admin_id INTEGER,
    set_at TIMESTAMP,
    -- Constraint: class-wide OR individual, not both
    CHECK ((klasse_id IS NOT NULL AND student_id IS NULL) OR
           (klasse_id IS NULL AND student_id IS NOT NULL))
)
```

**Lookup Priority:**
1. Individual student rules (if exist)
2. Class rules (if exist)
3. Default: all subtasks visible

**Benefits:**
- Explicit enable/disable per subtask
- Supports inheritance (class → individual overrides)
- Audit trail (who/when)
- Backward compatible (no rules = show all)

### Admin UI Design

**Unified Management Page:**

```
Context: [Klasse 5A ▼] or [Schüler ▼]

┌─ 📚 Thema 1: Textverarbeitung ─────┐
│  ☑ Gesamtes Thema                  │
│  ┌────────────────────────────┐    │
│  │ ☑ Aufgabe 1: Dokument       │    │
│  │ ☑ Aufgabe 2: Formatieren    │    │
│  │ ☐ Aufgabe 3: Bilder (Bonus) │    │
│  └────────────────────────────┘    │
└────────────────────────────────────┘

[Änderungen speichern]
```

**Features:**
- Checkbox interface (not dropdowns)
- Task-level toggle (all subtasks at once)
- Individual subtask checkboxes
- Inheritance indicators for students
- Bulk actions (enable all, reset to class)

### Student View Changes

**Before:**
```python
if current_subtask_id:
    show only that subtask
else:
    show all subtasks (fallback)
```

**After:**
```python
visible_subtasks = get_visible_subtasks_for_student(
    student_id, klasse_id, task_id
)
show only visible_subtasks
```

**Benefits:**
- No confusing fallback logic
- Explicit about what's visible
- Better error messages
- Simpler code

---

## Implementation Plan

### Phases

1. ✅ **Research** - Understanding current system (COMPLETE)
2. **Schema Design** - Finalize database structure
3. **UI Mockup** - Visual design for admin interface
4. **Backend** - Models + routes + migration
5. **Admin UI** - New template + JavaScript + CSS
6. **Student View** - Update routing logic
7. **Testing** - Comprehensive test scenarios
8. **Deployment** - Migration + monitoring

### Effort Estimate

**Total: 30-35 hours (4-5 full work days)**

- Backend: 8-11 hours
- Admin UI: 8-10 hours
- Student view: 2-3 hours
- Testing: 4-6 hours
- Documentation: 2 hours
- Schema/planning: 6-7 hours

### Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking current assignments | High | Backward compatible defaults |
| Complex UI | Medium | User testing, clear help text |
| Performance | Low | Indexed queries, caching |

---

## Key Design Decisions

### ✅ Confirmed

1. **Schema:** New `subtask_visibility` table (not JSON column)
2. **Inheritance:** Individual overrides class rules
3. **Default:** No rules = all subtasks visible (backward compat)
4. **UI:** New unified page (not enhanced dropdowns)

### ❓ To Decide

1. **Bulk operations scope:**
   - Copy settings between classes?
   - Apply templates (beginner/advanced modes)?
   - Enable all for new assignments?

2. **Default on assignment:**
   - All subtasks enabled by default?
   - Or none enabled (admin must explicitly enable)?

3. **current_subtask_id migration:**
   - Keep column for compatibility?
   - Deprecate over time?
   - Auto-migrate existing rules?

4. **UI placement:**
   - Link from class detail page?
   - Link from student detail page?
   - New menu item?

---

## Technical Considerations

### Performance

**Query optimization:**
- Index on `subtask_id`, `klasse_id`, `student_id`
- Cache visibility rules per request
- Batch load for multiple students

**Expected queries:**
```sql
-- Student view (one query per page load)
SELECT sv.* FROM subtask_visibility sv
WHERE sv.subtask_id IN (...)
  AND (sv.student_id = ? OR sv.klasse_id = ?)
ORDER BY sv.student_id DESC NULLS LAST
LIMIT 1 PER subtask_id
```

### Backward Compatibility

**Gradual migration:**
1. Deploy with feature flag (optional)
2. Admin can enable per class
3. Old system still works (fallback)
4. Eventually deprecate `current_subtask_id`

**Data migration:**
- No data loss (additive schema)
- Existing assignments work unchanged
- New rules only where admin sets them

### Security

**Authorization checks:**
- Only admins can set visibility rules
- Students can only view their visible subtasks
- Audit trail tracks who changed what

**Input validation:**
- Verify subtask belongs to task
- Verify student belongs to class
- Prevent inconsistent states

---

## Alternative Approaches Considered

### Option B: JSON Column

Instead of new table, add `visible_subtasks` JSON to `student_task`:

```sql
ALTER TABLE student_task
ADD COLUMN visible_subtasks TEXT;
-- Stores: "[1, 3, 5]"
```

**Why rejected:**
- Less flexible (harder for class-wide)
- No audit trail
- JSON in SQL (less normalized)
- Harder to query and bulk-update

### Option C: Multiple current_subtask_id

Add `current_subtasks` (plural) JSON array:

**Why rejected:**
- Still doesn't solve enable/disable
- Confusing semantics (what's "current" about multiple?)
- Doesn't support class-wide rules

### Decision: Option A (subtask_visibility table) is best

---

## User Stories

### Admin: Class-wide Assignment

**As a teacher,**
I want to assign a task to my entire class but only enable the first 3 subtasks,
So that students focus on basics before moving to advanced topics.

**Workflow:**
1. Go to class detail page
2. Click "Aufgaben verwalten"
3. See task with all subtasks
4. Check only first 3 subtasks
5. Save
6. All students see only those 3 subtasks

### Admin: Individual Override

**As a teacher,**
I want to enable additional subtasks for one advanced student,
So they have more challenging work while others focus on basics.

**Workflow:**
1. Go to student detail page
2. Click "Aufgaben verwalten"
3. See current class settings (inherited)
4. Check additional subtasks
5. Save
6. Student sees more subtasks than classmates

### Student: Clear Progression

**As a student,**
I want to see only the tasks my teacher has enabled for me,
So I know exactly what to work on without confusion.

**Experience:**
- Load task page
- See only enabled subtasks (no clutter)
- Progress bar shows only enabled tasks
- Clear what's next

---

## Future Enhancements (Post-MVP)

### Templates

**Preset visibility configurations:**
- "Beginner mode" - Basics only
- "Advanced mode" - All subtasks
- "Remedial" - Selected core tasks
- "Challenge" - Bonus tasks only

**Benefit:** Quick setup for common scenarios

### Copy Settings

**Bulk operations:**
- Copy from Class A to Class B
- Copy from one student to others
- Export/import configurations

**Benefit:** Reuse successful configurations

### Analytics

**Track visibility usage:**
- Which subtasks are most often disabled?
- Completion rates by visibility settings
- Identify patterns

**Benefit:** Data-driven pedagogy

---

## Questions for User (Patrick)

Before implementation Phase 2, need decisions on:

1. **Default behavior when assigning new task:**
   - Option A: All subtasks enabled (admin can disable)
   - Option B: No subtasks enabled (admin must enable)
   - Recommendation: Option A (less disruption)

2. **Bulk operations priority:**
   - Must-have: Toggle all for task
   - Nice-to-have: Copy between classes
   - Future: Templates
   - What's most important?

3. **UI placement preference:**
   - New standalone page (my recommendation)
   - Or enhanced existing assignment UI
   - Or both (link from detail pages to new page)

4. **current_subtask_id migration:**
   - Keep for now (backward compat)
   - Or migrate all at once
   - Recommendation: Keep, deprecate later

---

## Success Metrics

### Quantitative

- **Admin efficiency:** Time to assign subtasks (should decrease)
- **UI usage:** Admins use new interface (vs old dropdowns)
- **Student clarity:** Support tickets about "which task?" (should decrease)
- **Completion rates:** Track if selective visibility helps

### Qualitative

- **Admin feedback:** Easier to manage?
- **Student feedback:** Less confusing?
- **Teacher satisfaction:** Better control over pacing?

---

**Status:** Investigation complete, ready for Phase 2 (schema design) after user decisions
