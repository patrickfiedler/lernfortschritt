# Student View Fixes and Enhancements Plan

## Problem Summary (Test 9 Findings)

**Cache-busting issues:**
1. Completing subtask → next button → progress dots not updated correctly
2. Requires manual page reload to see correct state
3. Same root cause as admin view (browser caching AJAX-reloaded pages)

**Count mismatch:**
4. Dashboard shows "3/8" but only 4 subtasks visible (should show "3/4")
5. Student klasse view shows total count instead of visible count

**Related improvements from todo.md:**
6. Visual indicator for current task position (line 30)
7. Cache-Control headers instead of timestamp params (line 32)

---

## Root Cause Analysis

### Issue 1 & 2: Progress Dots Not Updating
**Location**: `templates/student/klasse.html` lines 291, 318

**Current behavior:**
- Line 291: Uncheck subtask → `location.reload()`
- Line 318: Next button → `location.reload()`
- Browser serves cached page, progress dots show stale state

**Why dots update inconsistently:**
- First reload: Cache hit → stale dots
- Second reload: Sometimes cache miss → correct dots
- This explains "works on second try" behavior

### Issue 3-5: Wrong Subtask Counts

**Dashboard** (`templates/student/dashboard.html` line 44):
```html
<span>{{ task.completed_subtasks }}/{{ task.total_subtasks }}</span>
```

**Backend** (`app.py` line 1228-1229):
```python
task['total_subtasks'] = len(subtasks)  # ALL subtasks
task['completed_subtasks'] = sum(1 for s in subtasks if s['erledigt'])
```

**Problem**: Uses `len(subtasks)` which includes ALL subtasks, not just visible ones.

**Should be**:
```python
visible_subtasks = models.get_visible_subtasks_for_student(student_id, klasse_id, task_id)
task['total_subtasks'] = len(visible_subtasks)
task['completed_subtasks'] = sum(1 for s in visible_subtasks if s['erledigt'])
```

---

## Implementation Plan

### Phase 1: Fix Cache-Busting in Student Views ✅ PRIORITY

**Files to modify:**
1. `templates/student/klasse.html`
2. Consider adding Cache-Control headers (as per todo.md line 32)

**Changes:**

#### Fix 1: Uncheck handler (line 291)
```javascript
// OLD
else {
    // Unchecking - reload page to reset state
    setTimeout(() => location.reload(), 100);
}

// NEW
else {
    // Unchecking - reload with cache-busting
    setTimeout(() => {
        const url = new URL(window.location);
        url.searchParams.set('_t', Date.now());
        window.location.href = url.toString();
    }, 100);
}
```

#### Fix 2: Next button (line 318)
```javascript
// OLD
function goToNextIncomplete() {
    location.reload();
}

// NEW
function goToNextIncomplete() {
    const url = new URL(window.location);
    url.searchParams.set('_t', Date.now());
    window.location.href = url.toString();
}
```

**Testing**: After fix, progress dots should update correctly on first try.

---

### Phase 2: Fix Visible Subtask Counts

**Files to modify:**
1. `app.py` - Dashboard route (around line 1228)
2. `app.py` - Student klasse route (already uses visible subtasks, verify counts)

#### Fix 1: Dashboard Progress Count

**Current code** (`app.py` line 1228-1229):
```python
subtasks = models.get_student_subtask_progress(task['id'])
task['total_subtasks'] = len(subtasks)
task['completed_subtasks'] = sum(1 for s in subtasks if s['erledigt'])
```

**New code**:
```python
# Get ALL subtasks for completion check
all_subtasks = models.get_student_subtask_progress(task['id'])

# Get VISIBLE subtasks for progress display
visible_subtasks = models.get_visible_subtasks_for_student(
    student_id, klasse['id'], task['task_id']
)
visible_subtask_ids = {s['id'] for s in visible_subtasks}

# Filter all_subtasks to only visible ones
visible_with_progress = [s for s in all_subtasks if s['id'] in visible_subtask_ids]

task['total_subtasks'] = len(visible_with_progress)
task['completed_subtasks'] = sum(1 for s in visible_with_progress if s['erledigt'])
```

