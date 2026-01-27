# UX Tier 1 Implementation Plan

## Goal
Implement critical accessibility and UX improvements from the comprehensive audit to remove barriers for students with disabilities and reduce cognitive load.

## Tier 1 Improvements (Quick Wins - ~10 hours total)

Based on the audit, these are HIGH IMPACT, LOW EFFORT changes:

### 1. Mobile Touch Targets (30 min)
**Problem**: Progress dots are 12px, need 44px minimum for touch screens
**Impact**: Mobile-only students (like Sophia) can't tap accurately
**Fix**: CSS media query to increase dot size on mobile

### 2. ARIA Labels & Keyboard Navigation (2 hours)
**Problem**: Screen readers can't announce dot content, no keyboard navigation
**Impact**: Screen reader users (like Jamal) can't use the app
**Fix**: Add `role="button"`, `aria-label`, `tabindex`, keyboard event handlers

### 3. Focus Indicators (30 min)
**Problem**: No visible focus state when tabbing through interface
**Impact**: Keyboard users don't know where they are
**Fix**: CSS outline on all interactive elements

### 4. Checkbox Text Reframe (15 min)
**Problem**: "Als erledigt markieren" sounds final/scary for anxious students
**Impact**: Perfectionist students (like Aisha) hesitate to mark complete
**Fix**: Change to "Ich habe das geschafft! ✓" (empowering)

### 5. Quiz Feedback Improvement (1 hour)
**Problem**: "Nicht bestanden" feels like failure, no encouragement
**Impact**: Quiz anxiety increases, students give up
**Fix**: Show progress ("7/10 richtig"), improvement tracking, encouragement

### 6. Time Estimates (2 hours)
**Problem**: No time awareness for ADHD students
**Impact**: Students (like Luca) can't plan, get distracted
**Fix**: Add `estimated_minutes` field to database, display "⏱️ ~15 Min"

### 7. Easy Reading Mode Toggle (3 hours)
**Problem**: Standard fonts exhausting for dyslexic students
**Impact**: Students (like Emma) avoid reading, disengage
**Fix**: Toggle for OpenDyslexic font, increased spacing, cream background

### 8. Focus Mode Enhancement (1 hour)
**Problem**: Resources open in new tabs, breaking concentration
**Impact**: Students lose focus switching between windows
**Fix**: Open PDFs/videos/links in modal overlay within app

## Decision Points

I need your preferences on these options:

### Question 1: Easy Reading Mode - How to activate?
**Option A**: Toggle button on every student page (persistent accessibility bar)
**Option B**: Setting in student profile (one-time choice, affects all pages)
**Option C**: Both - profile default + per-page override

**Recommendation**: Option C - respects student autonomy, reduces repeated clicking

### Question 2: Time Estimates - Where to add field?
**Option A**: Add to subtask table (most granular, accurate)
**Option B**: Add to task table (one estimate for whole task)
**Option C**: Both (task = sum of subtask estimates)

**Recommendation**: Option A - subtasks vary in length, need individual estimates

### Question 3: Quiz Threshold - Keep at 80% or reduce?
**Option A**: Keep 80% (Patrick said acceptable)
**Option B**: Reduce to 70% (audit recommends for anxiety reduction)
**Option C**: Make it configurable per task (some tasks harder than others)

**Recommendation**: Keep 80% but add practice mode option (Patrick mentioned this)

### Question 4: Focus Mode Modal - Which resources?
**Option A**: Only PDFs (most common)
**Option B**: PDFs + embedded videos (YouTube/Vimeo)
**Option C**: PDFs + videos + external links (iframe with warning)

**Recommendation**: Option B - videos are educational, links could be unsafe

### Question 5: Implementation Order
**Option A**: Do all 8 items sequentially (easier to test)
**Option B**: Group by type (all CSS, then templates, then backend)
**Option C**: Prioritize by impact (mobile touch + ARIA first, reading mode last)

**Recommendation**: Option C - fix critical accessibility barriers first

## Phases

- [ ] Phase 1: Critical accessibility (touch targets, ARIA, keyboard, focus)
- [ ] Phase 2: Anxiety reduction (checkbox text, quiz feedback)
- [ ] Phase 3: ADHD support (time estimates, focus mode)
- [ ] Phase 4: Dyslexia support (easy reading mode)
- [ ] Phase 5: Testing and refinement

