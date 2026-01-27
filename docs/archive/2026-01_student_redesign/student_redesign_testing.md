# Student Experience Redesign - Testing Checklist

**Status**: Ready for testing
**Phases Complete**: Phase 1-4 (Database, Admin, Student View, Terminology)
**Current Phase**: Phase 5 - Testing & Refinement

## Overview

This document provides a comprehensive testing checklist for the new student interface redesign. Follow each section systematically to ensure all features work correctly.

## Pre-Testing Setup

- [x] Flask dev server running (`python app.py`)
- [ ] Test student account ready (username: ____________, password: ____________)
- [ ] At least one class with assigned task containing:
  - [ ] Task with `why_learn_this` field filled in
  - [ ] At least 3-4 subtasks
  - [ ] Materials (links and/or files)
  - [ ] Optional: Quiz configured

## 1. Functional Testing

### 1.1 Student Dashboard (templates/student/dashboard.html)

**URL**: `http://localhost:5000/schueler/dashboard`

- [ ] Page title shows "Meine Themen" (not "Meine Aufgaben")
- [ ] Classes display correctly in grid layout
- [ ] Task cards show correct information (name, subject, level)
- [ ] Bonus tasks show "⭐ Bonusthema" badge (not "Bonusaufgabe")
- [ ] Progress bar displays correctly
- [ ] "Weiterarbeiten →" button works
- [ ] When no task assigned: shows "Kein Thema zugewiesen" (not "Keine Aufgabe")
- [ ] Breadcrumb navigation works

### 1.2 Student Class View - Basic Layout (templates/student/klasse.html)

**URL**: `http://localhost:5000/schueler/klasse/<klasse_id>`

#### Visual Structure
- [ ] Breadcrumb navigation displays: Dashboard › [Class Name]
- [ ] Content wrapped in white card with rounded corners and shadow
- [ ] Topic headline (h1) is prominent and bold
- [ ] Topic meta (subject · level) displays below headline
- [ ] Overall layout is clean and not overwhelming

### 1.3 Purpose Banner ("Why learn this?")

