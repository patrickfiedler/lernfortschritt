# Task Plan: Fix PDF Report Database Schema Mismatch

## Goal
Fix PDF report implementation to work with actual database schema by using existing model functions instead of incorrect SQL queries.

## Phases
- [ ] Phase 1: Investigate actual database schema
- [ ] Phase 2: Document existing model functions that compute progress
- [ ] Phase 3: Identify all incorrect SQL queries in report functions
- [ ] Phase 4: Refactor models.py report data functions
- [ ] Phase 5: Refactor utils.py PDF generation functions
- [ ] Phase 6: Test all three report types
- [ ] Phase 7: Commit fixes and update documentation

## Key Questions
1. What columns actually exist in each table?
2. How do existing functions compute progress data?
3. Which report functions need SQL fixes?
4. Which PDF functions need data structure fixes?
5. Are there any other assumptions about data that are incorrect?

## Decisions Made
- **Use existing model functions**: Don't write new SQL, use get_student_task() + get_student_subtask_progress()
- **Compute progress dynamically**: Count subtasks instead of expecting stored values
- **Fix data structure**: Align with actual database schema (klasse has only id/name)
- **Use 'abgeschlossen' field**: This is the actual completion flag, not 'is_completed'

## Errors Encountered
- **KeyError: 'stufe'**: klasse table only has id, name (not stufe, subject) - stufe/fach are on task table
- **KeyError: 'order_num'**: task table has 'number' not 'order_num'
- **KeyError: 'completed_subtasks'**: student_task table doesn't store these - must compute from subtask counts
- **OperationalError: no such column**: Multiple columns expected but don't exist

## Implementation Plan

### Phase 1: Fix `get_report_data_for_class()` ✅
- Remove klasse.stufe, klasse.subject references
- Use get_student_task() instead of raw SQL
- Use get_student_subtask_progress() to compute progress
- Use get_quiz_attempts() for quiz status

### Phase 2: Fix `get_report_data_for_student()`
- Remove klasse.stufe, klasse.subject references
- Use get_student_task() for each class
- Compute progress from subtasks
- Fix activity_log queries for complete report

### Phase 3: Test All Report Types
- Test class report
- Test student summary report
- Test student complete report
- Test student self-report

## Fixes Applied

### models.py:
1. get_report_data_for_class() - Use existing functions, compute progress from subtasks
2. get_report_data_for_student() - Fix SQL queries, use existing functions
3. Fixed quiz_attempt query - Join through student_task, use correct column names (punkte/max_punkte/bestanden)
4. Fixed unterricht query - Use unterricht_student table, datum field

### utils.py:
1. generate_student_report_pdf() - Handle activity_log as list, not dict
2. generate_student_self_report_pdf() - Handle tasks_completed as list, get count

## Test Results
✅ Class report: 2514 bytes
✅ Student summary report: 2586 bytes
✅ Student complete report: 3130 bytes
✅ Student self-report: 2467 bytes

## Status
**Phase 1 COMPLETE** - Investigation done, notes documented
**Phase 2 COMPLETE** - All report functions fixed
**Phase 3 COMPLETE** - All tests passing
**Ready for** - Weekly report generation script + crontab
