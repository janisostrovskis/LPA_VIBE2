---
name: ci-pipeline
description: CI/CD pipeline stages, pre-commit hook specifications, Docker Compose configuration, and enforcement script contracts. For DevOps Agent.
disable-model-invocation: true
user-invocable: false
---

# CI/CD Pipeline & Infrastructure

## Docker Compose Services (Development)

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: lpa_dev
      POSTGRES_USER: lpa
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # From env, never hardcoded
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - db
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    command: npm run dev
    ports:
      - "3000:3000"
    env_file: .env
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  pgdata:
```

## CI Pipeline Stages (in order)

Every stage must pass. Failure at any stage blocks the pipeline.

```
1. Lint          → ruff check (Python) + eslint (TypeScript)
2. Type Check    → mypy --strict (Python) + tsc --noEmit (TypeScript)
3. COLA Check    → python scripts/check_cola_imports.py
4. File Size     → python scripts/check_file_size.py
5. Unit Tests    → pytest tests/domain/ tests/application/ + vitest run
6. Integration   → pytest tests/api/ tests/infrastructure/ (with test DB)
7. Security Scan → python scripts/security_scan.py
8. E2E Tests     → npx playwright test (on merge to main only)
```

## Pre-Commit Hook Scripts

### `scripts/check_file_size.py`

**Contract:**
- Input: List of staged files from git
- Action: Count lines in each `.py`, `.ts`, `.tsx` file
- Output: REJECT commit if any file > 2,000 lines. WARN if > 1,500 lines.
- Exemptions: `alembic/versions/`, `node_modules/`, `dist/`, `.next/`
- Exit code: 0 = pass, 1 = fail

```python
#!/usr/bin/env python3
"""Pre-commit hook: reject files exceeding 2000 lines."""
import subprocess
import sys

HARD_LIMIT = 2000
WARN_LIMIT = 1500
EXTENSIONS = {'.py', '.ts', '.tsx'}
EXEMPT_PATHS = {'alembic/versions/', 'node_modules/', 'dist/', '.next/'}

def get_staged_files():
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True, text=True
    )
    return result.stdout.strip().split('\n')

def check_file_size(filepath):
    if any(exempt in filepath for exempt in EXEMPT_PATHS):
        return None
    if not any(filepath.endswith(ext) for ext in EXTENSIONS):
        return None
    with open(filepath) as f:
        lines = sum(1 for _ in f)
    if lines > HARD_LIMIT:
        return f"BLOCKED: {filepath} has {lines} lines (limit: {HARD_LIMIT})"
    if lines > WARN_LIMIT:
        return f"WARNING: {filepath} has {lines} lines (consider splitting at {WARN_LIMIT})"
    return None

# ... main loop checking staged files
```

### `scripts/check_cola_imports.py`

**Contract:**
- Input: All `.py` files under `backend/app/`
- Action: Parse imports and verify layer boundaries
- Rules:
  - `domain/` files: no imports from `application/`, `api/`, `infrastructure/`, `fastapi`, `sqlalchemy`, `pydantic`
  - `application/` files: no imports from `api/`, `infrastructure/` (except `application/ports/`)
  - `infrastructure/` files: no imports from `api/`
- Exit code: 0 = pass, 1 = violations found

### `scripts/security_scan.py`

**Contract:**
- Input: All staged files
- Action: Regex scan for hardcoded secrets
- Patterns: API keys (`sk_live_`, `sk_test_` with 20+ chars), passwords in quotes, connection strings with credentials, AWS keys, JWT secrets
- Exemptions: `.env.example` (placeholder values only), test files with obvious test values
- Exit code: 0 = clean, 1 = potential secrets found

## Backend Configuration

### `pyproject.toml` key sections:

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "A", "SIM", "TCH"]
# E722 = bare except (MUST be enabled for fail-loudly)

[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

### ESLint key rules:

```json
{
  "rules": {
    "no-empty": ["error", { "allowEmptyCatch": false }],
    "@typescript-eslint/no-floating-promises": "error",
    "@typescript-eslint/no-explicit-any": "error"
  }
}
```

## Deployment Checklist

Before any deployment:
- [ ] All CI stages pass
- [ ] `.env` configured on target (not in repo)
- [ ] Database migrations run: `alembic upgrade head`
- [ ] Health check endpoint responds: `GET /api/health`
- [ ] CORS origin set to production frontend URL
- [ ] Payment provider callback URL registered with production endpoint
- [ ] SSL/TLS configured
- [ ] Monitoring/alerting active
- [ ] Rollback procedure documented and tested
