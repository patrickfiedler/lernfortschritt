# Notes: Lernmanager Improvements Research

## 1. URL Improvements

### Current URL Patterns

**Total Routes: 60** (3 auth, 7 student, 49 admin, 1 shared)

#### Student Routes (7 total)
- `/schueler` - Dashboard
- `/schueler/klasse/<int:klasse_id>` - Class detail ⚠️ ISSUE
- `/schueler/aufgabe/<int:student_task_id>/quiz` - Quiz
- `/schueler/aufgabe/<int:student_task_id>/teilaufgabe/<int:subtask_id>` - Toggle subtask
- `/schueler/unterricht/<int:unterricht_id>/selbstbewertung` - Self-evaluation
- `/schueler/bericht` - Download report

**Key Issue:** Student sees `/schueler/klasse/1` - numeric ID not human-friendly

#### Admin Routes - Examples of Complex URLs
- `/admin/schueler/<int:student_id>/klasse/<int:klasse_id>/abschliessen` - 2 IDs
- `/admin/klasse/<int:klasse_id>/unterricht/<datum>` - ID + date string
- `/admin/wahlpflicht/<int:gruppe_id>/aufgabe/<int:task_id>/entfernen` - 2 IDs

#### ID Types Used
1. `klasse_id` - Class ID
2. `student_id` - Student ID
3. `task_id` - Task ID
4. `student_task_id` - Assignment ID (joins student+task)
5. `subtask_id` - Subtask ID
6. `material_id` - Material ID
7. `unterricht_id` - Lesson session ID
8. `gruppe_id` - Elective group ID
9. `datum` - Date string (YYYY-MM-DD)

### Flask Routing Options

Flask supports:
1. **Integer converters**: `<int:id>` (current approach)
2. **String converters**: `<string:slug>`
3. **UUID converters**: `<uuid:id>`
4. **Path converters**: `<path:path>` (captures /)
5. **Custom converters**: Can define custom regex-based converters

#### Slug-Based Routing Examples
```python
# Option A: Full slug replacement
/schueler/klasse/mathematik-5a  # Instead of /schueler/klasse/1

# Option B: Hybrid (ID + slug for readability)
/schueler/klasse/1-mathematik-5a  # Parse first part as ID

# Option C: Named routes with query params
/schueler/klasse?name=mathematik-5a
```

### Trade-offs Analysis

#### Option A: Pure Slug-Based URLs

**Pros:**
- Human-readable and memorable
- Better for bookmarks/sharing
- Professional appearance
- SEO benefits (not relevant for auth-required app)

**Cons:**
- Requires slug column in database (schema change)
- Slug generation logic (unique, URL-safe)
- Slug uniqueness constraints (what if two "Mathe 5a"?)
- Migration complexity (existing links break)
- Need slug regeneration if name changes
- Slightly slower DB queries (index on slug vs primary key)

**Impact:**
- Database: Add `slug` columns to `klasse`, `task`, `student` tables
- Routes: Change `<int:id>` to `<string:slug>` in ~30 routes
- Queries: Change from `WHERE id = ?` to `WHERE slug = ?`
- Estimated effort: Medium-High (2-3 days)

#### Option B: Hybrid URLs (ID + Slug)

**Pros:**
- Human-readable
- Backward compatible (can ignore slug part)
- No uniqueness issues (ID is primary)
- Simpler migration

**Cons:**
- URLs longer
- Slug can drift from actual name (confusing)
- Still need slug generation

**Impact:**
- Database: Add `slug` columns (optional, can generate on-the-fly)
- Routes: Custom converter to parse `1-mathematik-5a` → extract 1
- Estimated effort: Medium (1-2 days)

#### Option C: Keep IDs, Improve Context

**Pros:**
- No code changes needed
- No migration needed
- Fast DB queries
- Simple and reliable

**Cons:**
- URLs still not human-friendly
- Students see meaningless numbers

