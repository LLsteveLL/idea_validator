"""Persistence model notes.

The MVP uses SQLite directly through `app.db.session` instead of a full ORM.
The main persisted entity is an analysis record containing:
- the original idea input
- the final graph state
- the final API report
"""
