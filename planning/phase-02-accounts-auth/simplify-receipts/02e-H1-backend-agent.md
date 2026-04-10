---
simplify: PASS
date: 2026-04-10
sub-phase: 02e-H1
agent: backend-agent
---

# Simplify Receipt — 02e-H1

Reviewed API routes, middleware, DI wiring, and FastAPI app. Fixes applied:
- 204 routes: `response_model=None` to prevent FastAPI response body assertion
- Deprecated `HTTP_422_UNPROCESSABLE_ENTITY` → literal `422`
- Import ordering: moved `_bearer = HTTPBearer()` after all imports (E402)
- TypeVar `_T` → PEP 695 type param `T` (UP047/UP049)
- Unused `Response` import removed from auth.py and organizations.py
- Line length fix in organizations.py import
- mypy override extended to cover `app.api.routes.*` for Pydantic models
