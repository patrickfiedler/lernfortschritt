# UX Tier 1 - Quick Testing Checklist

## Before You Start

### 1. Run Migrations
```bash
cd /home/patrick/coding/Lernfortschritt
python migrate_add_time_estimates.py
python migrate_easy_reading_mode.py
```

**Expected output:** "Migration completed successfully!" for both

---

## Test 1: Mobile Touch Targets ⏱️ 2 min

- [ ] Open student task page
- [ ] Resize browser to <768px width (or use phone)
- [ ] Progress dots should be MUCH larger (44px vs 12px)
- [ ] Tap/click dots - should be easy to hit

**Visual check:** Dots go from tiny to finger-friendly

---

## Test 2: Keyboard Navigation ⏱️ 3 min

- [ ] Open student task page
- [ ] Press Tab until focus is on a progress dot
- [ ] Should see **blue outline** around dot
- [ ] Press → (right arrow) - focus moves to next dot
- [ ] Press ← (left arrow) - focus moves to previous dot
- [ ] Press Enter on a dot - navigates to that subtask

**Success:** Can navigate dots without mouse

---

## Test 3: Checkbox Text ⏱️ 1 min

- [ ] Open any student subtask
- [ ] Scroll to checkbox at bottom
- [ ] Label should read: **"Ich habe das geschafft! ✓"**
- [ ] NOT "Als erledigt markieren"

**Success:** New empowering text appears

---

## Test 4: Quiz Feedback ⏱️ 5 min

### Setup (if no quiz exists):
1. Login as admin
2. Create/edit a task with quiz (10 questions)
3. Assign to a student

### Test:
- [ ] Login as student
- [ ] Take quiz, answer 6/10 correct (60%)
- [ ] Should show: **"💪 Fast geschafft!"** (not "Nicht bestanden")
- [ ] Should say: "Du brauchst mindestens **70%**" (not 80%)
- [ ] Retake quiz, answer 7/10 correct (70%)
- [ ] Should show: **"🎉 Bestanden!"**
- [ ] Retake again, answer 8/10 correct (80%)
- [ ] Should show improvement: **"⭐ Du wirst besser! Beim letzten Mal: 7/10..."**

**Success:** Encouraging feedback + 70% threshold + improvement tracking

---

## Test 5: Time Estimates ⏱️ 5 min

### Setup:
1. Login as admin
2. Go to any task → Edit → Teilaufgaben section
3. You should see **number input fields** next to each subtask (placeholder: "Min")
4. Enter time estimates: 15, 20, 10, 25 (minutes)
5. Click "Speichern"

### Test:
- [ ] Login as student
- [ ] Open the task you edited
- [ ] Below "Aufgabe X von Y", should see **green badge**: "⏱️ ~15 Min"
- [ ] Navigate to next subtask - badge updates: "⏱️ ~20 Min"
- [ ] Subtasks without estimates show: "⏱️ ~15-30 Min"

**Success:** Time badges appear and update per subtask

---

## Test 6: Easy Reading Mode ⏱️ 3 min

- [ ] Login as student
- [ ] Click **"⚙️ Einstellungen"** in top navigation
- [ ] Check the box: "Lesemodus aktivieren"
- [ ] Click "Speichern"
- [ ] Page should reload with:
  - **Larger text** (18px vs 16px)
  - **Comic Sans font** (rounded, friendlier)
  - **More line spacing** (looks airier)
  - **Cream background** (#FAF4E8 instead of white)
- [ ] Navigate to task page - mode should **persist**
- [ ] Go back to settings, uncheck box - mode should **disable**

**Success:** Entire student interface changes style when enabled

---

## Test 7: Focus Indicators ⏱️ 2 min

- [ ] Open any page
- [ ] Press Tab repeatedly
- [ ] Every button, link, input should show **2px blue outline**
- [ ] Outline appears only on Tab (not on mouse click)

**Success:** Clear visual indicator for keyboard users

---

## Quick Visual Summary

| Feature | What to Look For | Pass? |
|---------|------------------|-------|
| Mobile dots | Big dots (44px) on narrow screen | ☐ |
| Keyboard nav | Arrow keys move between dots | ☐ |
| Focus outline | Blue ring on Tab | ☐ |
| Checkbox text | "Ich habe das geschafft! ✓" | ☐ |
| Quiz 70% | Passes at 7/10 correct | ☐ |
| Quiz feedback | Encouraging "Fast geschafft!" | ☐ |
| Time badges | Green "⏱️ ~X Min" on tasks | ☐ |
| Easy reading | Comic Sans + cream + big text | ☐ |

---

## If Something Doesn't Work

### Migrations didn't run?
```bash
# Check if columns exist
sqlite3 data/mbi_tracker.db "PRAGMA table_info(subtask);" | grep estimated_minutes
sqlite3 data/mbi_tracker.db "PRAGMA table_info(student);" | grep easy_reading_mode
```

### App won't start?
```bash
# Check for errors
python app.py
# Look for import errors or syntax errors
```

### CSS not loading?
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)
- Check browser console for 404 errors
- Increment CSS version in base.html: `?v=2026012709`

### Database locked?
```bash
# Stop app.py if running in background
pkill -f "python app.py"
```

---

## After All Tests Pass

```bash
# Stop the test server
pkill -f "python app.py"

# Commit and push
git add -A
git status  # Review what's changed
git commit -m "feat: UX Tier 1 improvements - accessibility, ADHD support, dyslexia support"
git push origin main
```

---

## Production Deployment

```bash
# SSH to server
ssh user@server

# Run migrations FIRST (before code deployment)
cd /opt/lernmanager
sudo SQLCIPHER_KEY='your_key' venv/bin/python migrate_add_time_estimates.py
sudo SQLCIPHER_KEY='your_key' venv/bin/python migrate_easy_reading_mode.py

# Deploy code
sudo /opt/lernmanager/deploy/update.sh

# Monitor for errors
sudo journalctl -u lernmanager -f
```

---

## Questions?

- **All tests pass?** → Commit and deploy!
- **Something broken?** → Check error messages, review TESTING_CHECKLIST.md
- **Want to skip a feature?** → Git can selectively stage files
- **Need to rollback?** → update.sh has automatic rollback on failure

**Total testing time:** ~20-25 minutes
**Deployment time:** ~5 minutes
**Risk level:** Low (all features are optional/additive)
