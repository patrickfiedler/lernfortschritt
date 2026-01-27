# Subtask Visibility Testing Plan

## Test Environment
- **Server**: http://127.0.0.1:5000
- **Status**: Flask development server running
- **Database**: data/mbi_tracker.db (with subtask_visibility table)

---

## Phase 6 Testing Checklist

### ✅ Pre-Flight Checks (Automated)
- [x] Database migration successful
- [x] subtask_visibility table exists with indexes
- [x] Flask app starts without errors
- [ ] All routes respond (no 404/500 errors)
- [ ] Models functions work without errors

### 🔧 Admin Testing

#### Test 1: Task Assignment → Redirect to Config (Q1A)
**Steps**:
1. Login as admin
2. Go to class detail page
3. Assign a task to the class
4. **Expected**: Redirect to `/admin/teilaufgaben-verwaltung/klasse/<id>?task_id=<id>`
5. **Expected**: Flash message: "Aufgabe zugewiesen. Bitte wähle nun die sichtbaren Teilaufgaben. ✅"

**Verification**:
- [ ] Redirect happens automatically
- [ ] Configuration page loads
- [ ] Flash message appears
- [ ] Checkboxes are all unchecked (Q1: no subtasks enabled by default)

#### Test 2: Class-Wide Subtask Configuration
**Steps**:
1. On configuration page for class
2. See list of all subtasks with checkboxes
3. Check subtasks 1, 2, 3
4. Click "💾 Änderungen speichern"
5. **Expected**: Button shows "Speichert..." then "✅ Gespeichert!"
6. Reload page
7. **Expected**: Subtasks 1, 2, 3 still checked

**Verification**:
- [ ] All subtasks displayed as checkboxes
- [ ] Checkboxes are interactive
- [ ] Save button works
- [ ] Visual feedback on save
- [ ] Settings persist after reload
- [ ] Database has 3 rows in subtask_visibility with klasse_id

#### Test 3: Bulk Actions - Enable/Disable All (Q4B)
**Steps**:
1. On class configuration page
2. Click "✅ Alle aktivieren"
3. **Expected**: All checkboxes checked
4. Click "Änderungen speichern"
5. **Expected**: All subtasks saved as enabled
6. Click "❌ Alle deaktivieren"
7. **Expected**: All checkboxes unchecked
8. Click "Änderungen speichern"
9. **Expected**: All subtasks saved as disabled

**Verification**:
- [ ] "Alle aktivieren" checks all boxes
- [ ] "Alle deaktivieren" unchecks all boxes
- [ ] Both actions save correctly
- [ ] Q4B: Only current subtasks affected (not future ones)

#### Test 4: Student-Specific Overrides (Q2B Two-Column)
**Steps**:
1. Login as admin
2. Go to student detail page
3. Click link to subtask configuration for student
4. **Expected**: Two-column layout
   - Left: Class settings (read-only)
   - Right: Student overrides (editable)
5. Enable subtask 4 for this student (not enabled for class)
6. Disable subtask 2 for this student (enabled for class)
7. Click "Änderungen speichern"
8. **Expected**: Settings saved with badges showing "Individuell"

**Verification**:
- [ ] Two-column layout displays
- [ ] Left column shows class settings (checkboxes disabled)
- [ ] Right column shows student settings (checkboxes enabled)
- [ ] Badges show "Vererbt" for inherited settings
- [ ] Badges show "Individuell" for custom settings
- [ ] Student overrides save correctly
- [ ] Database has rows with student_id (not klasse_id)

#### Test 5: Reset to Class Default
**Steps**:
1. On student configuration page with overrides
2. Click "🔄 Auf Klassenstandard zurücksetzen"
3. Confirm in dialog
4. **Expected**: Page reloads, all overrides removed
5. **Expected**: Student sees same subtasks as class

**Verification**:
- [ ] Confirmation dialog appears
- [ ] Page reloads after reset
- [ ] All student-specific rows deleted from database
- [ ] Student settings match class settings