**Explanation:**
- Get all subtasks (needed for internal logic)
- Get visible subtask IDs from visibility system
- Filter to visible only
- Count only visible subtasks

#### Verify: Student Klasse View

**Check** `app.py` around line 1270-1290 (student_klasse route):
- Already uses `get_visible_subtasks_for_student()` for display
- Progress bar in template should already be correct
- If not, apply same fix

---

### Phase 3: Visual Current Task Indicator (Optional)

**Requirement** (todo.md line 30):
> "in the student view (next to 0 von 8 Aufgaben erledigt) the current task should have a visible margin or shadow to visually mark where students are"

**Interpretation**: Add visual emphasis to active subtask card.

**Implementation**:

`templates/student/klasse.html` - Add CSS class to active subtask:
```html
<div class="subtask-card {% if active_subtask and sub.id == active_subtask.id %}subtask-active{% endif %}">
```

`static/css/style.css` - Add styling:
```css
.subtask-active {
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    border: 2px solid var(--primary);
    margin: 1rem 0;
}
```

**Testing**: Active subtask should have blue border and shadow.

---

### Phase 4: Cache-Control Headers (Better Long-term Solution)

**Requirement** (todo.md line 32):
> "replace timestamp URL parameter cache-busting with Cache-Control headers"

**Implementation**:

Create decorator in `app.py`:
```python
def no_cache(f):
    """Decorator to prevent caching of route responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function
```

Apply to student routes:
```python
@app.route('/schueler/klasse/<int:klasse_id>')
@student_required
@no_cache  # Add this
def student_klasse(klasse_id):
    # ...
```

Then revert timestamp changes:
```javascript
// Becomes simple again
location.reload();
```

**Benefits:**
- Cleaner URLs (no `?_t=123456`)
- Server-controlled caching policy
- Works for all navigation (back button, etc.)

**Drawback:**
- Slightly more server load (always revalidates)

---

---

## Phase 5: Fix "Next" Button with Subtask Gaps (Test 10)

**Problem**: Clicking "next" after completing subtask goes to first uncompleted, not next uncompleted.

**Scenario**: Visible subtasks are [1, 2, 3, 6, 7, 8] (gap at 4, 5)
- Complete subtask 3 → click next
- **Current**: Goes to subtask 1 (first uncompleted)
- **Expected**: Goes to subtask 6 (next in sequence)

**Root Cause**: Template uses `subtasks|rejectattr('erledigt')|list|first` which always finds FIRST uncompleted, ignoring sequence.

### Solution A: Track Current Position (Recommended)

**Implementation**: Pass current subtask index to "next" button, find next uncompleted AFTER current position.

**Changes needed:**

#### 1. Template - Add current index to next button
`templates/student/klasse.html` line 128:
```html
<!-- OLD -->
<button class="action-button" id="next-button" style="display: none;" onclick="goToNextIncomplete()">

<!-- NEW -->
{% set current_index = subtasks.index(active_subtask) if active_subtask in subtasks else -1 %}
<button class="action-button" id="next-button" style="display: none;"
        onclick="goToNextIncomplete({{ current_index }})">
```

