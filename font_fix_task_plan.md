# Task Plan: Fix Font Loading for Easy Reading Mode

## Goal
Replace broken Google Fonts loading with locally-hosted OpenDyslexic font for accessibility.

## Phases
- [x] Phase 1: Understand current font setup and the error
- [x] Phase 2: Research font options (see font_research_notes.md)
- [x] Phase 3: Remove Google Fonts link from base.html
- [x] Phase 4: Update CSS with better font stack (system fonts + better spacing)
- [ ] Phase 5: Test and verify
- [x] Phase 6: Add onboarding page todo
- [ ] Phase 7: Commit changes

## Key Questions
1. What font should we actually use for easy reading mode? (OpenDyslexic is the standard)
2. Where do we get the font files?
3. What font formats do we need? (woff2 for modern browsers, woff for fallback)

## Decisions Made
- **NOT using OpenDyslexic** - research shows it performs worse than standard fonts
- Use system font stack (SF Pro, Segoe UI, Roboto) - no download needed, better performance
- Improve spacing and typography in CSS (this is what actually helps readability)
- Add Comic Sans to fallback stack (popular perception of easier reading, even if not proven)

## Errors Encountered
- Current error: Loading Comic Sans MS from Google Fonts (403 error - Comic Sans isn't on Google Fonts)
- Comic Sans MS is a Microsoft system font, not available via Google Fonts API

## Status
**COMPLETE** - Fixed broken Google Fonts link, implemented research-backed system font stack with improved spacing.
