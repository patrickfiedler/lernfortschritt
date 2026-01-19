# Lernmanager - Ideas & Future Plans

## High Priority

- ~~502 error when I try to upload a file~~ (Fixed - was database permissions issue)
- ~~error logging functionality~~ (Complete - Phase 4)
- ~~Remove "Selbstbewertung pro Unterricht" from student page~~ (Complete - commit 4e64a18)
- ~~student attendance and evaluation page -> completely rewrite this page~~ (Complete - new rating system with -, ok, +, pre-defined comments, lesson comments)
- Code Review

## Features

- ~~Logging functionality: track number of users and page views~~ (Complete - Phase 5)
- ~~logging functionality #2: track student activities in action log~~ (Complete - Phase 5)
- ~~Student progress reports as PDF file per class: human readable format for quick overview~~ (Complete - Phase 6)
- ~~student progress reports as PDF file per student: information from class progress report + student's individual activity log~~ (Complete - Phase 6)
- ~~Add regular class dates for each class (schedule)~~ (Complete - implemented in student assessment improvements)

## Improvements

- ~~student view: show only the current (or the first) subtask of the active task~~ (Complete - see subtask_implementation_summary.md)
- ~~admin view: assign particular subtasks to classes and to students~~ (Complete - see subtask_implementation_summary.md)
- ~~Add #teilaufgabe anchor to student page. If the page reloads after a subtask has been completed, jump to this anchor directly.~~ (Complete - commit 4e64a18)
- (low priority, optional) student view: show visual learning map of open tasks and how they connect to each other; for the moment only for informational purposes
- admin view: when batch-importing students, add the url of the app to each line, along with username and password (either hardcode lernen.mrfiedler.de, or maybe read from configuration or HTML headers?)
- admin view: allow individual students to see all available tasks, but default to the current behaviour (students see only the active task)
- research a better way and place to implement student self-evaluation (was: student page, at bottom)

## Bugs

- ~~Fix task sorting: should be 1-2-3-10, not 1-10-2-3 (alphabetical vs numerical)~~ (Fixed)
- ~~Class assessment: make it obvious if data has been saved for a day (currently unclear - shows default 2/3 points for all dates)~~ (Fixed in student assessment improvements)

## Notes

-
