# Implementation Plan: Student View Fixes and Navigation Redesign

## Goal
Fix Tests 9-10 failures (cache-busting, navigation logic) and implement side-button navigation UX redesign for student subtask view.

## Phases
- [x] Phase 1: Fix cache-busting in student view (Test 9) - 2 locations in klasse.html
- [x] Phase 2: Fix visible subtask counts in dashboard route (Test 9 partial)
- [x] Phase 3: Implement prev/next navigation logic with gap handling (Test 10)
- [x] Phase 4: Redesign navigation buttons to sides with responsive layout
- [x] Phase 5: Fix mobile button width (too wide, don't fit side by side)
- [x] Phase 6: Add visible border to current task progress dot
- [x] Phase 7: Add color distinction for compulsory vs optional tasks (DEFERRED - requires schema changes)
- [x] Phase 8: Refinements from user feedback
  - [x] 8a: Fix dot centering in border (less intrusive styling)
  - [x] 8b: Make dots clickable for direct navigation
  - [x] 8c: Show .current class on ALL viewed subtasks (not just incomplete)
  - [x] 8d: Fix .current class missing after marking task complete
  - [x] 8e: Make completed AND current dots green (completed+current = green with border)
  - [x] 8f: Fix color scheme (incomplete=gray, completed=green, current incomplete=blue, current completed=green)
  - [x] 8g: Fix template .current class logic (use separate if statements)
  - [x] 8h: Fix cache invalidation for completion status
  - [x] 8i: Fix mobile button layout (separate wrapper for mobile buttons)
- [x] Phase 9: Manual testing and verification - USER CONFIRMED WORKING ✓
- [x] Phase 10: Update documentation

## Key Decisions
- **Combined Phase 5+6 from plan**: Implement navigation logic and button redesign together since they touch the same code
- **Order**: Cache-busting first (quick win), then counts, then navigation redesign (biggest change)
- **Testing approach**: Manual testing after each phase to verify fixes

## Files Modified

### 1. templates/student/klasse.html
- Lines 53-102: Replaced current-task section with task-navigation-wrapper (flexbox layout)
- Line 128: Removed old "next incomplete" button
- Lines 246-256: Removed next-button display logic from toggleSubtask
- Lines 293-318: Replaced goToNextIncomplete() with goToNextSubtask() and goToPrevSubtask()
- Added subtaskIds and completedIds arrays for navigation

### 2. app.py
- Lines 1221-1237: Fixed dashboard route to count only visible subtasks using get_visible_subtasks_for_student()

### 3. static/css/style.css
- Lines 1457-1558: Added task-navigation-wrapper styles with flexbox layout
- Desktop: Side buttons (prev left, next right) with hover shift effects
- Mobile: Stacked layout with 50% width buttons below content, reduced padding to fit
- Lines 1095-1100: Enhanced current dot border (3px white + 2px blue outline)

### 4. compulsory_optional_tasks_plan.md
- Created plan for future feature (deferred - requires schema changes)

## Testing Instructions

### Test 9 Retest: Cache-busting and Progress Dots
1. Log in as student (activehorse/nijata64)
2. Navigate to class with 4 visible subtasks
3. Complete subtask 1, click any navigation → Progress dot 1 should turn green immediately
4. Complete subtask 2 → Both dots 1 and 2 should be green
5. Dashboard should show "2/4" (not "2/8")

### Test 10 Retest: Navigation with Gaps
1. Use class with subtasks 1,2,3,6,7,8 (gap between 3 and 6)
2. Start at subtask 1, click Next → Should go to subtask 2
3. At subtask 2, click Next → Should go to subtask 3
4. At subtask 3, click Next → Should go to subtask 6 (skips gap)
5. Previous button should work in reverse order
6. Buttons should be on sides of content (desktop) or below (mobile)

### Navigation UX Check
1. Desktop view: Prev button on left, content center, Next button on right
2. Buttons should show arrow + label ("Zurück"/"Weiter")
3. Hover effects: slight shift left/right, blue background
4. Disabled buttons: gray, no hover effect
5. Mobile view (<768px): Content first, then two 50% width buttons below

## Issues Found During Testing
- **Mobile button width**: Buttons are 305px/319px wide but container is 620px, causing overflow
- **Progress dots**: Current task dot needs visible border for emphasis
- **Task colors**: Need distinction between compulsory (yellow when open) and optional (rainbow spectrum) tasks
  - **BLOCKED**: Requires database schema change to add `is_compulsory` field to subtasks table
  - **BLOCKED**: Requires task editor UI changes to mark subtasks as compulsory/optional
  - This is documented in todo.md and should be separate feature implementation

## Status
**✅ ALL PHASES COMPLETE** - Student view fixes and navigation redesign fully implemented and tested (Jan 27, 2026)

## Server Status
- Flask PID: 1289415
- URL: http://localhost:5000
- CSS version in HTML: `?v=2026012703` (incremented after fixes)
- Server responding correctly

## Final Fixes Applied
- **Mobile buttons**: Removed `scale(1.02)` transform on hover, added blue background instead
- **Dot color logic**:
  - Incomplete: Gray (#d1d5db)
  - Completed: Green (#10b981)
  - Current incomplete: Blue (#3b82f6) with blue ring
  - Current completed: Green (#10b981) with green ring
- **Dot clickability**: Added onclick handlers and tooltip with subtask name
- **Current class logic**: Shows on ANY viewed subtask AND persists after marking complete
- **JavaScript fix**: Keep 'current' class when marking complete (don't remove it)
- **CSS version**: Updated to v=2026012706

## CSS Changes Summary
1. **Current dot border**: White 3px border + dark blue 2px outline (double-ring effect)
2. **Mobile button sizing**: Reduced to `calc(50% - 1rem)` width, 1px border instead of 2px
3. **CSS cache-busting**: Added `?v=2026012702` version parameter to force fresh load

## Errors Encountered
- **Error 1**: CSS changes not appearing in browser despite cache clearing
  - **Root Cause**: Flask serves static files with aggressive browser caching, CTRL+F5 insufficient
  - **Fix**: Added version parameter to CSS link `?v=2026012702` in base.html and login.html ✓

- **Error 2**: No dot has `.current` class - border styling not applied
  - **Root Cause**: Template shows completed subtask (all 4 done), no current/active subtask
  - The `.current` class is only added when viewing an incomplete subtask
  - Border styling works correctly, just not visible when all tasks complete

- **Error 3**: Mobile buttons too wide on hover (315px + 318px = 633px > 620px container)
  - **Root Cause**: Hover transform `scale(1.02)` increases width by 2%, causing overflow
  - 297.666px × 1.02 = 303.6px (already too wide)
  - **Fix**: Removed scale transform on mobile ✓

- **Error 4**: Buttons displaying vertically with prev above content, next below
  - **Root Cause 1**: Parent used `flex-direction: column` forcing vertical stack
  - **Root Cause 2**: With `display: block` + floats, buttons flow around content
  - HTML order: prev button → content → next button creates wrong layout
  - **Fix**: Created separate mobile button wrapper after content
  - Desktop: Original buttons on sides (flexbox)
  - Mobile: Hide side buttons, show `.nav-buttons-mobile` wrapper with flexbox (flex: 1 each) ✓

- **Error 5**: Template error - "Ein unerwarteter Fehler ist aufgetreten" when viewing student task
  - **Root Cause**: Line 45 used `sub.name` but subtasks have `beschreibung` attribute, not `name`
  - **Fix**: Changed `sub.name` to `sub.beschreibung` in tooltip title ✓

- **Error 6**: Current class missing when navigating to completed task (shows blue instead of green)
  - **Root Cause**: Template used `elif` so current and completed were mutually exclusive
  - Line 41: `{% if current %}current{% elif completed %}completed{% endif %}`
  - If subtask was current, it only got "current" class (missing "completed")
  - **Fix**: Changed to two separate if statements so both classes can be applied ✓

- **Error 7**: Completed subtask shows gray after navigation (but correct on second navigation)
  - **Root Cause**: Backend caches subtask progress for 30 seconds
  - Mark complete → saves to DB, but cache not invalidated
  - Navigate (within 30s) → loads from stale cache (shows incomplete)
  - Navigate again (after 30s) → cache expired, fresh data (shows complete)
  - **Fix**: Added `cache.delete(cache_key)` after toggling subtask in app.py line 1370 ✓
  - **Flask restarted**: PID 1304162, cache invalidation now active

## Completed (Additional)
- **Phase 5**: Reduced mobile button padding and font size to fit side by side
  - Changed width from `calc(50% - 0.5rem)` to `calc(50% - 0.75rem)`
  - Reduced padding from `1rem` to `0.75rem 0.5rem`
  - Reduced arrow size from 2rem to 1.5rem
  - Reduced label font size to 0.6875rem
  - Changed hover transform to `scale(1.02)` (no lateral shift on mobile)
- **Phase 6**: Enhanced current dot visibility
  - Changed border to 3px white + 2px blue outline
  - Increased shadow from 3px to 4px with higher opacity

## Completed
- **Phase 1**: Fixed cache-busting in klasse.html lines 291 and 318
- **Phase 2**: Fixed dashboard to count only visible subtasks (app.py lines 1221-1237)
- **Phase 3**: Implemented prev/next navigation with gap handling (JavaScript functions in klasse.html)
- **Phase 4**: Redesigned navigation with side buttons (flexbox layout, responsive CSS in style.css)
- **Phase 5**: Fixed mobile button width and layout issues
- **Phase 6**: Added visible border to current task progress dot
- **Phase 7**: Compulsory vs optional task colors (deferred - requires schema changes)
- **Phase 8**: Implemented all user feedback refinements (8a-8i)
- **Phase 9**: Manual testing and user verification completed
- **Phase 10**: Documentation updated (task_plan.md, frontend_patterns.md, todo.md, CLAUDE.md)

---

## Implementation Summary

This implementation successfully fixed Tests 9-10 failures and delivered a complete navigation redesign for the student subtask view:

### Features Delivered:
1. ✅ Cache-busting for real-time progress updates
2. ✅ Accurate visible subtask counts throughout the application
3. ✅ Sequential prev/next navigation that handles gaps in subtask numbering
4. ✅ Responsive side-button layout (desktop: left/right, mobile: below content)
5. ✅ Clickable progress dots for direct subtask navigation
6. ✅ Visual indication of current task with colored ring borders
7. ✅ Proper color scheme (gray=incomplete, green=complete, blue/green rings for current)
8. ✅ Backend cache invalidation for immediate state updates

### Technical Achievements:
- Solved 7 major errors through systematic debugging (see Errors Encountered section)
- Documented 3 reusable patterns in frontend_patterns.md (mobile buttons, cache-busting, state tracking)
- Updated static file cache-busting strategy in CLAUDE.md
- Maintained backward compatibility with existing student progress data

### Files Modified:
- `templates/student/klasse.html` - Navigation structure, JavaScript, dot interactions
- `static/css/style.css` - Responsive layout, dot colors, mobile buttons
- `app.py` - Cache invalidation, visible subtask counting
- `templates/base.html` & `login.html` - CSS version parameters

### Lessons Learned:
1. **Mobile layout complexity**: Separate HTML wrappers are cleaner than CSS reordering
2. **Template class logic**: Use separate `if` statements for combinable states, not `elif`
3. **Cache invalidation**: Always delete cache keys after state changes
4. **Browser caching**: Timestamp parameters are effective for forcing fresh data loads

**Final Status**: All implementation goals achieved. User confirmed "This works" on Jan 27, 2026.
