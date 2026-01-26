# Task Plan: Improve Secrets Management in Deployment

## Goal
Move secrets from systemd service file to a separate file that persists across updates, preventing secret loss when service file changes.

## Phases
- [x] Phase 1: Research current implementation
- [x] Phase 2: Evaluate options for secrets management
- [x] Phase 3: Design recommended solution
- [x] Phase 4: Document implementation plan

## Key Questions
1. How are secrets currently handled in setup.sh and update.sh?
2. What are the standard approaches for systemd secrets management?
3. Which option best fits this project's simplicity and security needs?
4. What changes are needed to setup.sh, update.sh, and service file?

## Decisions Made
- (to be filled during research)

## Errors Encountered
- (none yet)

## Status
**All Phases Complete** - Comprehensive recommendation delivered

## Summary

Created comprehensive analysis with:
1. **secrets_management_notes.md** - Research findings on current implementation and all options
2. **secrets_management_recommendation.md** - Detailed implementation guide

**Recommendation**: Use systemd's `EnvironmentFile=` directive to load secrets from `/opt/lernmanager/.env`

This solves the problem by:
- Separating secrets from service file template
- Eliminating brittle sed parsing logic
- Making updates safer and simpler
- Following systemd best practices

## Decisions Made
- **Option 1 (EnvironmentFile=)** is the best fit for this project
  - Standard systemd feature
  - Clean separation
  - Low complexity
  - No app code changes needed