**Impact:**
- Add breadcrumbs showing "Mathematik 5a" in UI
- Improve page titles
- Estimated effort: Low (few hours)

### Recommendation

For this application:
- **Option C (Keep IDs + Improve Context)** is recommended
- Reasons:
  1. Internal school app (not public-facing)
  2. Students bookmark rarely (use dashboard)
  3. Teachers use bookmarks but know their class IDs
  4. Migration risk vs benefit is not worth it
  5. Can improve UX with better breadcrumbs/titles instead

**If slugs are desired:**
- **Option B (Hybrid)** is safer - no breaking changes

---

## 2. Database Performance

### Current Setup

**Database:** SQLite with optional SQLCipher encryption
**Connection Strategy:** Create new connection per request
**File:** `data/mbi_tracker.db` (456 KB)

#### Encryption Implementation (models.py:13-73)

```python
SQLCIPHER_KEY = os.environ.get('SQLCIPHER_KEY')
USE_SQLCIPHER = False

if SQLCIPHER_KEY:
    try:
        from sqlcipher3 import dbapi2 as sqlite3
        USE_SQLCIPHER = True
    except ImportError:
        import sqlite3  # Fallback to unencrypted
```

**Encryption is OPTIONAL** - controlled by environment variable

#### Current Connection Pattern

```python
def get_db():
    conn = sqlite3.connect(config.DATABASE)
    conn.row_factory = sqlite3.Row
    if USE_SQLCIPHER and SQLCIPHER_KEY:
        conn.execute(f'PRAGMA key = "{safe_key}"')

    # Performance optimizations
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def db_session():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()  # ⚠️ Closes after each request
```

**Current behavior:**
- Every route → `db_session()` → new connection → close
- Multiple queries per request = multiple `db_session()` calls
- No connection pooling

### Encryption Analysis

#### Why was SQLCipher added?
- Added via `migrate_to_sqlcipher.py` (in codebase)
- Protects student data at rest
- Compliance with data protection regulations (GDPR)

#### Performance Impact of Encryption

**Theoretical overhead:**
- Encryption: ~5-15% CPU overhead per query
- Key derivation on connect: ~50-100ms first time
- Cached in memory after first PRAGMA key

**Actual impact (based on existing optimizations):**
- Already using WAL mode (journal_mode=WAL)
- Already using NORMAL synchronous (vs FULL)
- Previous optimization: 84ms → 10-20ms per request
- Encryption overhead: Likely <5ms per request

**Recommendation:** Keep encryption unless specific performance issue identified

### Connection Pooling Options

#### Current Problem
Each request creates new connection:
```
Request → get_db() → connect() → set PRAGMAs → query → close()
```

**Overhead per connection:**
- File open: ~1-2ms
- PRAGMA execution: ~1-2ms
- Encryption key setup: ~1-2ms (if encrypted)
- Total: ~3-6ms per request

#### Solution 1: Flask-SQLAlchemy with Connection Pooling

**Pros:**
- Built-in connection pool
- ORM features (if desired)
- Industry standard

**Cons:**
- Major refactor (all raw SQL → SQLAlchemy ORM)
- Learning curve
- Heavier dependency

**Estimated effort:** Very High (1-2 weeks)

#### Solution 2: Simple Connection Pool (Custom)

**Pros:**
- Keep raw SQL queries
- Minimal code changes
- Control over pool size

**Cons:**
- Need to implement pool logic
- Thread safety considerations (Flask is multi-threaded with waitress)
- Complexity in handling SQLCipher key

**Estimated effort:** Medium (2-3 days)

#### Solution 3: Application-Level Connection Caching

**Pros:**
- Simplest approach
- Reuse connection within same request
- No threading complexity (request-scoped)

**Cons:**
- Only helps if multiple `db_session()` calls per request
- Doesn't help across requests

**Implementation:**
```python
from flask import g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(config.DATABASE)
        # ... set PRAGMAs
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()
```

