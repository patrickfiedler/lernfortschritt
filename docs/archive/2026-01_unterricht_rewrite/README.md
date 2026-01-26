# Unterricht Page Rewrite (January 2026)

## Summary
Complete redesign of the admin attendance/evaluation (unterricht) page.

## Problems
- Unclear what data was saved vs unsaved
- Confusing 1-2-3 rating scale
- No lesson-wide comment field

## Solution
**New Rating System:**
- Changed from `1-2-3` to `-` (criticism), `ok` (neutral), `+` (praise)
- Color-coded: red, yellow, green
- Default to "ok"

**Manual Save Workflow:**
- Clear visual indicators for unsaved changes
- Change tracking with counter
- Single save button for all changes
- Success feedback

**Additional Features:**
- Lesson-wide comment field
- Pre-defined comment dropdown (7 common phrases)
- Browser warning for unsaved changes

## Database Changes
- Migrated rating columns from INTEGER to TEXT
- Added `unterricht.kommentar` column for lesson comments

## Related Commits
- `c8e446f` - feat: complete rewrite of unterricht page with new rating system
- `21977bf` - chore: add database migration script for unterricht rating system

## Files
- `unterricht_rewrite_summary.md` - Complete implementation summary
