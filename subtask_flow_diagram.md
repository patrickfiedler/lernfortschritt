# Subtask Assignment Flow Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE SCHEMA                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  student_task                                                    │
│  ┌────────────────────────────────────────────────┐             │
│  │ id                                             │             │
│  │ student_id  ───────────────┐                   │             │
│  │ klasse_id                  │                   │             │
│  │ task_id                    │                   │             │
│  │ current_subtask_id  ───────┼─────┐             │             │
│  │ abgeschlossen              │     │             │             │
│  └────────────────────────────┘     │             │             │
│                                     │             │             │
│  subtask                            │             │             │
│  ┌────────────────────────────────┐ │             │             │
│  │ id                ◄─────────────┘             │             │
│  │ task_id                                       │             │
│  │ beschreibung                                  │             │
│  │ reihenfolge                                   │             │
│  └────────────────────────────────┘              │             │
│                                                   │             │
│  student_subtask                                 │             │
│  ┌──────────────────────────────────────┐       │             │
│  │ id                                    │       │             │
│  │ student_task_id  ─────────────────────┘       │             │
│  │ subtask_id                                    │             │
│  │ erledigt (0/1)                                │             │
│  └──────────────────────────────────────┘        │             │
└─────────────────────────────────────────────────────────────────┘
```

## Admin Assignment Flow

### Class-Level Assignment
```
Admin → Class Detail Page
   │
   ├─ Select Task
   │     │
   │     └─ AJAX → GET /admin/aufgabe/{task_id}/teilaufgaben
   │           │
   │           └─ Returns subtask list (JSON)
   │
   ├─ [Optional] Select Subtask
   │
   └─ Submit Form → POST /admin/klasse/{klasse_id}/aufgabe-zuweisen
         │              { task_id, subtask_id }
         │
         └─ assign_task_to_klasse(klasse_id, task_id, subtask_id)
               │
               └─ For each student in class:
                    INSERT student_task (current_subtask_id = subtask_id)
```

### Individual Student Assignment
```
Admin → Student Detail Page
   │
   ├─ Assign New Task
   │    │
   │    ├─ Select Task
   │    │     │
   │    │     └─ AJAX → Load subtasks
   │    │
   │    ├─ [Optional] Select Subtask
   │    │
   │    └─ Submit → POST /admin/schueler/{student_id}/aufgabe-zuweisen
   │           │
   │           └─ assign_task_to_student(student_id, klasse_id, task_id, subtask_id)
   │
   └─ Update Current Subtask (for existing task)
        │
        ├─ Select Subtask from dropdown
        │
        └─ Submit → POST /admin/schueler/{student_id}/teilaufgabe-setzen
              │
              └─ set_current_subtask(student_task_id, subtask_id)
                    │
                    └─ UPDATE student_task SET current_subtask_id = ?
```

## Student View Flow

### Loading Task Page
```
Student → Class Page (GET /schueler/klasse/{klasse_id})
    │
    ├─ get_student_task(student_id, klasse_id)
    │     │
    │     └─ Returns task with current_subtask_id
    │
    ├─ IF current_subtask_id IS NOT NULL:
    │    │
    │    ├─ get_current_subtask(student_task_id)
    │    │     │
    │    │     └─ Returns single subtask
    │    │
    │    ├─ Filter: subtasks = [current_subtask]
    │    │
    │    └─ Get completed_subtasks for collapsible view
    │
    └─ ELSE (current_subtask_id IS NULL):
         │
         └─ Show all subtasks (backward compatible)
```

### Completing Subtask
```
Student → Check subtask checkbox
    │
    └─ AJAX → POST /schueler/aufgabe/{student_task_id}/teilaufgabe/{subtask_id}
          │        { erledigt: true }
          │
          └─ toggle_student_subtask(student_task_id, subtask_id, true)
                │
                ├─ INSERT/UPDATE student_subtask (erledigt = 1)
                │
                └─ advance_to_next_subtask(student_task_id, subtask_id)
                      │
                      ├─ Get all subtasks ordered by reihenfolge
                      │
                      ├─ Find next incomplete subtask after current
                      │
                      └─ UPDATE student_task SET current_subtask_id = next_subtask_id
```

## Auto-Advance Logic

```
Complete Subtask #1
    │
    └─ advance_to_next_subtask()
          │
          ├─ Get subtasks: [#1, #2, #3, #4, #5]
          │
          ├─ Current completed: #1
          │
          ├─ Search from #2 onwards:
          │    │
          │    ├─ #2: Not complete → SET current = #2
          │    │
          │    └─ (If #2 complete, check #3, etc.)
          │
          └─ Result: Student now sees Subtask #2
```

## Three View Modes

### Mode 1: Current Subtask Filter (NEW)
```
current_subtask_id = 3
┌────────────────────────────────────────┐
│ Du arbeitest gerade an dieser          │
│ Teilaufgabe:                           │
│                                         │
│ ┌────────────────────────────────┐    │
│ │ [Aktuell] Subtask #3          │    │
│ │ Beschreibung...               │    │
│ │                         [ ☐ ] │    │
│ └────────────────────────────────┘    │
│                                         │
│ ▶ ✓ 2 Teilaufgaben bereits erledigt   │
│   (click to expand)                    │
│                                         │
│ Progress: ████░░░░░░ 3/5               │
└────────────────────────────────────────┘
```

### Mode 2: All Subtasks Visible (LEGACY)
```
current_subtask_id = NULL
┌────────────────────────────────────────┐
│ ┌────────────────────────────────┐    │
│ │ [1] Subtask #1            [✓] │    │
│ └────────────────────────────────┘    │
│ ┌────────────────────────────────┐    │
│ │ [2] Subtask #2            [✓] │    │
│ └────────────────────────────────┘    │
│ ┌────────────────────────────────┐    │
│ │ [3] Subtask #3            [ ☐] │    │
│ └────────────────────────────────┘    │
│ ┌────────────────────────────────┐    │
│ │ [4] Subtask #4            [ ☐] │    │
│ └────────────────────────────────┘    │
│                                         │
│ Progress: ████░░░░░░ 2/4               │
└────────────────────────────────────────┘
```

### Mode 3: No Subtasks
```
task has no subtasks
┌────────────────────────────────────────┐
│ Keine Teilaufgaben definiert.          │
└────────────────────────────────────────┘
```

## Key Benefits

### For Students
- **Reduced cognitive load**: Focus on one task at a time
- **Clear progression**: Auto-advance to next task
- **Motivation**: See completed tasks in collapsible view
- **Flexibility**: Teachers can enable "show all" mode if needed

### For Teachers
- **Scaffolding**: Guide students through complex tasks step-by-step
- **Differentiation**: Set different subtasks for different students
- **Pacing control**: Bulk assign same subtask to entire class
- **Flexibility**: Can switch between guided and self-directed modes

### Technical
- **Backward compatible**: NULL = show all (original behavior)
- **Database efficient**: Single column addition, minimal queries
- **Self-maintaining**: Auto-advance handles progression automatically
- **Flexible**: Easy to add more features (e.g., hide completed tasks)