- [ ] Purpose banner displays when `why_learn_this` field is filled
- [ ] Banner has blue gradient background
- [ ] Light bulb icon (💡) displays on left
- [ ] Label "Wofür brauchst du das?" is visible
- [ ] Purpose text is readable and properly formatted
- [ ] Banner does NOT display when field is empty
- [ ] Banner is responsive on mobile (doesn't overflow)

### 1.4 Progress Tracking

#### Progress Text
- [ ] Shows "X von Y Aufgaben erledigt" (correct count)
- [ ] Updates dynamically when task completed (without reload)

#### Progress Dots
- [ ] Displays one dot per subtask
- [ ] Gray dots for uncompleted tasks
- [ ] Green dots for completed tasks
- [ ] Blue dot (larger, glowing) for current task
- [ ] Quiz dot shows "?" character at the end
- [ ] Quiz dot turns green when quiz passed
- [ ] Dots wrap properly on mobile screens
- [ ] Dots align horizontally with proper spacing

### 1.5 Current Task Display

- [ ] Task badge shows "Aufgabe X von Y" (correct numbering)
- [ ] Task content renders markdown correctly (headings, lists, links, code)
- [ ] Content is readable and properly formatted
- [ ] Checkbox labeled "Als erledigt markieren"
- [ ] Checkbox is NOT checked initially for uncompleted task
- [ ] Checkbox IS checked for already completed task
- [ ] Checkbox area is clickable (hover effect visible)

### 1.6 Task Completion Flow

**Test Scenario**: Complete a subtask

1. **Before clicking checkbox**:
   - [ ] Current task displays with unchecked checkbox
   - [ ] Success banner is hidden
   - [ ] "Next" button is hidden
   - [ ] Progress dot for current task is blue

2. **Click checkbox to mark complete**:
   - [ ] Checkbox becomes checked
   - [ ] Success banner appears with green background: "Gut gemacht! Aufgabe erledigt."
   - [ ] "Next" button appears: "Weiter zur nächsten Aufgabe →"
   - [ ] Current progress dot changes from blue to green
   - [ ] Progress text updates: "X von Y Aufgaben erledigt" (X increased by 1)
   - [ ] No page reload occurred

3. **Click "Next" button**:
   - [ ] Page reloads
   - [ ] Next uncompleted subtask displays
   - [ ] Progress preserved (completed task still marked done)
   - [ ] Success banner hidden again
   - [ ] "Next" button hidden again

4. **Uncheck a completed task**:
   - [ ] Navigate to a completed task
   - [ ] Uncheck the checkbox
   - [ ] Page reloads
   - [ ] Task shows as uncompleted
   - [ ] Progress updated correctly

### 1.7 Completed Tasks Section

- [ ] Collapsible section shows "✓ X Aufgabe(n) bereits erledigt"
- [ ] Section is collapsed by default
- [ ] Click to expand shows list of completed tasks
- [ ] Each completed task shows checkmark icon
- [ ] Task descriptions truncated to 100 characters
- [ ] Shows "..." if description is longer
- [ ] Section hidden when no tasks completed

### 1.8 Materials Section

- [ ] Collapsible section shows "📎 Materialien"
- [ ] Section is OPEN by default (not collapsed)
- [ ] Link materials show 🔗 icon
- [ ] File materials show 📄 icon
- [ ] Links open in new tab
- [ ] File downloads work correctly
- [ ] Description displays (or falls back to path)
- [ ] Section hidden when no materials exist

### 1.9 Quiz Section

**When all subtasks completed but quiz not passed**:
- [ ] Quiz card displays with "❓ Quiz" header
- [ ] Shows previous attempts (if any) with scores
- [ ] Shows pass/fail badge for each attempt
- [ ] "Quiz starten" button works
- [ ] Shows "mindestens 80% richtige Antworten" message
- [ ] Quiz dot in progress is gray/unfilled

**When quiz passed**:
- [ ] Quiz card replaced with success message: "✅ Quiz bestanden! Thema abgeschlossen."
- [ ] Quiz dot in progress is green/filled
- [ ] Task marked as `abgeschlossen`

**When subtasks not all completed**:
- [ ] Quiz section does NOT display

### 1.10 Topic Description Section

- [ ] Collapsible section labeled "Ausführliche Beschreibung"
- [ ] Section is collapsed by default
- [ ] Click to expand shows learning goal (🎯) if present
- [ ] Shows description (📋) if present
- [ ] Markdown renders correctly
- [ ] Shows "Keine zusätzlichen Informationen verfügbar" when empty

### 1.11 No Task Assigned

- [ ] When student has no task: shows "Kein Thema zugewiesen" (not "Keine Aufgabe")
- [ ] Shows "← Zurück zum Dashboard" button
- [ ] Button works correctly

### 1.12 Edge Cases

- [ ] Task with NO subtasks: shows "Keine Aufgaben definiert"
- [ ] Task with NO materials: materials section hidden
- [ ] Task with NO quiz: quiz dot not shown in progress
- [ ] Task with NO why_learn_this: purpose banner hidden
- [ ] Task with NO lernziel or beschreibung: topic description shows fallback message

## 2. Cross-Browser Testing

Test in the following browsers:

### Desktop
- [ ] **Chrome** (latest): All features work
- [ ] **Firefox** (latest): All features work
- [ ] **Safari** (latest): All features work
- [ ] **Edge** (latest): All features work

### Mobile Browsers
- [ ] **Chrome Mobile** (Android): All features work
- [ ] **Safari Mobile** (iOS): All features work

### Specific Browser Checks
- [ ] CSS gradients render correctly
- [ ] Box shadows display properly
- [ ] Border radius (rounded corners) works
- [ ] Animations (slideIn, scale) work smoothly
- [ ] Flexbox layout works correctly
- [ ] Grid layout works correctly

## 3. Responsive Design Testing

### Mobile (< 768px)

- [ ] Content card padding reduces to 1.5rem 1rem
- [ ] Purpose banner text wraps properly
- [ ] Progress header stacks vertically (text above dots)
- [ ] Progress dots wrap to multiple rows if needed
- [ ] Task content is readable (no horizontal scroll)
- [ ] Buttons are thumb-friendly (adequate tap target size)
- [ ] Collapsible sections work on touch
- [ ] Breadcrumb doesn't overflow

### Tablet (768px - 1024px)

- [ ] Layout uses available space well
- [ ] Cards don't become too wide
- [ ] Text remains readable
- [ ] Touch targets adequate

### Desktop (> 1024px)

- [ ] Content card max-width constraint works (doesn't stretch too wide)
- [ ] Hover effects work on interactive elements
- [ ] Layout is balanced and aesthetically pleasing

## 4. Accessibility Testing

- [ ] Tab navigation works through all interactive elements
- [ ] Checkbox can be toggled with keyboard (Space/Enter)
- [ ] Links are keyboard accessible
- [ ] Collapsible sections (details/summary) work with keyboard
- [ ] Focus indicators visible on interactive elements
- [ ] Color contrast meets WCAG AA standards:
  - [ ] Purpose banner (white text on blue)
  - [ ] Success banner (white text on green)
  - [ ] Action button (white text on blue)
- [ ] Text remains readable when zoomed to 200%

## 5. Performance Testing

- [ ] Page loads within 2 seconds (first visit)
- [ ] Page loads within 1 second (subsequent visits)
- [ ] No layout shift (CLS) during load
- [ ] Checkbox toggle feels instant (< 300ms response)
- [ ] Progress dot animation is smooth
- [ ] No JavaScript errors in console
- [ ] No CSS warnings in console

## 6. Visual Quality Assurance

### Colors & Styling
- [ ] Blue gradient (#3b82f6 to #2563eb) looks good
- [ ] Green success color (#10b981) is vibrant but not harsh
- [ ] Gray neutral colors are subtle
- [ ] Shadows are subtle (not too dark or too light)
- [ ] Rounded corners (0.75rem on card, 0.5rem on elements) look polished

### Typography
- [ ] Headings are bold and clear
- [ ] Body text is readable (adequate size and line-height)
- [ ] Badge text is legible
- [ ] Icon emojis display correctly (no missing glyphs)

### Spacing
- [ ] Elements have adequate breathing room
- [ ] Sections are visually separated
- [ ] Padding and margins feel balanced
- [ ] Content doesn't feel cramped or too sparse

## 7. Integration Testing

### Complete Student Journey

**Scenario**: Student completes an entire topic from start to finish

1. [ ] Login as student
2. [ ] Navigate to dashboard → see class with assigned task
3. [ ] Click "Weiterarbeiten →" → see task page
4. [ ] Read "Why do you need this?" purpose
5. [ ] Check current progress (0 of N completed)
6. [ ] Read current task
7. [ ] Mark task as complete → see success banner
8. [ ] Click "Next" → see next task
9. [ ] Repeat until all tasks done
10. [ ] Expand "completed tasks" → see all completed tasks
11. [ ] Open materials → view resources
12. [ ] Quiz appears → start quiz
13. [ ] Complete quiz with 80%+ → see success message
14. [ ] Return to dashboard → see task marked complete

## 8. Admin Workflow Testing

Ensure admin changes reflect in student view:

- [ ] Admin adds `why_learn_this` field → student sees purpose banner
- [ ] Admin removes `why_learn_this` field → purpose banner disappears
- [ ] Admin adds new subtask → student sees updated count
- [ ] Admin reorders subtasks → student sees new order
- [ ] Admin adds material → student sees new material
- [ ] Admin adds quiz → student sees quiz after tasks complete

## 9. Known Issues / Notes

Use this section to document any issues found during testing:

### Issues Found
```
1. [Date] [Browser] [Issue description]
   - Steps to reproduce:
   - Expected behavior:
   - Actual behavior:
   - Priority: High/Medium/Low

2.

```

### Browser-Specific Notes
```
- Chrome:
- Firefox:
- Safari:
- Mobile:
```

## 10. Sign-Off

### Testing Completion

- [ ] All functional tests passed
- [ ] All browsers tested
- [ ] Responsive design verified
- [ ] Accessibility checked
- [ ] Performance acceptable
- [ ] Visual quality approved
- [ ] No blocking issues

### Ready for Deployment

- [ ] All tests completed
- [ ] Issues documented and addressed/accepted
- [ ] Code reviewed
- [ ] Commit messages clear
- [ ] Ready to push to production

**Tested by**: _______________
**Date**: _______________
**Sign-off**: _______________

---

## Next Steps After Testing

1. **If issues found**: Document in "Known Issues" section, fix, re-test
2. **If all tests pass**: Proceed to Phase 6 (Documentation & Deployment)
3. **Deploy to production**: Push to GitHub, SSH to server, run update.sh
4. **Run migration on production**: Ensure `why_learn_this` column exists
5. **Fill in "why_learn_this" for existing tasks**: Admin task
6. **Monitor production**: Check for any issues in live environment
