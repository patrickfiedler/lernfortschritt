# Task Plan: Fix Easy Reading Mode on Task View

## Goal
Make easy reading mode (Comic Sans font, cream background, larger text) apply to all student pages, not just dashboard.

## Phases
- [x] Phase 1: Identify the problem
- [x] Phase 2: Check how student data is passed to templates
- [x] Phase 3: Fix student_klasse route to pass student object
- [x] Phase 4: Check other student routes
- [x] Phase 5: Fix all routes that render templates

## Key Questions
1. How is the student object passed to klasse.html template? **ANSWER: It's NOT - that's the bug!**
2. Is the easy_reading_mode flag available in the task view context? **ANSWER: No, student object missing**

## Decisions Made
- student_dashboard calls `models.get_student(student_id)` and passes student to template
- student_klasse does NOT get or pass student object - FIXED
- student_quiz also needs student object - FIXED
- student_bericht generates PDF, doesn't need template fix
- student_settings already has student object

## Routes Fixed
1. `/schueler/klasse/<int:klasse_id>` - Added student = models.get_student(student_id) and student to render_template
2. `/schueler/aufgabe/<int:student_task_id>/quiz` - Added student = models.get_student(student_id) and student to both render_template calls (quiz.html and quiz_result.html)

## Errors Encountered
None.

## Status
**COMPLETE** - All student template routes now pass student object with easy_reading_mode flag
