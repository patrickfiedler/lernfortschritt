# UX Tier 1: Testing Plan

## Overview
7 of 8 planned improvements have been implemented. This document outlines how to test each feature.

## Pre-Testing Setup

### 1. Run Migrations (LOCAL)
```bash
python migrate_add_time_estimates.py
python migrate_easy_reading_mode.py
```

### 2. Run Migrations (PRODUCTION)
```bash
ssh user@server
cd /opt/lernmanager
sudo SQLCIPHER_KEY='your_key' /opt/lernmanager/venv/bin/python migrate_add_time_estimates.py
sudo SQLCIPHER_KEY='your_key' /opt/lernmanager/venv/bin/python migrate_easy_reading_mode.py
```

### 3. Deploy to Production
```bash
# Commit and push
git add -A
git commit -m "feat: UX Tier 1 improvements (accessibility, ADHD support, dyslexia support)"
git push origin main

# Deploy
ssh user@server 'sudo /opt/lernmanager/deploy/update.sh'
```

---

## Testing Checklist

### ✅ Item 1: Mobile Touch Targets

**What was changed:** Progress dots increased from 12px to 44px on mobile (WCAG 2.1 AA compliant)

**How to test:**
1. Open student task page on mobile device or narrow browser window (<768px)
2. Look at progress dots - they should be visibly larger
3. Try tapping dots - they should be easy to tap accurately
4. Gap between dots should be 16px (comfortable spacing)

**Success criteria:**
- Dots are 44x44px on mobile
- No accidental taps on adjacent dots
- Quiz dot ("?") also scales properly

---

### ✅ Item 2: ARIA Labels & Keyboard Navigation

**What was changed:** Added screen reader labels and keyboard controls for progress dots

**How to test (Screen Reader):**
1. Open student task page
2. Enable screen reader (NVDA on Windows, VoiceOver on Mac)
3. Tab to progress dots
4. Each dot should announce: "Aufgabe X: [description] - [Erledigt/nicht erledigt]"
5. Current dot should announce "aria-current=true"

**How to test (Keyboard):**
1. Open student task page
2. Tab to first progress dot (should show blue outline)
3. Press → (right arrow) - focus moves to next dot
4. Press ← (left arrow) - focus moves to previous dot
5. Press Enter or Space on a dot - navigates to that subtask

**Success criteria:**
- All dots are keyboard accessible (tabindex="0")
- Arrow keys navigate between dots
- Enter/Space activates dot navigation
- Screen reader announces dot labels correctly

---

### ✅ Item 3: Focus Indicators

**What was changed:** Added visible 2px blue outline when tabbing through interface

**How to test:**
1. Open any student page
2. Press Tab repeatedly
3. Every interactive element (buttons, links, inputs, dots) should show blue outline
4. Outline should be 2px solid blue with 2px offset

**Success criteria:**
- Focus indicator visible on all interactive elements
- Indicator only shows for keyboard users (not mouse clicks)
- Color contrast passes WCAG AA (blue on white background)

---

### ✅ Item 4: Checkbox Text Reframe

**What was changed:** Changed "Als erledigt markieren" → "Ich habe das geschafft! ✓"

**How to test:**
1. Open student task page
2. Look at checkbox label below task description
3. Text should read "Ich habe das geschafft! ✓" (empowering, not clinical)

**Success criteria:**
- New text appears on all subtask checkboxes
- Checkbox still functions correctly when clicked

---

### ✅ Item 5: Quiz Feedback Improvement

**What was changed:**
- Threshold reduced from 80% to 70%
- Encouraging feedback instead of "Nicht bestanden"
- Shows improvement from previous attempts

**How to test:**
1. Take a quiz and get 7/10 correct (70%)
   - Should pass with "🎉 Bestanden!"
2. Take a quiz and get 6/10 correct (60%)
   - Should show "💪 Fast geschafft!" instead of "❌ Leider nicht bestanden"
   - Should show encouragement: "Du brauchst mindestens 70%..."
3. Retake the same quiz and get 7/10
   - Should show improvement message: "⭐ Du wirst besser! Beim letzten Mal: 6/10 (60%). Jetzt: 7/10 (70%). Weiter so! 💪"

**Success criteria:**
- 70% passes (not 80%)
- Failed attempts show encouraging language
- Improvement tracking works across multiple attempts
- Previous attempt comparison is accurate

---

### ✅ Item 6: Time Estimates

**What was changed:**
- Added `estimated_minutes` field to subtask table
- Student view shows "⏱️ ~X Min" badge
- Admin editor has time input field

**How to test (Student View):**
1. Open student task page
2. Look at task badges (below "Aufgabe X von Y")
3. Should see green badge: "⏱️ ~15 Min" (or specific estimate if set)
4. If subtask has no estimate, shows "⏱️ ~15-30 Min"

**How to test (Admin Editor):**
1. Log in as admin
2. Go to any task
3. Edit subtasks
4. Each subtask should have a number input field (width 80px, placeholder "Min")
5. Enter a time estimate (e.g., 20)
6. Save subtasks
7. Check student view - should show "⏱️ ~20 Min"

