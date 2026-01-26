# Task Plan: Three Major Improvements to Lernmanager

## Goal
Research and plan three significant improvements: (1) human-friendly URLs, (2) database performance optimization, (3) redesigned student experience.

## Phases
- [x] Phase 1: Research URL routing patterns and Flask best practices
- [x] Phase 2: Research database performance (encryption removal, connection pooling)
- [x] Phase 3: Quiz user on student UX expectations and create mockups
- [x] Phase 4: Synthesize findings and create implementation roadmap
- [x] Phase 5: Update future_features_plan.md with new items

## Key Questions

### 1. URL Improvements
- What URLs currently exist in the app (student and admin)?
- What Flask URL routing features are available (slugs, converters, etc.)?
- What are the trade-offs between `/klasse/1` vs `/klasse/mathematik-5a`?
- How would this affect existing links, bookmarks, security?

### 2. Database Performance
- Why was SQLCipher encryption added originally? Security requirements?
- What's the actual performance impact of encryption?
- Can we use connection pooling with SQLite? Flask-SQLAlchemy or other solutions?
- What are the risks of removing encryption (compliance, data exposure)?
- How to migrate from encrypted to unencrypted database?

### 3. Student Experience Redesign
- What are the current student user flows?
- What do students see on each page (dashboard, task view, quiz)?
- What cognitive load issues exist (too much info at once)?
- What design patterns work for student-facing educational apps?
- User needs to answer:
  - Age range of students?
  - Primary use case (homework tracking, in-class work, both)?
  - Device usage (desktop, tablet, mobile)?
  - Current pain points from student feedback?
  - Desired behavior changes?

## Decisions Made
- Starting with comprehensive research before making recommendations
- Will gather user input on student UX via structured questions

## Errors Encountered
(None yet)

## Status
**ALL PHASES COMPLETE ✅** - Ready for implementation

## Design Decision
**Approved design:** `mockup_hybrid_final.html`
- Content card structure (Style 2)
- Bold colors (Style 3)
- Simple progress dots (Style 1)

## Deliverables Created
1. ✅ `improvements_notes.md` - Comprehensive research findings
2. ✅ `mockup_style_1_clean_minimal.html` - Clean design option
3. ✅ `mockup_style_2_warm_friendly.html` - Warm design option
4. ✅ `mockup_style_3_bold_focused.html` - Bold design option
5. ✅ `mockup_hybrid_final.html` - APPROVED hybrid design
6. ✅ `student_redesign_roadmap.md` - Implementation roadmap (20-25 hours)
7. ✅ `future_features_plan.md` - Updated with all improvements

## Recommendations Summary

### 1. URLs: Keep IDs, Improve Context
- **Action:** Add better breadcrumbs (included in student redesign)
- **Effort:** Low (part of redesign)
- **Priority:** Handled by other work

### 2. Database: Keep Encryption, Add Caching
- **Action:** Implement request-level connection caching
- **Effort:** 2-4 hours
- **Priority:** Quick win after student redesign

### 3. Student Experience: Full Redesign
- **Action:** Implement approved hybrid design
- **Effort:** 20-25 hours (3-4 days)
- **Priority:** HIGH - Ready to implement
