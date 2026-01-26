# Task Plan: __pycache__ Investigation and Performance Optimization

## Goal
Investigate why VPS has fewer __pycache__ files than local development, verify if Python bytecode caching is working effectively, and assess performance optimization recommendations.

## Phases
- [x] Phase 1: Create plan and identify investigation areas
- [x] Phase 2: Analyze __pycache__ structure on both environments
- [x] Phase 3: Investigate Python import behavior and caching
- [x] Phase 4: Review current performance recommendations
- [x] Phase 5: Deliver findings and actionable insights

## Key Questions
1. Why does VPS have only 3 .pyc files while local has many more?
2. Is Python effectively using bytecode caching to speed up the app?
3. Does __pycache__ actually impact runtime performance significantly?
4. Are the current optimization recommendations still valid?

## Decisions Made
- Will examine actual Python files to understand import patterns
- Will check if __pycache__ differences indicate a problem or are normal

## New Information
- User added `Environment="PYTHONPYCACHEPREFIX=/opt/lernmanager/instance/tmp"` to systemd service
- After restart, more .pyc files appeared
- This suggests a permissions or directory access issue was limiting .pyc creation

## Errors Encountered
None yet.

## Status
**All Phases Complete** - Investigation finished, findings delivered in pycache_explained.md

## Analysis Complete

### Root Cause Identified
The VPS had only 3 .pyc files because of **write permissions issue** in `/opt/lernmanager/__pycache__`. The systemd service user couldn't create bytecode cache files.

### Solution Implemented
Adding `PYTHONPYCACHEPREFIX=/opt/lernmanager/instance/tmp` redirects all .pyc files to a writable location.

### Performance Impact Assessment
- **Startup cost:** ~50-100ms per server restart (low impact)
- **Runtime cost:** Zero (bytecode loaded in memory)
- **User-facing impact:** None (waitress workers persist)

### Original Recommendations Still Valid
Priority order unchanged:
1. HTTP caching (highest impact)
2. Template caching (high impact)
3. Increase waitress threads (medium impact)
4. Gzip compression (medium impact)
5. __pycache__ fix (low impact - now resolved)
