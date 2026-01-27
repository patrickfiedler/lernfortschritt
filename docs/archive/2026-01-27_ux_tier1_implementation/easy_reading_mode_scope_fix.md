# Easy Reading Mode Scope Issue

## Problem
Easy reading mode (Comic Sans, larger text, cream background) applies to admin views when viewing student pages. This is unintended - it should only apply to student-facing pages.

## Root Cause
In `base.html` line 15, we check:
```html
<body{% if student and student.easy_reading_mode %} class="easy-reading-mode"{% endif %}>
```

This checks if a `student` object exists with `easy_reading_mode` enabled. But when admin views student pages, we're passing the student object to show their info, so the mode gets applied.

## Solution
Need to also check the user type. Only apply easy reading mode when:
1. A student object exists
2. The student has easy_reading_mode enabled
3. **AND the current user is a student (not an admin viewing student pages)**

## Fix Applied
**File: templates/base.html line 15**

OLD:
```html
<body{% if student and student.easy_reading_mode %} class="easy-reading-mode"{% endif %}>
```

NEW:
```html
<body{% if student and student.easy_reading_mode and session.student_id %} class="easy-reading-mode"{% endif %}>
```

Now checks three conditions:
1. `student` object exists (prevents errors)
2. `student.easy_reading_mode` is enabled (setting is on)
3. `session.student_id` exists (current user IS a student, not admin)

This ensures easy reading mode only applies when a student with the setting enabled is logged in, not when an admin views student pages.
