---
name: security-checklist
description: Full B.3 security review checklist with 31 pass/fail items and automated verification commands. For Security Agent.
disable-model-invocation: true
user-invocable: false
---

# Security Audit Checklist

Run after EVERY phase and subphase. Every item is pass/fail. **A single fail blocks progression.**

## Section 1: COLA Adherence

### Check 1.1 — Domain layer purity
```bash
grep -rn "from fastapi\|from sqlalchemy\|from pydantic\|import fastapi\|import sqlalchemy" backend/app/domain/ --include="*.py"
```
**Expected:** Zero results. **If results found:** FAIL — domain has framework imports.

### Check 1.2 — Application layer isolation
```bash
grep -rn "from backend.app.api\|from backend.app.infrastructure" backend/app/application/ --include="*.py" | grep -v "from backend.app.application.ports"
```
**Expected:** Zero results (ports imports are OK). **If results found:** FAIL.

### Check 1.3 — Infrastructure uses ports
```bash
grep -rn "from backend.app.api" backend/app/infrastructure/ --include="*.py"
```
**Expected:** Zero results. **If results found:** FAIL.

### Check 1.4 — No React/Next.js in backend
```bash
grep -rn "from react\|from next\|import React" backend/ --include="*.py"
```
**Expected:** Zero results.

### Check 1.5 — No business logic in frontend
Review `frontend/src/` for any business rule implementations (membership status transitions, capacity calculations, payment processing logic). These MUST live in the backend.

## Section 2: Secrets and Credentials

### Check 2.1 — No .env in git
```bash
git log --all --diff-filter=A --name-only -- "*.env" ".env*" 2>/dev/null
```
**Expected:** Zero results (no .env files ever committed).

### Check 2.2 — No hardcoded secrets
```bash
grep -rn "sk_live\|sk_test\|password\s*=\s*['\"][^'\"]\{8,\}\|api_key\s*=\s*['\"\]\|secret_key\s*=\s*['\"]" backend/ frontend/ --include="*.py" --include="*.ts" --include="*.tsx" --include="*.js"
```
**Expected:** Zero results.

### Check 2.3 — .env.example has placeholders only
```bash
cat .env.example 2>/dev/null | grep -v "^#\|^$\|REPLACE_ME\|your_\|changeme\|xxx\|placeholder"
```
Review remaining lines — no real values should appear.

### Check 2.4 — env.py validates required vars
Read `backend/app/infrastructure/config/env.py`. Verify:
- [ ] All secret fields (DATABASE_URL, STRIPE_SECRET_KEY, JWT_SECRET) have NO default value
- [ ] Missing vars cause startup failure with clear error message

### Check 2.5 — .gitignore coverage
```bash
grep -c "\.env" .gitignore
```
Verify `.env`, `.env.*`, and `!.env.example` are all present.

### Check 2.6 — No secrets in Docker Compose
```bash
grep -n "password\|secret\|key\|token" docker-compose.yml 2>/dev/null | grep -v "env_file\|^\s*#"
```
**Expected:** No hardcoded secret values (env_file references are OK).

## Section 3: Authentication and Authorization

### Check 3.1 — Auth-required routes protected
Review all routes in `backend/app/api/routes/` under auth-required paths. Each must use `Depends(get_current_user)` or equivalent auth dependency.

### Check 3.2 — Admin routes check role
Review admin routes. Each must verify admin role after auth check.

### Check 3.3 — CORS configuration
```bash
grep -rn "CORSMiddleware\|allow_origins" backend/app/ --include="*.py"
```
Verify `allow_origins` is set to the frontend URL only, NOT `["*"]`.

### Check 3.4 — JWT storage
Review frontend auth code. JWT tokens must use httpOnly cookies, NOT localStorage.

### Check 3.5 — Webhook signature verification
```bash
grep -rn "verify_signature\|construct_event\|Webhook.construct" backend/app/ --include="*.py"
```
Every webhook endpoint must verify signatures before processing.

## Section 4: Data Protection

### Check 4.1 — Input validation
All API route handler parameters must use Pydantic models or FastAPI's `Body`/`Query`/`Path` with validation.

### Check 4.2 — No raw SQL
```bash
grep -rn "text(\|execute(\|raw_sql\|\.exec(" backend/app/ --include="*.py" | grep -v "alembic\|test"
```
Review any results — raw SQL requires explicit approval and parameterization.

### Check 4.3 — No dangerouslySetInnerHTML
```bash
grep -rn "dangerouslySetInnerHTML" frontend/src/ --include="*.tsx" --include="*.ts"
```
**Expected:** Zero results (or each instance uses DOMPurify sanitization).

### Check 4.4 — GDPR data fields
Verify personal data fields (name, email, phone, address) are:
- Identified in entity definitions
- Deletable via data deletion endpoint
- Exportable via data export endpoint

### Check 4.5 — Audit logs
```bash
grep -rn "audit\|AuditLog\|audit_service" backend/app/application/ --include="*.py"
```
Verify sensitive operations (membership changes, payment actions, certification decisions, admin overrides) create audit log entries.

### Check 4.6 — File upload validation
If file uploads exist, verify type whitelist and size limits are enforced.

## Section 5: Error Handling (Fail-Loudly)

### Check 5.1 — No bare except in Python
```bash
grep -rn "except:" backend/ --include="*.py" | grep -v "except [A-Z]"
```
**Expected:** Zero results.

### Check 5.2 — No except-pass in Python
```bash
grep -rn -A1 "except" backend/ --include="*.py" | grep "pass$"
```
**Expected:** Zero results.

### Check 5.3 — No empty catch in TypeScript
```bash
grep -rn "catch" frontend/src/ --include="*.ts" --include="*.tsx" -A1 | grep -B1 "^.*}$" | grep "catch"
```
Review for empty catch blocks.

### Check 5.4 — No print/console.log for errors
```bash
grep -rn "print(" backend/app/ --include="*.py" | grep -v "test\|__pycache__"
grep -rn "console\.log\|console\.error" frontend/src/ --include="*.ts" --include="*.tsx"
```
**Expected:** Zero in production code (tests are OK).

### Check 5.5 — Payment errors visible
Review payment use cases. Every payment failure must result in a status change visible to the user.

### Check 5.6 — FAIL-QUIET-EXCEPTION audit
```bash
grep -rn "FAIL-QUIET-EXCEPTION" backend/ frontend/ --include="*.py" --include="*.ts" --include="*.tsx"
```
Each instance must have: rationale, WARNING log, plan approval reference.

## File Size Check

```bash
find backend/ frontend/ -name "*.py" -o -name "*.ts" -o -name "*.tsx" 2>/dev/null | xargs wc -l 2>/dev/null | sort -rn | head -20
```
**Expected:** No file exceeds 2,000 lines.

## Results Template

After running all checks, fill in `planning/phase-NN/SECURITY_REVIEW.md` with pass/fail for each item and the `REVIEW RESULT: PASS/FAIL` verdict.
