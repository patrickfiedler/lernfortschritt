# Task Plan: Fix NS_ERROR_REDIRECT_LOOP on VPS

## Goal
Diagnose and fix the redirect loop error preventing access to the Lernmanager app on VPS.

## Phases
- [x] Phase 1: Gather VPS deployment information
- [x] Phase 2: Check nginx/web server configuration
- [x] Phase 3: Examine Flask app configuration
- [x] Phase 4: Create and document fix

## Key Questions
1. Is nginx configured correctly for the Flask app?
2. Are there conflicting redirect rules?
3. Is HTTPS/HTTP redirect causing the loop?
4. Is the systemd service running correctly?

## Decisions Made
- **Fix approach**: Use explicit FORCE_HTTPS env var instead of FLASK_ENV check
- **Reasoning**: Safer default (HTTP works), explicit HTTPS opt-in, clearer intent

## Errors Encountered
- NS_ERROR_REDIRECT_LOOP: User cannot access app on VPS (browser error)

## Status
**COMPLETE** - Fix implemented and documented

**ROOT CAUSE:**
SESSION_COOKIE_SECURE=True was enabled (via FLASK_ENV=production) but site was accessed over HTTP. Browser couldn't save session cookies, causing infinite redirect loop.

**SOLUTION:**
Changed to use explicit FORCE_HTTPS environment variable. Now works over HTTP by default, and HTTPS-only cookies can be enabled after SSL configuration.
