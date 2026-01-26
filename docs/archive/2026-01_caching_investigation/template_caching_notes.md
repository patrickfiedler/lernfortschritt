# Notes: Template Caching Implementation

## Current Application Analysis

### Templates Found (20 total)
**Admin templates:**
- `admin/dashboard.html` - Main landing page
- `admin/klassen.html` - Class list
- `admin/klasse_detail.html` - Class detail with students
- `admin/schueler_detail.html` - Student detail
- `admin/aufgaben.html` - Task list
- `admin/aufgabe_detail.html` - Task detail
- `admin/aufgabe_form.html` - Task create/edit
- `admin/unterricht.html` - Lesson attendance/evaluation
- `admin/analytics.html` - Analytics dashboard
- `admin/student_activity.html` - Student activity
- `admin/wahlpflicht.html` - Elective courses
- `admin/passwort.html` - Password management
- `admin/errors.html` - Error log

**Student templates:**
- `student/dashboard.html` - Student dashboard
- `student/klasse.html` - Class/task view
- `student/quiz.html` - Quiz taking
- `student/quiz_result.html` - Quiz result

**Shared:**
- `login.html` - Login page
- `base.html` - Base template
- `error.html` - Error page

### Current Dependencies
```
Flask>=2.0
Flask-WTF>=1.0
waitress>=2.0
markdown>=3.4
reportlab>=4.0
sqlcipher3-binary>=0.5.0
```

**Missing:** Flask-Caching (need to add)

## Template Caching Strategy

### Caching Approach Decision

#### Option 1: Full Response Caching with @cache.cached()
Cache entire rendered HTML responses.

**Pros:**
- Simple decorator approach
- Caches complete HTML output
- Good for pages that don't change often

**Cons:**
- User-specific content (session data) can't be cached
- CSRF tokens need special handling
- All-or-nothing approach

#### Option 2: Fragment/Query Caching with @cache.memoize()
Cache database queries and expensive computations, not full templates.

**Pros:**
- More granular control
- Can cache data while keeping user-specific UI
- Safer with session/CSRF
- Better for dynamic, personalized pages

**Cons:**
- Requires more code changes
- Need to identify slow queries first

**DECISION: Use Option 2 (Fragment Caching)**

The Lernmanager app has:
- User-specific navigation (admin vs student)
- Session-based authentication
- CSRF-protected forms everywhere
- Per-user data (student progress, admin classes)

Full response caching would break these features. Fragment caching is the right approach.

## High-Value Caching Targets

### Database Query Analysis

#### Frequently Called Queries (Cache Candidates)
1. **`get_all_klassen()`** - Returns all classes
   - Called on: admin dashboard, class list, task assignment
   - Frequency: High
   - Change rate: Low (classes created rarely)
   - Cache timeout: 5 minutes

2. **`get_all_tasks()`** - Returns all learning tasks
   - Called on: admin task list, task assignment pages
   - Frequency: High
   - Change rate: Low (tasks updated occasionally)
   - Cache timeout: 5 minutes

3. **`get_klasse_by_id(id)`** - Single class details
   - Called on: class detail page, student assignment
   - Frequency: Very high
   - Change rate: Low
   - Cache timeout: 5 minutes

4. **`get_students_in_klasse(klasse_id)`** - Students in a class
   - Called on: class detail, attendance, task assignment
   - Frequency: Very high
   - Change rate: Medium (students added/removed occasionally)
   - Cache timeout: 2 minutes

5. **`get_student_tasks(student_id, klasse_id)`** - Student's assigned tasks
   - Called on: student dashboard, progress tracking
   - Frequency: Very high (every student page load)
   - Change rate: Medium (tasks assigned/completed)
   - Cache timeout: 1 minute

#### Expensive Aggregations (Cache Candidates)
1. **Dashboard statistics** - Task counts, completion rates
2. **Analytics queries** - Event aggregations over time ranges
3. **Student progress calculations** - Completion percentages

### Cache Key Strategy

Use specific IDs to avoid cache collisions:
```python
# Class list (per admin, though same for all admins)
key = f"classes_list"

# Single class details
key = f"class_{klasse_id}"

# Students in class
key = f"class_{klasse_id}_students"

# Student tasks
key = f"student_{student_id}_class_{klasse_id}_tasks"

# Task details
key = f"task_{task_id}"
```

### Cache Invalidation Strategy

#### Time-Based Expiration
Primary strategy: Let cache expire naturally
- Stable data (classes, tasks): 5 minutes
- Medium volatility (student lists): 2 minutes
- High volatility (student progress): 1 minute