**Estimated effort:** Low (few hours)

### Performance Benchmarks Needed

To decide on database changes, measure:

1. **Current performance:**
   - Request latency (already logged via analytics)
   - Database connection time
   - Query execution time

2. **Bottleneck identification:**
   - Is connection creation the bottleneck?
   - Or are queries slow?
   - Or is rendering slow?

3. **Test scenarios:**
   - Admin dashboard (lists classes, students, tasks)
   - Student dashboard (lists classes, active tasks)
   - Unterricht page (many students + ratings)

### Recommendation: Database Performance

**Priority Order:**

1. **Measure first** - Profile current performance
   - Add timing logs to `get_db()`
   - Measure connection vs query time
   - Identify actual bottleneck

2. **Quick win: Request-level caching** (Option 3)
   - Low effort, safe change
   - Helps pages with multiple queries
   - ~2-4ms savings per request (estimate)

3. **Keep encryption** unless proven bottleneck
   - Data protection is important
   - Overhead is minimal with WAL mode

4. **Connection pooling** only if proven necessary
   - SQLite handles concurrent reads well with WAL
   - Writes are serialized anyway (SQLite limitation)
   - Pool mainly helps with connection overhead

**Decision:** Don't remove encryption. Test request-level connection caching first.

---

## 3. Student Experience

### User Requirements (from questions)

#### Student Demographics
- **Age range:** Mixed 10-18 years
- **Tech level:** Varies - must work for youngest while not feeling childish for older students

#### Devices Used (multi-device)
- Desktop computers (school computer lab)
- Personal tablets (iPad, Android tablets)
- Smartphones (iOS/Android)
- Chromebooks or laptops

**Implication:** Responsive design is critical. Touch-friendly UI needed.

#### Usage Contexts (multiple scenarios)
- During class (teacher-guided) - quick access is important
- Self-paced learning (in class) - independent work
- Quick progress checks - brief status views

**Implication:** Interface must support both focused work sessions and quick check-ins.

#### Main Problems to Solve
User's feedback: "It's a mixture. It feels like paperwork, so it could be more engaging. I don't want it to be childish, I don't want it to be gamified either."

**Key insights:**
1. **Terminology change needed:**
   - Current "tasks" → rename to "topics"
   - Current "subtasks" → rename to "tasks"

2. **"Why do I need this?" is critical:**
   - Students keep asking this question
   - Needs to be part of every topic
   - Should be tailored to age group
   - Must be visible but not intrusive

3. **Current workflow problem:**
   - Students go from dashboard → topic view
   - First thing they see: general task description
   - They want to see it, but NOT as first thing every time
   - Should be accessible but not prominent

4. **Subtask visibility issue:**
   - Currently: If admin sets specific subtask, students ONLY see that one
   - Students don't see previous or next subtasks
   - Need visual progress indicator (completed vs open)
   - Need ability to move between subtasks

5. **Design principles:**
   - Simplicity and focus are key
   - Highlight current subtask prominently
   - Move general topic description below
   - Make description viewable with click, hideable again

### Design Decisions (from follow-up questions)

#### 1. "Why do I need this?" Section
**Decision:** In the topic header (always visible, brief)
- Short sentence or two at top of topic page
- Always visible
- Example: "You'll use this to understand climate change patterns"
- **Note:** User wants help generating these during implementation

#### 2. After Subtask Completion
**Decision:** Show success message + manual 'Next' button
- Celebrate completion briefly
- Student clicks 'Next task' to continue
- Gives sense of accomplishment
- Maintains momentum while allowing control

#### 3. Subtask Access Control
**Decision:** Allow navigation to completed subtasks (review past work)
- Students can go back to review completed subtasks
- Cannot jump ahead to future ones
- Provides review capability while maintaining progression

#### 4. Visual Style
**Decision:** User wants to see mockups for all 3 styles
- Style 1: Clean and minimal (productivity apps)
- Style 2: Warm and friendly (educational but mature)
- Style 3: Bold and focused (clear visual hierarchy)
- **Action:** Created 3 HTML mockups for preview