#### 2. JavaScript - Find next after current index
`templates/student/klasse.html` line 318:
```javascript
// OLD
function goToNextIncomplete() {
    location.reload();
}

// NEW
function goToNextIncomplete(currentIndex) {
    // Get all visible subtask IDs in order
    const subtaskIds = [{% for sub in subtasks %}{{ sub.id }}{% if not loop.last %}, {% endif %}{% endfor %}];

    // Find next uncompleted after current
    const completedDots = document.querySelectorAll('.progress-dots .dot.completed:not(.dot-quiz)');
    const completedSet = new Set();
    completedDots.forEach(dot => {
        const index = parseInt(dot.dataset.subtaskIndex);
        if (!isNaN(index)) completedSet.add(index);
    });

    // Find next uncompleted index after current
    let nextIndex = -1;
    for (let i = currentIndex + 1; i < subtaskIds.length; i++) {
        if (!completedSet.has(i)) {
            nextIndex = i;
            break;
        }
    }

    if (nextIndex === -1) {
        // No more incomplete after current, wrap to first incomplete
        for (let i = 0; i < currentIndex; i++) {
            if (!completedSet.has(i)) {
                nextIndex = i;
                break;
            }
        }
    }

    if (nextIndex !== -1) {
        // Navigate to next subtask with cache-busting
        const nextSubtaskId = subtaskIds[nextIndex];
        const url = new URL(window.location);
        url.searchParams.set('subtask_id', nextSubtaskId);
        url.searchParams.set('_t', Date.now());
        window.location.href = url.toString();
    } else {
        // All complete - just reload
        const url = new URL(window.location);
        url.searchParams.set('_t', Date.now());
        window.location.href = url.toString();
    }
}
```

#### 3. Progress dots - Add index data attribute
`templates/student/klasse.html` line 41:
```html
<!-- OLD -->
<div class="dot {% if sub.erledigt %}completed{% elif current_subtask and sub.id == current_subtask.id %}current{% endif %}"

<!-- NEW -->
<div class="dot {% if sub.erledigt %}completed{% elif current_subtask and sub.id == current_subtask.id %}current{% endif %}"
     data-subtask-index="{{ loop.index0 }}"
```

**Benefits:**
- Handles gaps correctly
- Maintains sequential navigation
- Wraps to beginning if no more uncompleted ahead

**Testing scenario**:
1. Visible subtasks: 1, 2, 3, 6, 7, 8
2. Complete 1, 2, 3
3. Click next → should go to 6 (not back to 1)
4. Complete 6, 7, 8
5. Click next → should wrap to first incomplete (or show completion)

### Solution B: Backend Navigation (Alternative)

Instead of client-side logic, pass `?next=true` parameter and let backend calculate next subtask.

**Pros**: Cleaner separation, server controls navigation
**Cons**: More complex backend logic, requires route changes

---

## Phase 6: Redesign Navigation Buttons (UX Enhancement)

**Goal**: Move prev/next buttons to sides of task content (book-page / swipe metaphor)

**Current design**: Buttons stacked vertically below task content
**New design**: Buttons flanking task content on desktop, below on mobile

### Visual Layout

**Desktop (>768px)**:
```
┌─────────────────────────────────────────┐
│  [←]  Task Description Content   [→]    │
│  Prev         (center)            Next   │
│                                          │
│       [Checkbox: Als erledigt]           │
└─────────────────────────────────────────┘
```

**Mobile (<768px)**:
```
┌───────────────────┐
│ Task Description  │
│     (center)      │
│                   │
│  [Als erledigt]   │
│  [← Prev] [Next →]│
└───────────────────┘
```

### Implementation

#### 1. HTML Structure
`templates/student/klasse.html` - Wrap content in flex container:

```html
<!-- OLD: Sequential layout -->
<div class="task-card">
    <div class="task-content">...</div>
    <button>Prev</button>
    <button>Next</button>
</div>

<!-- NEW: Flexbox with side buttons -->
<div class="task-navigation-wrapper">
    <!-- Previous button (left side) -->
    <button class="nav-button nav-prev" onclick="goToPrevIncomplete({{ current_index }})">
        <span class="nav-arrow">←</span>
        <span class="nav-label">Zurück</span>
    </button>

    <!-- Center content -->
    <div class="task-content-center">
        <div class="task-card">
            <!-- Task description -->
            <div class="task-content markdown-content">
                {{ active_subtask.beschreibung | markdown }}
            </div>

            <!-- Checkbox -->
            <div class="task-complete">
                <input type="checkbox" ...>
                <label>Als erledigt markieren</label>
            </div>

            <!-- Success banner (shown after completion) -->
            <div id="success-banner" style="display: none;">...</div>
        </div>
    </div>

    <!-- Next button (right side) -->
    <button class="nav-button nav-next" onclick="goToNextIncomplete({{ current_index }})">
        <span class="nav-arrow">→</span>
        <span class="nav-label">Weiter</span>
    </button>
</div>
```

