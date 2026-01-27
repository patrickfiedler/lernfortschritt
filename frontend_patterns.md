# Frontend Patterns and Common Issues

This document captures important patterns, gotchas, and solutions for frontend development in Lernmanager.

## Template Inheritance Issues

### Problem: Nested Script Tags Breaking JavaScript

**Symptom**: JavaScript functions undefined, `ReferenceError: functionName is not defined`

**Root Cause**:
- `templates/base.html` wraps `{% block scripts %}` with `<script>` tags
- Child templates that include their own `<script>` tags create nested structure
- Browsers see: `<script><script>code</script></script>` which is invalid

**Example of WRONG approach**:
```html
{% block scripts %}
<script>
function myFunction() {
    // This won't work!
}
</script>
{% endblock %}
```

**Correct approach**:
```html
{% block scripts %}
function myFunction() {
    // Code here is wrapped by base.html's <script> tags
}
{% endblock %}
```

**CSS in templates**: Always put CSS in `{% block content %}` with inline `<style>` tags, never in `{% block scripts %}`.

---

## Browser Caching After AJAX Operations

### Problem: Stale Data After Save-and-Reload

**Symptom**:
- AJAX save succeeds (200 OK)
- Page reloads automatically
- Old data still displayed
- Manual reload shows correct data

**Root Cause**:
- Browser caches GET requests by URL
- `location.reload()` may serve cached response
- Server has new data, but browser doesn't fetch it

**Wrong approach**:
```javascript
fetch('/api/save', {method: 'POST', body: data})
    .then(() => location.reload()); // May serve cache
```

**Correct approach** - Cache-busting with timestamp:
```javascript
fetch('/api/save', {method: 'POST', body: data})
    .then(() => {
        const url = new URL(window.location);
        url.searchParams.set('_t', Date.now());
        window.location.href = url.toString(); // Forces fresh fetch
    });
```

**Why this works**: Browser treats `?_t=1738056123` as different URL than `?_t=1738056456`, bypassing cache.

**Alternative** - POST-Redirect-GET pattern:
```python
# Backend returns redirect instead of JSON
return redirect(url_for('view_page', _external=False, _anchor=None))
```

---

## Unsaved Changes Detection

### Problem: False "Unsaved Changes" Warning on Reload

**Symptom**:
- Save succeeds
- Page tries to reload
- Browser shows: "Are you sure you want to leave?"
- Blocks automatic reload

**Root Cause**:
1. JavaScript tracks `initialState` on page load
2. User makes changes, `hasUnsavedChanges = true`
3. Save succeeds, but `initialState` not updated
4. `beforeunload` listener still sees differences
5. Browser blocks reload

**Wrong approach**:
```javascript
function save() {
    fetch('/save', {method: 'POST', body: data})
        .then(() => {
            hasUnsavedChanges = false; // Not enough!
            location.reload();
        });
}
```

**Correct approach** - Update tracking state:
```javascript
function save() {
    fetch('/save', {method: 'POST', body: data})
        .then(() => {
            // Update initialState to current state
            document.querySelectorAll('.my-checkbox').forEach(checkbox => {
                initialState[checkbox.id] = checkbox.checked;
            });

            // Clear flag and warning
            hasUnsavedChanges = false;
            document.getElementById('warning').style.display = 'none';

            // Now safe to reload
            location.reload();
        });
}
```

**Pattern setup**:
```javascript
let initialState = {};
let hasUnsavedChanges = false;

document.addEventListener('DOMContentLoaded', function() {
    // Capture initial state
    document.querySelectorAll('.tracked-input').forEach(input => {
        initialState[input.id] = input.value;
    });

    // Detect changes
    document.querySelectorAll('.tracked-input').forEach(input => {
        input.addEventListener('change', checkForUnsavedChanges);
    });

    // Warn before leaving
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = '';
            return '';
        }
    });
});

function checkForUnsavedChanges() {
    hasUnsavedChanges = false;
    document.querySelectorAll('.tracked-input').forEach(input => {
        if (input.value !== initialState[input.id]) {
            hasUnsavedChanges = true;
        }
    });
}
```

---

## Combined Pattern: Save with Reload

Complete working example combining all patterns:

```javascript
// Track state
let initialState = {};
let hasUnsavedChanges = false;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tracking
    document.querySelectorAll('.form-field').forEach(field => {
        initialState[field.id] = field.value;
    });

    // Listen for changes
    document.querySelectorAll('.form-field').forEach(field => {
        field.addEventListener('change', checkForUnsavedChanges);
    });

    // Warn before navigation
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = '';
            return '';
        }
    });
});

function checkForUnsavedChanges() {
    hasUnsavedChanges = false;
    document.querySelectorAll('.form-field').forEach(field => {
        if (field.value !== initialState[field.id]) {
            hasUnsavedChanges = true;
        }
    });

    const warning = document.getElementById('unsaved-warning');
    warning.style.display = hasUnsavedChanges ? 'block' : 'none';
}

function saveForm() {
    const saveBtn = document.getElementById('save-btn');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Speichert...';

    // Collect form data
    const formData = {};
    document.querySelectorAll('.form-field').forEach(field => {
        formData[field.id] = field.value;
    });

    // Save to backend
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    fetch('/api/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update tracking state to prevent warning
            document.querySelectorAll('.form-field').forEach(field => {
                initialState[field.id] = field.value;
            });
            hasUnsavedChanges = false;
            document.getElementById('unsaved-warning').style.display = 'none';

            // Show success briefly
            saveBtn.textContent = '✅ Gespeichert!';

            // Reload with cache-busting after delay
            setTimeout(() => {
                const url = new URL(window.location);
                url.searchParams.set('_t', Date.now());
                window.location.href = url.toString();
            }, 500);
        } else {
            alert('Fehler: ' + data.message);
            saveBtn.disabled = false;
            saveBtn.textContent = 'Speichern';
        }
    })
    .catch(error => {
        alert('Netzwerkfehler: ' + error);
        saveBtn.disabled = false;
        saveBtn.textContent = 'Speichern';
    });
}
```