#### 5. Progress Indicator Format
**Decision:** Text plus dots/circles
- Combine text ("3 of 8 tasks complete") with visual dots
- Each subtask shown as dot - filled for complete, empty for incomplete, highlighted for current

#### 6. Context Display
**Decision:** Minimal breadcrumb (e.g., 'Math > Climate Topics')
- Small text showing where they are
- Not prominent - focuses on content
- Good for orientation without distraction

#### 7. Topic Description Display
**Decision:** Slide down/expand in place, but move topic description below current subtask
- Accordion-style expansion
- Keeps subtask near top of page
- All content visible on one page
- Doesn't affect layout of current task

### Redesign Requirements Summary

#### Information Hierarchy (top to bottom)
1. **Minimal breadcrumb** - Where am I?
2. **"Why do I need this?"** - Brief, always visible, at top
3. **Progress indicator** - Text + dots showing completed/current/remaining
4. **Current task** - Prominent, focused
5. **Completion checkbox** - Clear action
6. **Success message** (after completion) - Brief celebration
7. **Next button** (after completion) - Continue to next task
8. **Topic description** (expandable) - General info, minimized by default

#### Key Interactions
- **Mark complete:** Checkbox → Success message appears → Next button appears
- **Next task:** Click button → Navigate to next task in sequence
- **View topic info:** Click to expand → Slides down below current task
- **Navigate subtasks:** Can click on completed subtask dots to review past work
- **Return to dashboard:** Breadcrumb link

#### Terminology Changes Required
- Database/models: Keep internal names (backward compatibility)
- UI only: "Aufgabe" → "Thema", "Teilaufgabe" → "Aufgabe"
- Affects: templates, labels, headings

### Technical Considerations

#### Responsive Design Needs
- Desktop: Full width layout (max-width ~800-1000px)
- Tablet: Touch-friendly buttons (min 44px tap targets)
- Mobile: Single column, larger text, bottom navigation

#### Accessibility
- Keyboard navigation for all interactions
- ARIA labels for screen readers
- Color contrast ratios (WCAG AA minimum)
- Focus indicators on interactive elements

#### Performance
- Keep current fast loading
- Minimal JavaScript (progressive enhancement)
- Lazy load topic description content if large

### Mockups Created

Three HTML mockup files for user preview:

1. **mockup_style_1_clean_minimal.html**
   - Lots of white space
   - Simple icons
   - Clear typography
   - Professional but not boring
   - Like Google Classroom aesthetic

2. **mockup_style_2_warm_friendly.html**
   - Softer colors (warm gradients)
   - Friendly but not childish illustrations
   - Comfortable spacing
   - Approachable for younger students
   - Not patronizing for older ones

3. **mockup_style_3_bold_focused.html**
   - Strong contrasts
   - Clear sections
   - Obvious 'what to do next'
   - Prioritizes clarity and action
   - Bold visual hierarchy

All mockups include:
- Minimal breadcrumb navigation
- "Why do I need this?" section at top
- Progress indicator (text + dots)
- Current task prominently displayed
- Completion checkbox
- Success message (shows on check)
- Next button (shows on check)
- Expandable topic description (below)
- Interactive demo of completing a task

**Decision:** Hybrid design approved! (`mockup_hybrid_final.html`)

**Final design combines:**
- **From Style 2:** White content card containing all information (clear visual boundaries)
- **From Style 3:** Bold color scheme (dark header, blue gradient purpose banner, strong contrasts)
- **From Style 1:** Simple clean progress dots (no checkmarks, just colored circles)

This creates a professional, focused interface that works for ages 10-18 without being childish or gamified.

### Current User Flows
(To be populated during research)

### User Requirements
(To be gathered via questions)

### Design Patterns for Students
(To be researched)

### Cognitive Load Analysis
(To be analyzed)
