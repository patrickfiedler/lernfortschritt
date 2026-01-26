# Deployment Improvements (January 26, 2026)

## Summary
Major overhaul of deployment system to address two critical issues:
1. Secrets management using systemd EnvironmentFile
2. Automatic database migration execution

## Problem
- Secrets were extracted/injected from service file using brittle sed parsing
- Database migrations had to be run manually (often forgotten)

## Solution
- Moved secrets to `/opt/lernmanager/.env` loaded via `EnvironmentFile=`
- Added automatic migration detection and execution to `update.sh`

## Impact
- Eliminated ~40 lines of complex sed logic
- Secrets now persist across all service file updates
- Migrations run automatically on deployment
- Safer, simpler deployments

## Related Commit
- `5c9680f` - feat: improve deployment with EnvironmentFile secrets and auto-migrations

## Files
- `secrets_management_notes.md` - Research on all options
- `secrets_management_plan.md` - Implementation tracking
- `secrets_management_recommendation.md` - Detailed design document
- `deployment_improvements_plan.md` - Overall implementation plan
- `oneliner_update_summary.md` - Migration script updates
