# Task Plan: Fix Quiz Navigation Issues

## Goal
Make quiz accessible via clicking dot AND next button on last subtask. Note: Practice mode was deferred to Tier 2, not implementing now.

## Phases
- [x] Phase 1: Add onclick to quiz dot (WORKS)
- [x] Phase 2: Update goToNextSubtask to navigate to quiz
- [x] Phase 3: Investigate why next button is inactive on last subtask
- [x] Phase 4: Fix next button navigation logic
- [x] Phase 5: Complete - ready for testing

## Key Questions
1. Why is the next button inactive on the last subtask? **ANSWER: has_next only checked if there's another subtask**
2. Is the goToNextSubtask function being called correctly? **ANSWER: Function works, but button was disabled**
3. What determines if the next button is disabled? **ANSWER: {% if not has_next %} in template**

## Decisions Made
- Practice mode is NOT part of Test 4 - it was deferred to Tier 2 (see UX_TIER1_SUMMARY.md line 143)
- Quiz dot click already works
- Need to focus on next button issue
- Fixed: Updated has_next to check for quiz: `current_index < (subtasks|length - 1) or (current_index == (subtasks|length - 1) and task.quiz_json)`

## Changes Made
**File: templates/student/klasse.html:72**
- OLD: `{% set has_next = current_index < (subtasks|length - 1) %}`
- NEW: `{% set has_next = current_index < (subtasks|length - 1) or (current_index == (subtasks|length - 1) and task.quiz_json) %}`
- Logic: Button is enabled if there's a next subtask OR if on last subtask and quiz exists

## Errors Encountered
None.

## Status
**COMPLETE** - Next button now enabled on last subtask when quiz exists, and goToNextSubtask() will navigate to quiz