**Success criteria:**
- Time estimates display correctly for students
- Admin can add/edit time estimates
- NULL values show fallback "~15-30 Min"
- Estimates save correctly to database

---

### ✅ Item 7: Easy Reading Mode

**What was changed:**
- Added `easy_reading_mode` field to student table
- Settings page for students to toggle mode
- CSS changes when enabled: Comic Sans, 18px, line-height 2.0, cream background

**How to test:**
1. Log in as student
2. Click "⚙️ Einstellungen" in navigation
3. Check "Lesemodus aktivieren" checkbox
4. Click "Speichern"
5. Return to dashboard - entire page should have:
   - Comic Sans font (or system equivalent)
   - Larger text (18px base)
   - More line spacing (2.0)
   - Cream background (#FAF4E8) instead of white

6. Navigate to task page - mode should persist
7. Go back to settings and uncheck - mode should disable

**Success criteria:**
- Toggle saves correctly to database
- CSS changes apply to entire student interface
- Mode persists across page reloads
- Cream background reduces glare
- Text is more readable for dyslexic users

---

## Deferred Items (Not Implemented)

### ⏸️ Item 8: Focus Mode Modal
**Why deferred:** Requires complex modal implementation with PDF/video embedding and view tracking

**Future implementation needs:**
- Modal overlay component
- PDF viewer (PDF.js)
- YouTube/Vimeo embed support
- Material view tracking in database
- Close button with tracking

### ⏸️ Item 9: Practice Mode for Quizzes
**Why deferred:** Requires mode selection UI and separate grading logic

**Future implementation needs:**
- Mode selection cards on quiz start page
- Practice mode flag in quiz submission
- Separate grading logic (don't save to student_task)
- Show correct answers after practice submission
- Allow unlimited retries

---

## Automated Testing (Optional)

### Lighthouse Accessibility Audit
```bash
# Install Lighthouse
npm install -g lighthouse

# Run audit on student page
lighthouse http://localhost:5000/schueler --only-categories=accessibility --view
```

**Target scores:**
- Accessibility: 95+ (100 is ideal)
- Focus indicators: Pass
- ARIA labels: Pass
- Touch targets: Pass

### Screen Reader Testing
- **Windows**: NVDA (free)
- **Mac**: VoiceOver (built-in)
- **Linux**: Orca

Test navigation with Tab key and arrow keys, ensure all content is announced.

---

## Regression Testing

Check that existing features still work:

1. ✅ Task completion (checkbox marking)
2. ✅ Quiz taking and grading
3. ✅ Progress dots navigation
4. ✅ Material links and uploads
5. ✅ Student dashboard loading
6. ✅ Admin task editing

---

## Deployment Checklist

Before deploying to production:

- [ ] All migrations run successfully on local database
- [ ] Local testing passes for all 7 items
- [ ] No console errors in browser
- [ ] Mobile responsive design still works
- [ ] Admin interface unaffected by changes
- [ ] Commit message is clear and descriptive

After deploying to production:

- [ ] Run migrations on production database (with SQLCIPHER_KEY)
- [ ] Test with real student account
- [ ] Test on actual mobile device (not just browser responsive mode)
- [ ] Monitor error logs for first 24 hours

---

## Rollback Plan

If critical issues occur in production:

```bash
# SSH to server
ssh user@server

# Check service status
sudo systemctl status lernmanager

# View recent errors
sudo journalctl -u lernmanager -n 100

# If needed, rollback to previous commit
cd /opt/lernmanager
sudo -u lernmanager git log --oneline -5  # Find previous commit hash
sudo -u lernmanager git reset --hard <previous-commit-hash>
sudo systemctl restart lernmanager
```

**Note:** update.sh has automatic rollback on service failure, so manual rollback should rarely be needed.

---

## Success Metrics

After 1-2 weeks in production, check:

1. **Accessibility:**
   - Screen reader users can complete tasks independently
   - Keyboard-only users can navigate fully
   - Mobile touch errors reduced

2. **Student Experience:**
   - Quiz completion rate increases (70% threshold helps)
   - Students report understanding "what to do" better (task name visible)
   - Easy reading mode adoption rate (how many students enable it)

3. **Time Awareness:**
   - Teachers report better time management in lessons
   - Students complete tasks within estimated time more often

4. **Technical:**
   - No increase in error rates
   - Page load times unaffected
   - Database performance stable

---

## Support Resources

If users need help:

- **Students:** Settings page has clear description of Easy Reading Mode
- **Teachers:** Time estimates help plan lesson flow
- **Accessibility:** ARIA labels and keyboard navigation should work with all modern screen readers

---

## Next Steps (Future UX Improvements)

After Tier 1 is validated:

**Tier 2 (High Priority):**
- Draft saving for subtask responses
- Color blindness support (patterns + color)
- Additional ARIA labels for form inputs

**Tier 3 (Major Restructure):**
- Topic → Task → Subtask redesign
- Restructure subtasks to 5-20 minute chunks
- Achievement/badge system
- Streak counter
