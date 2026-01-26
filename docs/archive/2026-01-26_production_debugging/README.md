# Production Debugging (January 26, 2026)

## Summary
Investigation and resolution of production server breakage after deployment.

## Problem
- Production server stopped working after recent commits
- Localhost worked fine, production failed
- Last known working: commit `06eb4af`

## Root Cause
Missing database migration - `migrate_add_why_learn_this.py` was not run on production server.

## Secondary Issue
HTTPS redirect loop due to `SESSION_COOKIE_SECURE` being enabled without HTTPS configured.

## Solutions
1. Run missing migration on production
2. Changed from `FLASK_ENV=production` to explicit `FORCE_HTTPS` env var

## Related Commits
- `da542cf` - fix: prevent redirect loop when HTTPS not configured

## Files
- `production_breakage_plan.md` - Investigation task plan
- `production_debug_notes.md` - Debugging findings
- `redirect_loop_notes.md` - HTTPS redirect investigation
- `redirect_loop_solution.md` - Solution documentation
- `redirect_loop_task_plan.md` - Implementation plan
- `vps_revert_guide.md` - Rollback instructions