---

## Debugging Tips

### Check Template Block Structure
Look for duplicate script/style tags:
```bash
grep -n "<script>" templates/your_template.html
# Should only appear in base.html, not child templates
```

### Test Cache Behavior
```javascript
// Add to see if reload bypasses cache
console.log('Page loaded at:', new Date().toISOString());
```

### Verify State Tracking
```javascript
// Add to checkForUnsavedChanges()
console.log('Initial:', initialState);
console.log('Current:', getCurrentState());
console.log('Has changes:', hasUnsavedChanges);
```

### Check Network Cache
- Open DevTools → Network tab
- Enable "Disable cache" checkbox
- Test if issue persists
- If it works with cache disabled → cache-busting needed

---

## Real-World Issues Fixed

### Issue 1: Subtask Management Template (Jan 2026)
**File**: `templates/admin/teilaufgaben_verwaltung.html`

**Problems**:
1. Nested `<script>` tags broke JavaScript functions
2. Badge state not updating after AJAX save
3. "Unsaved changes" warning blocking reload

**Solutions**:
1. Removed `<script>` wrapper from `{% block scripts %}`
2. Added cache-busting: `url.searchParams.set('_t', Date.now())`
3. Updated `initialState` before reload

**Commits**: See task_plan.md Errors #2, #3, #4

### Similar Issues in Student View
User reported similar caching behavior in student interface. If updating student view with AJAX saves, apply same cache-busting pattern.

---

## Responsive Button Layout with Separate Mobile Wrapper

### Problem: Mobile Navigation Buttons Stack Vertically Instead of Horizontally

**Symptom**:
- Desktop: Buttons correctly positioned on left and right sides of content
- Mobile: Buttons stack vertically (one above content, one below)
- Expected: Two buttons side-by-side below content on mobile

**Root Cause**:
1. Flexbox `flex-direction: column` on parent forces vertical stacking
2. Float-based layout fails due to HTML element order (prev → content → next)
3. Buttons flow around content instead of grouping below it

**Wrong approach #1** - Try to reorder with CSS:
```css
/* Doesn't work - can't change visual order reliably with floats */
.nav-prev { float: left; }
.nav-next { float: right; }
```

**Wrong approach #2** - Complex flexbox ordering:
```css
/* Fragile, breaks with dynamic content */
.nav-prev { order: 1; }
.content { order: 2; }
.nav-next { order: 3; }
```

**Correct approach** - Separate mobile button wrapper:

Create duplicate button set for mobile, hide/show appropriately:

**HTML Structure**:
```html
<div class="task-navigation-wrapper">
    <!-- Desktop: Left button -->
    <button class="nav-button-side nav-prev">←</button>

    <!-- Content (center on desktop, full width on mobile) -->
    <div class="current-task">...</div>

    <!-- Desktop: Right button -->
    <button class="nav-button-side nav-next">→</button>

    <!-- Mobile: Button wrapper (after content) -->
    <div class="nav-buttons-mobile">
        <button class="nav-button-side nav-prev">←</button>
        <button class="nav-button-side nav-next">→</button>
    </div>
</div>
```

**CSS Implementation**:
```css
/* Desktop layout - flexbox with side buttons */
.task-navigation-wrapper {
    display: flex;
    align-items: flex-start;
    gap: 1.5rem;
}

/* Hide mobile wrapper on desktop */
.nav-buttons-mobile {
    display: none;
}

/* Mobile layout */
@media (max-width: 768px) {
    .task-navigation-wrapper {
        flex-direction: column;
    }

    /* Hide desktop side buttons */
    .task-navigation-wrapper > .nav-button-side {
        display: none;
    }

    /* Show mobile wrapper with horizontal layout */
    .nav-buttons-mobile {
        display: flex;
        gap: 1rem;
        margin-top: 1.5rem;
        width: 100%;
    }

    /* Each button takes 50% width */
    .nav-buttons-mobile .nav-button-side {
        flex: 1;
    }
}
```

**Why this works**:
- Desktop: Original buttons visible, wrapper hidden
- Mobile: Original buttons hidden, wrapper buttons visible
- Clean separation of concerns
- No layout fighting between desktop/mobile

**Trade-offs**:
- ✅ Simple, maintainable CSS
- ✅ Works across all screen sizes
- ✅ No JavaScript required
- ⚠️ Button HTML duplicated (minor)

**Alternative considered** - CSS Grid:
Could work, but flexbox is simpler for this use case and already in use.

---

## Related Patterns

### POST-Redirect-GET (Alternative to AJAX+Reload)
Instead of AJAX save + manual reload, use traditional form POST:
```python
@app.route('/save', methods=['POST'])
def save():
    # Save data
    flash('Gespeichert!', 'success')
    return redirect(url_for('view_page'))
```

**Pros**: No cache issues, no manual reload
**Cons**: Full page refresh, no partial updates

### Optimistic UI Updates
Update UI immediately, rollback on error:
```javascript
// Update UI optimistically
badge.textContent = 'Individuell';
badge.className = 'badge badge-primary';

fetch('/save', {method: 'POST', body: data})
    .catch(error => {
        // Rollback on error
        badge.textContent = 'Vererbt';
        badge.className = 'badge badge-secondary';
        alert('Fehler beim Speichern');
    });
```

**When to use**: Fast feedback, rare failures expected
