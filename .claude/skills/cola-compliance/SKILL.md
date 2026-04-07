---
name: cola-compliance
description: COLA architecture import rules and layer boundary enforcement. Preloaded into every agent to prevent layer violations.
disable-model-invocation: true
user-invocable: false
---

# COLA Compliance Rules

You MUST follow these import rules. Violations are build errors — the pre-commit hook `scripts/check_cola_imports.py` rejects commits that break them.

## Two-Service Architecture

| Service | Contains | Language |
|---------|----------|----------|
| `backend/` (FastAPI) | Domain + Application + Infrastructure + API adapter | Python |
| `frontend/` (Next.js) | Adapter layer only (UI) | TypeScript |

The frontend NEVER contains business logic. It calls the backend API only.

## Backend Layer Import Rules

| Layer | Directory | May Import From | MUST NOT Import From |
|-------|-----------|----------------|---------------------|
| **Domain** | `backend/app/domain/` | `backend/app/domain/`, `backend/app/lib/` | application, api, infrastructure, FastAPI, SQLAlchemy, Pydantic BaseModel |
| **Application** | `backend/app/application/` | `backend/app/domain/`, `backend/app/lib/` | api, infrastructure (concrete), FastAPI, SQLAlchemy |
| **API (Adapter)** | `backend/app/api/` | `backend/app/application/`, `backend/app/domain/`, `backend/app/lib/` | infrastructure |
| **Infrastructure** | `backend/app/infrastructure/` | `backend/app/application/ports/`, `backend/app/domain/`, `backend/app/lib/` | api |

## Domain Layer Constraints (CRITICAL)

The Domain layer is **pure Python**. These imports are FORBIDDEN in any file under `backend/app/domain/`:

```python
# FORBIDDEN in domain layer:
from fastapi import ...          # NO
from sqlalchemy import ...       # NO
from pydantic import BaseModel   # NO (use dataclasses instead)
import requests                  # NO
import httpx                     # NO
```

Domain entities MUST use Python `@dataclass` or plain classes, NOT Pydantic BaseModel.

## Verification Commands

Before completing any work, run:

```bash
# Check domain layer purity
grep -rn "from fastapi\|from sqlalchemy\|from pydantic" backend/app/domain/ --include="*.py"
# Expected: zero results

# Check application layer
grep -rn "from backend.app.api\|from backend.app.infrastructure" backend/app/application/ --include="*.py" | grep -v "from backend.app.application.ports"
# Expected: zero results (ports imports are OK)

# Check infrastructure doesn't import api
grep -rn "from backend.app.api" backend/app/infrastructure/ --include="*.py"
# Expected: zero results
```

## File Size Rule

No `.py`, `.ts`, or `.tsx` file may exceed **2,000 lines**. At **1,500 lines**, split proactively. The pre-commit hook `scripts/check_file_size.py` enforces this.

## If You Need Something From a Forbidden Layer

You are structuring the code wrong. Do NOT bypass — refactor instead:
- Need DB access in a use case? → Define a port (ABC) in `application/ports/`, implement in `infrastructure/`
- Need business logic in frontend? → Move it to a backend use case, expose via API
- Need framework types in domain? → Create a domain value object that maps to/from the framework type