#### Manual Invalidation (Optional Enhancement)
Clear cache on data modifications:
```python
@cache.delete_memoized(get_klasse_by_id, klasse_id)
@cache.delete_memoized(get_students_in_klasse, klasse_id)
```

**Start without manual invalidation** - Time-based is simpler and sufficient for this use case.

## Cache Backend Selection

### SimpleCache (In-Memory)
**Pros:**
- ✅ No external dependencies
- ✅ Fast (RAM access)
- ✅ Simple setup (zero config)
- ✅ Built into Flask-Caching

**Cons:**
- ❌ Loses cache on server restart
- ❌ Not shared across processes (though waitress uses threads, not processes)

### RedisCache
**Pros:**
- ✅ Persistent across restarts
- ✅ Shared across multiple app instances
- ✅ Production-grade

**Cons:**
- ❌ Requires Redis server (additional dependency)
- ❌ More complex deployment
- ❌ Network overhead (though minimal on localhost)

### FileSystemCache
**Pros:**
- ✅ Persistent across restarts
- ✅ No external dependencies
- ✅ Simple

**Cons:**
- ❌ Slower than memory
- ❌ Disk I/O overhead
- ❌ Not ideal for high-traffic

**DECISION: Start with SimpleCache**

Reasons:
1. Lernmanager is single-server deployment
2. Waitress uses threads (shared memory), not processes
3. Zero configuration needed
4. Can upgrade to Redis later if needed
5. Cache warmup after restart is fast enough

## Implementation Plan

### Step 1: Add Flask-Caching Dependency
Update `requirements.txt`:
```
Flask-Caching>=2.0
```

### Step 2: Initialize Flask-Caching in app.py
```python
from flask_caching import Cache

# After app initialization
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes default
})
```

### Step 3: Wrap Frequently-Called Functions in models.py

Add caching to key functions:
```python
from flask import current_app

# In models.py, after imports
cache = None  # Will be set by app.py

def get_all_klassen():
    # Existing code, wrapped with @cache.memoize(timeout=300)

def get_klasse_by_id(klasse_id):
    # Existing code, wrapped with @cache.memoize(timeout=300)

def get_students_in_klasse(klasse_id):
    # Existing code, wrapped with @cache.memoize(timeout=120)
```

### Step 4: Test Caching
- Load pages and verify response times improve
- Check cache hit rates (if Flask-Caching provides stats)
- Verify data freshness (changes appear within timeout)

### Step 5: Optional Monitoring
Add cache statistics endpoint (admin-only):
```python
@app.route('/admin/cache_stats')
@admin_required
def cache_stats():
    stats = cache.get_stats()  # If available
    return jsonify(stats)
```

## Expected Performance Impact

### Baseline (No Caching)
Every page load = multiple database queries:
- Dashboard: 3-5 queries
- Class detail: 5-10 queries
- Student dashboard: 3-7 queries

**Estimated time:** 5-20ms per page in query overhead

### With Caching
First load: Same as baseline (cache miss)
Subsequent loads: Cache hits
- get_all_klassen(): 5ms → <0.1ms
- get_students_in_klasse(): 3ms → <0.1ms
- get_student_tasks(): 5ms → <0.1ms

**Estimated improvement:** 10-15ms saved per cached page load
**Cache hit rate:** Expect 70-90% for frequently-accessed pages

### Real-World Impact
- Admin viewing class list repeatedly: Much faster
- Students checking dashboard: Faster on repeated visits within 1 minute
- Overall: Noticeable but not dramatic (caching complements other optimizations)

## Risks and Mitigations

### Risk 1: Stale Data
**Scenario:** Teacher adds student, doesn't see them for 2 minutes

**Mitigation:**
- Use short timeouts (1-5 minutes)
- Consider manual cache invalidation for critical operations
- Acceptable trade-off for performance gain

### Risk 2: Memory Usage
**Scenario:** Cache grows too large, consumes RAM

**Mitigation:**
- SimpleCache has built-in size limits
- Data is small (few hundred students/classes max)
- Estimated memory: <10MB for typical school

### Risk 3: CSRF Token Caching
**Scenario:** Cached forms have invalid CSRF tokens

**Mitigation:**
- We're NOT caching full responses
- CSRF tokens generated fresh in templates
- Not a concern with fragment caching

## Success Criteria

1. **Performance:** Page load times improve by 10-20ms on cache hits
2. **Stability:** No new errors or bugs introduced
3. **Data freshness:** Changes appear within cache timeout (acceptable delay)
4. **Memory usage:** Minimal increase (<20MB)
5. **Code complexity:** Minimal changes, easy to maintain
