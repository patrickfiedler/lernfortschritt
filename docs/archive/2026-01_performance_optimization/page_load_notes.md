# Page Load Performance Notes

## What We Fixed
- **Analytics logging**: 85ms → 0.02ms (eliminated this bottleneck)
- **WAL mode**: Enabled for better DB concurrency
- **Async logging**: All analytics events now queued

## Current Symptoms
- **Local dev**: 50-200ms per page load
- **Production VPS**: 400-1000ms per page load
- **Issue**: Pages still feel slow despite analytics fix

## Hypothesis
Analytics logging was only ONE source of delay. Other potential bottlenecks:
1. Database queries (per-page queries, not just analytics)
2. Template rendering
3. Static file serving
4. Network latency
5. Python/WSGI overhead
6. Nginx reverse proxy configuration

## Investigation Areas

### 1. Database Queries
Each page load likely involves:
- Session verification (check if user exists)
- Loading class data
- Loading student data
- Loading task data
- Loading materials
- Etc.

Each query could add 10-100ms on slow VPS storage.

### 2. Template Rendering
- Jinja2 template compilation
- Rendering loops (students, tasks, etc.)
- Markdown conversion
- Could add 10-50ms

### 3. @before_request Hook
Even though analytics is async now, what else happens in @before_request?
- Session checks?
- Database lookups?
- Authentication?

### 4. Static Files
- Are CSS/JS files being served by Flask or nginx?
- Are they gzip compressed?
- Are there many small files (multiple round trips)?

### 5. Network/Nginx
- Nginx → Python communication overhead
- No caching headers?
- No connection keepalive?

## Diagnostic Results

### Database Performance ✅ GOOD
- Database size: 0.45 MB (small)
- Common queries: <1ms each
- `get_all_klassen()`: 0.72ms
- `get_all_tasks()`: 0.82ms
- **Conclusion**: Database is NOT the bottleneck

### Static Files Analysis
- Total: 4 files, 1.6 MB
- Breakdown:
  - 1 PDF: 1.5 MB (large!)
  - 1 JS file: 39 KB (marked.min.js - markdown parser)
  - 1 CSS file: 16 KB
  - 1 favicon

**Potential Issue**: The 1.5MB PDF in static/ directory shouldn't be there

### Template Complexity
- Largest template: `admin/unterricht.html` - 474 lines
- Several templates: 200-300 lines
- **Potential Issue**: Large templates may render slowly

## Likely Bottlenecks (Based on Symptoms)

### Local (50-200ms)
If analytics logging was 10ms and now it's 0.02ms, where's the other 40-190ms?

Likely culprits:
1. **Template rendering**: 20-50ms (Jinja2 + markdown conversion)
2. **Multiple small queries**: 5-10 queries × 1ms = 5-10ms
3. **Python/Flask overhead**: 10-20ms
4. **Session handling**: 5-10ms
5. **WSGI overhead**: 5-10ms

### Production VPS (400-1000ms)
This is 2-5x worse than local. Why?

Likely culprits:
1. **Network latency**: nginx ↔ Python communication
2. **CPU performance**: VPS CPU slower than local
3. **Template rendering on slower CPU**: 50-200ms
4. **Multiple queries still slow**: Even 1ms × 10 queries = slower on VPS
5. **No caching**: Every request renders templates from scratch
6. **Waitress threading overhead**: Context switches

### What Analytics Logging Hid
We thought 85ms was the whole problem, but it was masking:
- The analytics write blocked everything else
- Now that it's async, we can see the OTHER delays
- These delays were always there, just harder to notice

## Next Steps
1. Check query count per page (N+1 queries?)
2. Profile template rendering time
3. Check nginx configuration (caching, gzip, keepalive)
4. Check if waitress is configured optimally
5. Consider template fragment caching for expensive renders
