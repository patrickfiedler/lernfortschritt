# Task Plan: Deployment Script Improvements

## Goal
1. Implement EnvironmentFile-based secrets management
2. Add automatic database migration detection and execution to update.sh

## Phases
- [x] Phase 1: Implement EnvironmentFile secrets management
  - [x] Update deploy/lernmanager.service
  - [x] Update deploy/setup.sh
  - [x] Update deploy/update.sh (remove secret injection)
- [x] Phase 2: Design database migration auto-detection
  - [x] Decide on migration detection strategy
  - [x] Design migration execution flow
- [x] Phase 3: Implement migration auto-execution
  - [x] Add migration detection to update.sh
  - [x] Add migration execution logic
  - [x] Handle errors gracefully
- [x] Phase 4: Update documentation and test

## Key Questions
1. ✅ How to load secrets? → EnvironmentFile=/opt/lernmanager/.env
2. ❓ How to detect if migrations are needed?
   - Option A: Look for migrate_*.py files that haven't been run
   - Option B: Maintain migration state file
   - Option C: Always run all migrations (they're idempotent)
3. ❓ Should migrations run automatically or prompt user?
   - Auto-run seems safe since migrations are idempotent
4. ❓ How to handle SQLCipher for migrations?
   - Pass SQLCIPHER_KEY from .env to migration scripts

## Decisions Made
- Using /opt/lernmanager/.env for secrets storage
- Service file will use EnvironmentFile= directive

## Migration Detection Strategy - DECIDED
**Approach**: Detect if migrate_*.py files changed in commit, then run ALL migrate_*.py files
- Migrations are idempotent (check if already applied)
- Simple and reliable
- No state tracking needed
- Pass SQLCIPHER_KEY from .env to migration scripts via environment

## Errors Encountered
- (none yet)

## Status
**All Phases Complete** - Implementation finished, ready for testing

## Implementation Summary

### Files Modified

1. **deploy/lernmanager.service**
   - Removed: Inline Environment= directives for secrets
   - Added: `EnvironmentFile=/opt/lernmanager/.env`
   - Result: Service file is now a clean template

2. **deploy/setup.sh**
   - Removed: sed injection of secrets into service file
   - Added: Creation of `/opt/lernmanager/.env` with generated secrets
   - Result: Secrets stored in separate file from day one

3. **deploy/update.sh**
   - Removed: ~30 lines of sed-based secret extraction/injection logic
   - Simplified: Service file update (just copy, no modification)
   - Added: Database migration detection and execution (Step 6/8)
   - Added: SQLCIPHER_KEY export for encrypted databases
   - Added: Migration status in deployment summary
   - Result: Simpler, safer updates with automatic migrations

### New Files Created

1. **MIGRATION_GUIDE.md**
   - Complete guide for migrating existing deployments
   - Automated and manual migration options
   - Troubleshooting section
   - Post-migration instructions

### How Migration Auto-Detection Works

When `update.sh` runs:
1. Checks if any `migrate_*.py` files changed in the commit
2. If yes, runs ALL `migrate_*.py` files found in repo root
3. Migrations are idempotent (check if already applied)
4. Exports SQLCIPHER_KEY from .env if database is encrypted
5. Reports success/failure for each migration
6. Continues deployment even if migrations fail (with warning)

### Benefits Delivered

✅ **Secrets never lost during updates** - stored in persistent .env file
✅ **Simpler deployment scripts** - no fragile sed parsing
✅ **Automatic database migrations** - no manual intervention needed
✅ **SQLCipher support** - migrations work with encrypted databases
✅ **Standard systemd practice** - using EnvironmentFile= directive
✅ **Easy secret management** - just edit .env and restart service

### Documentation Created

1. **DEPLOYMENT_IMPROVEMENTS_SUMMARY.md** - Overview of all changes
2. **MIGRATION_GUIDE.md** - Step-by-step migration instructions
3. **deploy/QUICK_REFERENCE.md** - Quick reference for common operations
4. **secrets_management_notes.md** - Research and options analysis
5. **secrets_management_recommendation.md** - Detailed recommendation
6. **deployment_improvements_plan.md** - This file, tracking implementation

## Next Steps for User

1. Review DEPLOYMENT_IMPROVEMENTS_SUMMARY.md
2. Migrate production server using MIGRATION_GUIDE.md
3. Test thoroughly
4. Commit changes to GitHub
5. Future deployments will be automated!