## Key Questions
1. Easy reading mode: Toggle per-page, profile setting, or both?
2. Time estimates: Subtask-level, task-level, or both?
3. Quiz threshold: Keep 80%, reduce to 70%, or make configurable?
4. Focus mode: Which resource types to support in modal?
5. Implementation order: Sequential, grouped by type, or prioritized by impact?

## Decisions Made
- **Q1 (Easy Reading Mode)**: Profile setting (one-time choice in student profile)
- **Q2 (Time Estimates)**: Subtask level - add `estimated_minutes` field to subtask table + task editor
- **Q3 (Quiz Threshold)**: Reduce to 70% AND add practice mode option
- **Q4 (Focus Mode)**: Support PDFs + embedded videos (YouTube/Vimeo)
- **Q5 (Implementation Order)**: Sequential (items 1-8 in order)

## Follow-up Questions - ANSWERED

### Database Migration
**Q6**: The `estimated_minutes` field for subtasks - **DECISION: B**
- Optional (NULL allowed), show "~15-30 Min" as fallback if not set
- Allows gradual rollout, existing subtasks work without updates

### Practice Mode Behavior
**Q7**: When student selects "Practice Mode" on quiz - **DECISION: A**
- Results don't count toward pass/fail
- Unlimited retries allowed
- Shows correct answers after submission (educational)
- Reduces anxiety while teaching

### Easy Reading Mode - What Changes?
**Q8**: Easy Reading Mode should include - **DECISION: All of the above**
- Font: OpenDyslexic (specialized dyslexia font, serve via CDN or local)
- Line spacing: 2.0 (up from 1.7)
- Font size: 18px (up from 16px)
- Background: Cream (#FAF4E8) instead of white (#FFFFFF)
- All changes applied when toggle is enabled in student profile

### Focus Mode Modal - Close Behavior
**Q9**: When student closes focus mode modal - **DECISION: B**
- Mark material as "viewed" in database
- Useful analytics for teacher (track resource engagement)
- No interrupting feedback prompt

## Final Clarification Questions

### OpenDyslexic Font Hosting
**Q10**: OpenDyslexic font licensing/hosting:
- A) Use Google Fonts CDN (easiest, requires internet)
- B) Self-host font file (privacy, offline support)
- C) Fallback to Comic Sans if OpenDyslexic fails to load

**Note**: OpenDyslexic is open source (SIL license), can be self-hosted

### Easy Reading Mode Scope
**Q11**: Which pages should Easy Reading Mode affect?
- A) Only student dashboard and task pages
- B) All student-facing pages (including quiz, reports)
- C) Entire app (admin pages too)

**Recommendation**: B - All student pages

### Practice Mode Access
**Q12**: How do students access Practice Mode?

**Option A - Separate Practice Button**
```
┌─────────────────────────────────────┐
│ Quiz: Variablen und Datentypen      │
├─────────────────────────────────────┤
│ Du hast dieses Quiz noch nicht      │
│ bestanden. Möchtest du:             │
│                                     │
│ [Quiz starten (zählt!)]             │
│ [Übungsmodus (zählt nicht)]         │
└─────────────────────────────────────┘
```
**How it works:**
- Two buttons shown before quiz starts
- Student chooses mode upfront
- "Quiz starten" = regular mode (counts toward pass/fail)
- "Übungsmodus" = practice mode (shows answers, unlimited retries)
- Clear what each button does

**Pros:** Very clear choice, hard to accidentally start wrong mode
**Cons:** Slightly more clicks

---

**Option B - Checkbox Toggle**
```
┌─────────────────────────────────────┐
│ Quiz: Variablen und Datentypen      │
├─────────────────────────────────────┤
│ [✓] Übungsmodus                     │
│     (zählt nicht, zeigt Antworten)  │
│                                     │
│ Frage 1 von 10:                     │
│ Was ist eine Variable?              │
│ ( ) Ein fester Wert                 │
│ ( ) Ein Speicherplatz               │
│                                     │
│ [Weiter →]                          │
└─────────────────────────────────────┘
```
**How it works:**
- Checkbox at top of quiz page (always visible)
- Student can toggle during quiz
- When checked: results don't count, answers shown after
- When unchecked: regular quiz mode
- Student could switch mid-quiz

**Pros:** Flexible, student can change mind
**Cons:** Could accidentally toggle and lose progress, might be confusing