#### 2. CSS Styling
`static/css/style.css` - Add responsive navigation styles:

```css
/* Navigation wrapper - Desktop flexbox */
.task-navigation-wrapper {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin: 2rem 0;
}

/* Navigation buttons - Side placement */
.nav-button {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    padding: 1rem 0.75rem;
    background: var(--gray-100);
    border: 2px solid var(--gray-300);
    border-radius: 0.5rem;
    cursor: pointer;
    transition: all 0.2s;
    min-width: 80px;
    flex-shrink: 0;
}

.nav-button:hover {
    background: var(--primary);
    border-color: var(--primary);
    color: white;
    transform: translateX(0);
}

.nav-prev:hover {
    transform: translateX(-4px); /* Subtle shift left */
}

.nav-next:hover {
    transform: translateX(4px); /* Subtle shift right */
}

.nav-button:disabled {
    opacity: 0.3;
    cursor: not-allowed;
    background: var(--gray-100);
    border-color: var(--gray-300);
    color: var(--gray-500);
}

.nav-button:disabled:hover {
    transform: none;
}

/* Arrow - Large and visible */
.nav-arrow {
    font-size: 2rem;
    line-height: 1;
}

/* Label - Small helper text */
.nav-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    opacity: 0.8;
}

/* Center content - Takes remaining space */
.task-content-center {
    flex: 1;
    min-width: 0; /* Allow flex shrinking */
}

/* Mobile: Stack vertically */
@media (max-width: 768px) {
    .task-navigation-wrapper {
        flex-direction: column;
        align-items: stretch;
    }

    .nav-button {
        flex-direction: row;
        justify-content: center;
        width: 100%;
        padding: 1rem;
    }

    /* Reverse order: content, then buttons */
    .task-content-center {
        order: 1;
    }

    .nav-prev {
        order: 2;
    }

    .nav-next {
        order: 3;
    }

    /* Buttons side-by-side on mobile */
    .nav-prev,
    .nav-next {
        width: calc(50% - 0.5rem);
    }

    /* Container for mobile buttons */
    .task-navigation-wrapper {
        gap: 0.5rem;
    }
}
```

#### 3. JavaScript - Add Previous Navigation
`templates/student/klasse.html` - Add `goToPrevIncomplete()`:

```javascript
function goToPrevIncomplete(currentIndex) {
    // Get all visible subtask IDs in order
    const subtaskIds = [{% for sub in subtasks %}{{ sub.id }}{% if not loop.last %}, {% endif %}{% endfor %}];

    // Get completed set
    const completedDots = document.querySelectorAll('.progress-dots .dot.completed:not(.dot-quiz)');
    const completedSet = new Set();
    completedDots.forEach(dot => {
        const index = parseInt(dot.dataset.subtaskIndex);
        if (!isNaN(index)) completedSet.add(index);
    });

    // Find previous uncompleted before current
    let prevIndex = -1;
    for (let i = currentIndex - 1; i >= 0; i--) {
        if (!completedSet.has(i)) {
            prevIndex = i;
            break;
        }
    }

    if (prevIndex === -1) {
        // No incomplete before current, wrap to last incomplete
        for (let i = subtaskIds.length - 1; i > currentIndex; i--) {
            if (!completedSet.has(i)) {
                prevIndex = i;
                break;
            }
        }
    }

    if (prevIndex !== -1) {
        // Navigate to previous subtask with cache-busting
        const prevSubtaskId = subtaskIds[prevIndex];
        const url = new URL(window.location);
        url.searchParams.set('subtask_id', prevSubtaskId);
        url.searchParams.set('_t', Date.now());
        window.location.href = url.toString();
    }
}
```

