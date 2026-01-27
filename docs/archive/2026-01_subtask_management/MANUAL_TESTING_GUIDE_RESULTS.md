# Manual Testing Guide - Subtask Visibility

## 🎯 Test Results Summary

### ✅ Automated Tests: 10/10 PASSED

All backend functionality working correctly:
- Visibility rules work
- Student overrides function properly
- Task completion uses visible subtasks only (Q5A)
- Bulk operations work
- Reset to class default works

### ⚠️ Manual Testing Needed

The automated tests verify the **backend logic** works. Now we need to verify the **user interface** works correctly in a real browser.

---

## 🧪 Quick Test Scenarios (15 minutes)

### Test 1: Admin Task Assignment → Redirect (Q1A)

**Goal**: Verify Q1A implementation - assignment redirects to config page

**Steps**:
1. Go to http://127.0.0.1:5000
2. Login as admin: `admin` / `admin`
3. Click "Klassen" in navigation
4. Click on a class name
5. In "Aufgabe für alle zuweisen" section:
   - Select a task from dropdown
   - Click "Zuweisen"

**Expected Result**:
- ✅ Redirects to `/admin/teilaufgaben-verwaltung/klasse/<id>?task_id=<id>`
- ✅ Flash message: "Aufgabe zugewiesen. Bitte wähle nun die sichtbaren Teilaufgaben. ✅"
- ✅ Shows subtask configuration page
- ✅ All checkboxes UNCHECKED (Q1: no subtasks enabled by default)

**Status**: [ ] Pass [x] Fail

**Error Message**:
- Both success "Aufgabe zugewiesen. Bitte wähle nun die sichtbaren Teilaufgaben. ✅" and error "Ein unerwarteter Fehler ist aufgetreten. Der Fehler wurde protokolliert." appear.
- App redirects to http://localhost:5000/admin dashboard

---

### Test 2: Enable Subtasks for Class

**Goal**: Verify checkbox interface and save functionality

**Steps** (continue from Test 1):
1. You should be on subtask config page
2. Check boxes for subtasks 1, 2, 3
3. Click "💾 Änderungen speichern"

**Expected Result**:
- ✅ Button text changes to "Speichert..."
- ✅ Then changes to "✅ Gespeichert!" (green)
- ✅ After 2 seconds, returns to normal
- ✅ Reload page - checkboxes still checked

**Browser Console**:
- ✅ No JavaScript errors
- ✅ POST request to `/admin/teilaufgaben-verwaltung/speichern`
- ✅ Response: `{"success": true, ...}`

**Status**: [ ] Pass [ ] Fail

---

### Test 3: Bulk Actions (Q4B)

**Goal**: Verify "Enable All" and "Disable All" buttons

**Steps**:
1. On subtask config page
2. Click "❌ Alle deaktivieren"
3. Observe: All checkboxes unchecked
4. Click "✅ Alle aktivieren"
5. Observe: All checkboxes checked
6. Click "Änderungen speichern"

**Expected Result**:
- ✅ All checkboxes respond immediately
- ✅ Save persists all changes
- ✅ Q4B: Only current subtasks affected (not future ones if task updated later)

**Status**: [ ] Pass [ ] Fail

---

### Test 4: Unsaved Changes Warning

**Goal**: Verify warning system works

**Steps**:
1. On subtask config page
2. Check/uncheck a box
3. DON'T save

**Expected Result**:
- ✅ Warning banner appears: "⚠️ Du hast ungespeicherte Änderungen!"
- ✅ Try to leave page (click back or link)
- ✅ Browser shows: "Leave site? Changes may not be saved"

**Steps to clear**:
4. Click "Änderungen speichern"
5. Warning banner disappears

**Status**: [ ] Pass [ ] Fail

---

### Test 5: Student Override (Q2B Two-Column Layout)

**Goal**: Verify two-column interface for individual students

**Steps**:
1. Go to "Schüler" (students) list
2. Click on a student name
3. Find a task assignment (or assign one)
4. Look for link to subtask configuration
   - **Note**: Link might need to be added manually to template
   - Or navigate directly: `/admin/teilaufgaben-verwaltung/schueler/<student_id>?task_id=<task_id>&klasse_id=<klasse_id>`

**Expected Result** (Q2B):
```
┌─────────────────────┬─────────────────────┐
│ Klasseneinstellung  │ Individuelle        │
│ (read-only)         │ (editable)          │
├─────────────────────┼─────────────────────┤
│ ☑ Subtask 1         │ ☑ Subtask 1 [Vererbt]│
│ ☑ Subtask 2         │ ☑ Subtask 2 [Vererbt]│
│ ☐ Subtask 3         │ ☐ Subtask 3 [Vererbt]│
└─────────────────────┴─────────────────────┘
```

**Actions**:
5. In right column, enable Subtask 3 (disabled for class)
6. In right column, disable Subtask 1 (enabled for class)
7. Click "Änderungen speichern"

**Expected Result**:
- ✅ Two columns side-by-side (desktop)
- ✅ Left column: checkboxes disabled (read-only preview)
- ✅ Right column: checkboxes enabled (editable)
- ✅ Badges show "Vererbt" for inherited, "Individuell" for custom
- ✅ After save, badges update correctly
- ✅ "Auf Klassenstandard zurücksetzen" button visible

**Status**: [ ] Pass [ ] Fail

---

### Test 6: Reset to Class Default

**Goal**: Verify reset button removes overrides

**Steps** (continue from Test 5):
1. Click "🔄 Auf Klassenstandard zurücksetzen"
2. Confirm in dialog

