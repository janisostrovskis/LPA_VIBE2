---
simplify: PASS
date: 2026-04-10
sub-phase: 02a-H1
agent: database-agent
---

# Simplify Receipt — 02a-H1

## Findings & Fixes

1. **URL scheme rewriting duplication** — `_async_database_url()` in `session.py` and `_async_url()` in `alembic/env.py` were identical. Extracted to `backend/app/infrastructure/database/url.py` → `to_async_url()`. Both files now import from the shared module.

2. **Stringly-typed `preferred_locale`** — `Member.preferred_locale` was `str` with a comment "lv | en | ru", but `Locale(StrEnum)` already existed. Changed to `Locale` type for compile-time safety.

3. **Module-level engine creation** — `session.py` created `_engine` and `AsyncSessionFactory` at import time, triggering `get_settings()` and `create_async_engine()` during module import. Refactored to lazy `@lru_cache` factory functions (`_get_engine()`, `_get_session_factory()`) so no I/O occurs until first use.

4. **Redundant unique index on `magic_link_tokens.token`** — Migration had both `UniqueConstraint("token")` and a separate `create_index(..., unique=True)` on the same column. Removed the redundant index from migration and `index=True` from the model's `mapped_column`.