#### 4. Button State Management
Show/hide and enable/disable based on position:

```javascript
// On page load - set button states
document.addEventListener('DOMContentLoaded', function() {
    const currentIndex = {{ current_index }};
    const totalSubtasks = {{ subtasks|length }};

    // Disable prev if first
    if (currentIndex === 0) {
        document.querySelector('.nav-prev').disabled = true;
    }

    // Disable next if last
    if (currentIndex === totalSubtasks - 1) {
        document.querySelector('.nav-next').disabled = true;
    }
});
```

### Benefits

**UX improvements:**
- Natural "page turning" metaphor
- Less scrolling (buttons always visible)
- Touch-friendly (large click targets on sides)
- Spatial memory (left = back, right = forward)

**Accessibility:**
- Keyboard navigation still works
- Large touch targets (80px min)
- Clear labels + arrow icons

**Responsive:**
- Desktop: Flanking buttons don't crowd content
- Mobile: Stacks below, full width buttons

### Testing
- [ ] Desktop: Buttons on left/right, content centered
- [ ] Desktop: Hover effects (subtle shift + color)
- [ ] Mobile: Buttons below content, side-by-side
- [ ] Navigation works in both directions
- [ ] Disabled state when at first/last subtask

---

## Testing Checklist

### Test 9 (After Phase 1)
- [ ] Complete subtask 1, click next → dots update immediately
- [ ] Complete subtask 2, click next → both dots green
- [ ] Uncheck subtask → state resets immediately
- [ ] No stale state on first reload

### Test 8.3 (After Phase 2)
- [ ] Dashboard shows "3/4" not "3/8" when 4 visible
- [ ] Klasse view progress matches visible count
- [ ] Completing visible subtask updates count correctly

### Phase 3 (Optional)
- [ ] Active subtask has visible border/shadow
- [ ] Easy to identify current position

### Test 10 (After Phase 5)
- [ ] Complete subtasks 1, 2, 3 with gaps at 4, 5
- [ ] Click next → goes to subtask 6 (not back to 1)
- [ ] Complete 6, 7 → click next → goes to 8
- [ ] Complete 8 → all done or wraps correctly

### Phase 4 (Future)
- [ ] URLs clean (no timestamp params)
- [ ] Caching still prevented
- [ ] Back button works correctly

---

## Implementation Order

**Immediate (Phase 1)**: Fix cache-busting - critical for Test 9
**Next (Phase 2)**: Fix counts - needed for Test 8.3
**Optional (Phase 3)**: Visual indicator - UX improvement
**Future (Phase 4)**: Cache-Control headers - cleanup/optimization

---

## Estimated Time

- Phase 1: 15 minutes (2 simple JS changes)
- Phase 2: 30 minutes (backend logic + testing)
- Phase 3: 15 minutes (CSS + template)
- Phase 4: 45 minutes (decorator + route updates + revert JS)

**Total**: ~2 hours for complete solution

---

## Related Files Reference

| File | Purpose | Changes Needed |
|------|---------|----------------|
| `templates/student/klasse.html` | Student subtask view | Cache-busting in JS (Phase 1, 4) |
| `app.py` | Backend routes | Fix counts in dashboard route (Phase 2) |
| `static/css/style.css` | Styling | Active subtask indicator (Phase 3) |
| `models.py` | Database layer | No changes needed (already has functions) |

---

## Notes

- Phase 1 is identical fix to admin view (same root cause)
- Phase 2 leverages existing `get_visible_subtasks_for_student()` function
- Phase 4 is cleaner but requires more testing (affects all routes)
- See `frontend_patterns.md` for detailed cache-busting patterns