**Expected Result**:
- ✅ Confirmation dialog appears
- ✅ Page reloads
- ✅ Right column matches left column (all overrides removed)
- ✅ All badges show "Vererbt"

**Status**: [ ] Pass [ ] Fail

---

### Test 7: Student View - Visible Subtasks Only (Q5A, Q6A)

**Goal**: Verify students see only enabled subtasks

**Setup**:
1. As admin, enable subtasks 1, 2, 3 for a class (out of 5+ total)
2. Logout

**Steps**:
3. Login as student: `activehorse` / `nijata64`
4. Click on class with assigned task
5. View task page

**Expected Result** (Q5A, Q6A):
- ✅ See only 3 subtasks (1, 2, 3) - NOT all 5+
- ✅ Progress shows: "0 of 3 Aufgaben erledigt"
- ✅ Progress dots: Only 3 dots (not 5+)
- ✅ Hidden subtasks (4, 5, ...) completely invisible

**Status**: [ ] Pass [ ] Fail

---

### Test 8: Empty State (Q3B)

**Goal**: Verify encouraging empty state when no subtasks enabled

**Setup**:
1. As admin, assign a task to a class
2. On config page, disable ALL subtasks (uncheck all)
3. Save
4. Logout

**Steps**:
5. Login as student
6. Go to class page with that task

**Expected Result** (Q3B):
```
┌────────────────────────────────┐
│                                │
│         ✨ (floating)           │
│                                │
│  Weitere Aufgaben kommen bald! │
│  Dein Lehrer bereitet sie vor. │
│                                │
└────────────────────────────────┘
```

**Visual**:
- ✅ Blue gradient background
- ✅ Sparkle emoji animates (floats up and down)
- ✅ Positive, encouraging text
- ✅ NO error message or confusing fallback

**Status**: [ ] Pass [ ] Fail

---

### Test 9: Progress Matches Visible (Q5A)

**Goal**: Verify progress calculation uses visible subtasks only

**Setup**:
1. Task has 10 total subtasks
2. Admin enables only 3 for class
3. Student sees 3 subtasks

**Steps**:
4. As student, complete 2 of 3 visible subtasks

**Expected Result**:
- ✅ Progress: "2 of 3 Aufgaben erledigt" - NOT "2 of 10"
- ✅ Percentage: ~67% - NOT 20%
- ✅ Progress dots: 2 filled, 1 empty (only 3 dots total)

**Status**: [ ] Pass [ ] Fail

---

### Test 10: Task Completion (Q5A)

**Goal**: Verify task completes when all VISIBLE subtasks done

**Setup**:
1. Task has 10 total subtasks
2. Admin enables 3 for student
3. Task has no quiz (or quiz already passed)

**Steps**:
4. Student completes all 3 visible subtasks

**Expected Result**:
- ✅ Task marked as complete
- ✅ Hidden subtasks don't block completion
- ✅ Student sees completion message/indicator

**Status**: [ ] Pass [ ] Fail

---

## 🐛 Known Issues to Watch For

### Issue 1: CSRF Token Errors
**Symptom**: Save button fails with 400 Bad Request
**Check**: Browser console for CSRF errors
**Fix**: Ensure meta tag exists: `<meta name="csrf-token" content="...">`

### Issue 2: JavaScript Not Loading
**Symptom**: Buttons don't work, no visual feedback
**Check**: Browser console for 404 errors or syntax errors
**Fix**: Verify template extends base, scripts block exists

### Issue 3: Two-Column Layout Broken
**Symptom**: Columns stack or don't display side-by-side
**Check**: Browser width > 768px, CSS loaded
**Fix**: Check `subtask-columns` CSS class, grid template

### Issue 4: Empty State Not Showing
**Symptom**: Blank page or old error message
**Check**: `subtasks` variable is empty list (not None)
**Fix**: Verify template conditional: `{% if not subtasks %}`

### Issue 5: Progress Wrong
**Symptom**: Progress shows "2 of 10" instead of "2 of 3"
**Check**: Template uses `subtasks` not `all_subtasks`
**Fix**: Verify: `{{ subtasks|length }}` not `{{ all_subtasks|length }}`

---

## 📊 Final Checklist

After completing all tests above:

**Backend** ✅:
- [x] All models functions work
- [x] Visibility rules enforced
- [x] Student overrides work
- [x] Task completion correct

**Admin UI**:
- [ ] Assignment redirects to config (Q1A)
- [ ] Checkboxes display and save
- [ ] Bulk actions work (Q4B)
- [ ] Unsaved changes warning
- [ ] Two-column layout for students (Q2B)
- [ ] Reset to class default works

**Student UI**:
- [ ] See only visible subtasks (Q5A, Q6A)
- [ ] Empty state displays (Q3B)
- [ ] Progress matches visible (Q5A)
- [ ] Task completion works (Q5A)

**Browser Compatibility**:
- [ ] Chrome/Edge (tested)
- [ ] Firefox (tested)
- [ ] Safari (tested if available)
- [ ] Mobile responsive (< 768px width)

---

## 🎉 Success Criteria

**Feature is READY** when:
1. All 10 manual tests pass
2. No JavaScript console errors
3. UI looks correct on desktop and mobile
4. Students see correct subtasks
5. Progress calculations accurate

**Feature is COMPLETE** when:
1. Success criteria met
2. Documentation updated (CLAUDE.md)
3. Committed to git
4. Deployed to production (optional)

---

## 📝 Test Results

**Date**: _____________
**Tester**: Patrick
**Browser**: _____________
**Screen Size**: _____________

**Overall Result**: [ ] PASS [ ] FAIL

**Notes**:
```

```

**Bugs Found**:
```

```

**Screenshots** (if needed):
- Location: _____________
