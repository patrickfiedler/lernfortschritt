# Caching Investigation (January 2026)

## Summary
Research into template caching and Python bytecode optimization.

## Topics Investigated
1. Jinja2 template caching mechanisms
2. Python `__pycache__` behavior
3. Template compilation optimization
4. Static file caching

## Key Findings
- Jinja2 automatically caches compiled templates in memory
- Python bytecode cache significantly improves startup time
- `PYTHONPYCACHEPREFIX` allows centralized cache location
- Template caching is already optimal by default

## Implementation
Added `PYTHONPYCACHEPREFIX=/opt/lernmanager/instance/tmp` to systemd service for better cache management.

## Related Commits
- `ee825f7` - perf: add PYTHONPYCACHEPREFIX to systemd service

## Files
- `jinja2_caching_investigation.md` - Jinja2 caching research
- `jinja2_caching_notes.md` - Implementation notes
- `template_caching_notes.md` - Template optimization findings
- `pycache_explained.md` - Python bytecode cache explanation
- `pycache_investigation.md` - Investigation details
- `pycache_notes.md` - Research notes