#### Test 6: Unsaved Changes Warning
**Steps**:
1. On configuration page
2. Check/uncheck some boxes
3. **Expected**: Warning banner appears: "⚠️ Du hast ungespeicherte Änderungen!"
4. Try to leave page (back button, link click)
5. **Expected**: Browser warning: "Leave site? Changes you made may not be saved"

**Verification**:
- [ ] Warning banner shows on changes
- [ ] Warning banner hides after save
- [ ] Browser beforeunload warning works

---

### 👤 Student Testing

#### Test 7: Visible Subtasks Display (Q5A, Q6A)
**Steps**:
1. Login as student
2. Go to class page with assigned task
3. **Expected**: See only subtasks enabled by admin
4. **Expected**: Progress shows "X of Y" where Y = visible subtasks only

**Scenario A - Class settings only**:
- Class has subtasks 1, 2, 3 enabled (out of 10 total)
- Student sees: 3 subtasks
- Progress: "0 of 3 complete"

**Scenario B - Student override**:
- Class has subtasks 1, 2, 3 enabled
- This student has subtask 4 also enabled
- Student sees: 4 subtasks (1, 2, 3, 4)
- Progress: "0 of 4 complete"

**Verification**:
- [ ] Only visible subtasks displayed
- [ ] Hidden subtasks not shown at all
- [ ] Progress calculation correct (Q5A)
- [ ] Navigation buttons work with visible subtasks

#### Test 8: Empty State (Q3B)
**Steps**:
1. Admin assigns task but enables NO subtasks
2. Student goes to class page
3. **Expected**: Encouraging empty state:
   ```
   ✨ (animated)
   Weitere Aufgaben kommen bald!
   Dein Lehrer bereitet sie vor.
   ```

**Verification**:
- [ ] Empty state displays (not error message)
- [ ] Sparkle emoji floats (animation)
- [ ] Positive, encouraging copy
- [ ] Blue gradient background

#### Test 9: Progress Matches Visible (Q5A)
**Steps**:
1. Task has 10 total subtasks
2. Admin enables 3 for class
3. Student completes 2 of 3 visible subtasks
4. **Expected**: Progress shows "2 of 3 (67%)" NOT "2 of 10 (20%)"

**Verification**:
- [ ] Progress text shows visible count
- [ ] Progress dots show visible count
- [ ] Percentage calculated from visible only

#### Test 10: Task Completion (Q5A)
**Steps**:
1. Task has 10 total subtasks
2. Admin enables 3 for student
3. Student completes all 3 visible subtasks
4. Student passes quiz (if exists)
5. **Expected**: Task marked as complete
6. **Expected**: Student sees completion message

**Verification**:
- [ ] Task completes when all visible done (not all 10)
- [ ] Hidden subtasks don't block completion
- [ ] check_task_completion() works correctly

---

### 🐛 Edge Case Testing

#### Edge Case 1: Task with No Subtasks
**Steps**:
1. Create task without any subtasks
2. Assign to class
3. Go to configuration page
4. **Expected**: Message: "Diese Aufgabe hat noch keine Teilaufgaben."

**Verification**:
- [ ] Empty state shown in admin UI
- [ ] No errors thrown
- [ ] Helpful message displayed

#### Edge Case 2: All Subtasks Disabled
**Steps**:
1. Admin disables all subtasks for class
2. Student goes to class page
3. **Expected**: Empty state (Q3B)

**Verification**:
- [ ] Shows encouraging empty state
- [ ] No error message
- [ ] Student can't see disabled subtasks

#### Edge Case 3: Student Not in Class
**Steps**:
1. Try to access student config for wrong class
2. **Expected**: Authorization check fails
3. **Expected**: Redirect with error message

**Verification**:
- [ ] Authorization works
- [ ] No unauthorized access
- [ ] Error message shown

#### Edge Case 4: Task Not Assigned
**Steps**:
1. Try to configure subtasks for unassigned task
2. **Expected**: Error or empty state

**Verification**:
- [ ] Handles gracefully
- [ ] No crashes

#### Edge Case 5: Concurrent Edits
**Steps**:
1. Open config page in two tabs
2. Save different settings in each
3. **Expected**: Last save wins (no data corruption)