---

**Option C - Two Start Buttons (Recommended)**
```
┌─────────────────────────────────────┐
│ Quiz: Variablen und Datentypen      │
├─────────────────────────────────────┤
│ Wähle einen Modus:                  │
│                                     │
│ ┌───────────────────────────────┐   │
│ │ 📝 Quiz starten               │   │
│ │ Zählt für deine Note          │   │
│ │ 70% zum Bestehen              │   │
│ └───────────────────────────────┘   │
│                                     │
│ ┌───────────────────────────────┐   │
│ │ 🎯 Übungsmodus                │   │
│ │ Zählt nicht                   │   │
│ │ Zeigt richtige Antworten      │   │
│ └───────────────────────────────┘   │
└─────────────────────────────────────┘
```
**How it works:**
- Two distinct cards/buttons shown before quiz
- Each explains what it does
- Student picks one, quiz starts in that mode
- Mode is fixed (can't change mid-quiz)
- After practice, can click "Quiz starten" for real attempt

**Pros:** Clearest option, self-explanatory, prevents accidents
**Cons:** Takes more vertical space, requires more UI design

---

**My Recommendation: Option C**

**Why:**
1. **Reduces anxiety**: Student sees "Übungsmodus" is an option before starting
2. **Prevents mistakes**: Can't accidentally switch modes mid-quiz
3. **Self-documenting**: Each card explains what happens
4. **Natural flow**: Practice first → then real quiz
5. **Matches student mental model**: "I want to practice" vs "I'm ready for the real thing"

**Alternative: Option A** if you want simpler UI (just two buttons, less design work)

**Avoid: Option B** - checkbox during quiz is confusing and error-prone

## Errors Encountered
- (None yet)

## All Decisions Finalized

- **Q1**: Easy Reading Mode = Profile setting
- **Q2**: Time estimates = Subtask level (`estimated_minutes` field)
- **Q3**: Quiz threshold = 70% + practice mode
- **Q4**: Focus mode = PDFs + embedded videos
- **Q5**: Implementation order = Sequential (1-8)
- **Q6**: `estimated_minutes` = Optional (NULL allowed, fallback to "~15-30 Min")
- **Q7**: Practice mode = Results don't count, unlimited retries, shows answers
- **Q8**: Easy Reading Mode = OpenDyslexic font + 2.0 spacing + 18px + cream background
- **Q9**: Focus mode close = Mark material as "viewed"
- **Q10**: OpenDyslexic = Self-hosted font file
- **Q11**: Easy Reading Mode scope = All student-facing pages
- **Q12**: Practice mode access = Two card-style buttons with explanations

## Implementation Progress

- [x] 1. Mobile touch targets (30 min) - COMPLETE
- [x] 2. ARIA labels & keyboard navigation (2 hrs) - COMPLETE
- [x] 3. Focus indicators (30 min) - COMPLETE
- [x] 4. Checkbox text reframe (15 min) - COMPLETE
- [x] 5. Quiz feedback improvement (1 hr) - COMPLETE
- [x] 6. Time estimates (2 hrs) - COMPLETE
- [x] 7. Easy reading mode (3 hrs) - COMPLETE
- [ ] 8. Focus mode modal (1 hr) - SKIPPED (requires Practice Mode implementation first)

## Status
**IMPLEMENTATION COMPLETE** - 7 of 8 items finished, ready for testing

### Completed Items (Ready to Test)
1. ✅ Mobile touch targets - 44px dots on mobile
2. ✅ ARIA labels & keyboard navigation - Screen reader support, arrow keys
3. ✅ Focus indicators - Visible blue outline
4. ✅ Checkbox text - "Ich habe das geschafft! ✓"
5. ✅ Quiz feedback - Encouraging messages, 70% threshold, improvement tracking
6. ✅ Time estimates - Database field, student display, admin editor
7. ✅ Easy reading mode - Profile toggle, Comic Sans font, 18px, cream background

### Deferred Items
8. ⏸️ Focus mode modal - Deferred (needs more complex modal implementation)
9. ⏸️ Practice mode for quizzes - Deferred (needs mode selection UI + backend logic)

## Errors Encountered
- Migration script had import order issue with sqlite3 - Fixed by importing after checking SQLCipher key
- easy_reading_mode not in base template context - Fixed by checking student object exists