**Verification**:
- [ ] No database errors
- [ ] Last save persists
- [ ] No orphaned rows

---

### 🔍 Database Verification

#### Check 1: Subtask Visibility Table
**Query**:
```sql
SELECT * FROM subtask_visibility;
```

**Expected**:
- Rows with klasse_id (class-wide rules)
- Rows with student_id (individual overrides)
- No rows with both klasse_id AND student_id
- enabled column has 0 or 1
- set_at timestamp populated
- set_by_admin_id populated

**Verification**:
- [ ] Table structure correct
- [ ] Constraints working (CHECK clause)
- [ ] Data format correct
- [ ] Indexes exist

#### Check 2: Query Performance
**Test**:
```python
import time
start = time.time()
models.get_visible_subtasks_for_student(student_id, klasse_id, task_id)
elapsed = time.time() - start
print(f"Query took {elapsed*1000:.2f}ms")
```

**Expected**: < 50ms for typical dataset

**Verification**:
- [ ] Queries are fast (indexes used)
- [ ] No N+1 query problems
- [ ] Scales with data size

---

### 📱 UI/UX Testing

#### UI Test 1: Responsive Design
**Steps**:
1. Resize browser to mobile width (< 768px)
2. Check configuration page
3. **Expected**: Two-column layout stacks vertically

**Verification**:
- [ ] Mobile layout works
- [ ] Buttons are touch-friendly
- [ ] Text readable on small screens

#### UI Test 2: Visual Feedback
**Steps**:
1. Check/uncheck boxes
2. Hover over subtask items
3. Click save button
4. **Expected**: All interactions have visual feedback

**Verification**:
- [ ] Hover effects work
- [ ] Active states clear
- [ ] Loading states shown
- [ ] Success states shown

#### UI Test 3: Accessibility
**Steps**:
1. Tab through checkboxes
2. Use keyboard to check/uncheck
3. Screen reader simulation

**Verification**:
- [ ] Keyboard navigation works
- [ ] Focus visible
- [ ] Labels associated with inputs

---

## Automated Test Script

Run this to verify basic functionality:

```python
# test_subtask_visibility.py
import models

# Test 1: Get visible subtasks (empty initially)
visible = models.get_visible_subtasks_for_student(1, 1, 1)
assert visible == [], f"Expected empty, got {visible}"

# Test 2: Enable subtask for class
models.set_subtask_visibility_for_class(1, 1, True, 1)
visible = models.get_visible_subtasks_for_student(1, 1, 1)
assert len(visible) == 1, f"Expected 1, got {len(visible)}"

# Test 3: Student override
models.set_subtask_visibility_for_student(1, 2, True, 1)
visible = models.get_visible_subtasks_for_student(1, 1, 1)
assert len(visible) == 2, f"Expected 2, got {len(visible)}"

# Test 4: Disable class subtask (student override takes precedence)
models.set_subtask_visibility_for_class(1, 1, False, 1)
visible = models.get_visible_subtasks_for_student(1, 1, 1)
# Should still see subtask 2 (student override)
assert any(s['id'] == 2 for s in visible), "Student override not working"

print("✅ All tests passed!")
```

---

## Manual Testing Checklist for Patrick

After I run automated tests, please manually verify:

### Admin Flow:
1. [ ] Assign task → redirects to config (Q1A)
2. [ ] Check boxes → save → persist
3. [ ] Enable all → save → all enabled
4. [ ] Student config → two columns (Q2B)
5. [ ] Student override → save → badges show "Individuell"
6. [ ] Reset to class → overrides removed

### Student Flow:
1. [ ] See only enabled subtasks
2. [ ] Progress shows visible count (Q5A)
3. [ ] Empty state when no subtasks (Q3B)
4. [ ] Complete visible subtasks → task completes
5. [ ] Hidden subtasks truly hidden

### Bugs to Watch For:
- [ ] JavaScript errors in console
- [ ] CSRF token errors on save
- [ ] Database errors in Flask log
- [ ] Progress calculation wrong
- [ ] Empty state not showing
- [ ] Two-column layout broken

---

**Status**: Ready for testing with credentials
**Next**: Share admin + student credentials for manual testing
