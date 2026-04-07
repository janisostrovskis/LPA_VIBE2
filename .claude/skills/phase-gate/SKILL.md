---
name: phase-gate
description: Phase completion workflow — /simplify then security review then testing gate. Preloaded into every agent to enforce the mandatory sequence.
disable-model-invocation: true
user-invocable: false
---

# Phase Gate Workflow

After completing work on any phase or subphase, you MUST execute this sequence. **No step may be skipped. No shortcuts.**

## The Sequence

```
Step 1: /simplify  →  Step 2: Security Review  →  Step 3: Testing Gate  →  Proceed
```

If Step 3 fails, go back to Step 1 (not Step 2).

## Step 1: /simplify

Run `/simplify` on all files changed in the phase.

1. Review the output — look for: code duplication, unnecessary complexity, reuse opportunities, dead code
2. Fix ALL identified issues
3. Re-run `/simplify` until output is clean (zero findings)
4. Verify no file exceeds 2,000 lines

**Do not skip this step.** Even if you believe the code is clean.

## Step 2: Security Review

Complete every item in the security checklist. Document results.

1. Run the automated checks from `security-checklist` skill (if Security Agent) or request Security Agent review via handoff
2. Document results in `planning/phase-NN/SECURITY_REVIEW.md`
3. Fix all failures
4. Re-run until all items pass

Template for `SECURITY_REVIEW.md`:

```markdown
# Security Review: Phase [NN] — [Phase Name]

## Date: YYYY-MM-DD
## Reviewer: Security Agent

## COLA Adherence
- [ ] No forbidden imports in domain layer
- [ ] No forbidden imports in application layer
- [ ] Infrastructure uses ports only
- [ ] No business logic in frontend

## Secrets and Credentials
- [ ] No .env in git history
- [ ] No hardcoded secrets in source
- [ ] env.py validates all required vars

## Authentication and Authorization
- [ ] Auth routes protected
- [ ] Admin routes check role
- [ ] CORS configured correctly

## Data Protection
- [ ] Input validated before use cases
- [ ] No raw SQL
- [ ] Audit logs for sensitive ops

## Error Handling
- [ ] No bare except / empty catch
- [ ] No swallowed promises
- [ ] Payment errors surface visibly

## REVIEW RESULT: [ PASS / FAIL ]
```

## Step 3: Testing Gate

Complete the testing gate document with pass/fail for each criterion.

1. Fill in `planning/phase-NN/TESTING_GATE.md`
2. ALL sections must be PASS
3. If any section is FAIL → loop back to Step 1

Template for `TESTING_GATE.md`:

```markdown
# Testing Gate: Phase [NN] — [Phase Name]

## Date: YYYY-MM-DD
## Responsible agent: [name]

## Unit Tests
- [ ] All domain tests pass
- [ ] All use case tests pass
- [ ] Coverage: ___% (min 80% domain, 70% application)

## Integration Tests
- [ ] Repository tests pass against test DB
- [ ] API route tests pass
- [ ] Adapter tests pass (mocked externals)

## E2E Tests (if applicable)
- [ ] Playwright tests pass
- [ ] Tested in LV, EN, RU
- [ ] Mobile + desktop viewports

## Manual Verification
- [ ] Feature works per plan
- [ ] Errors display correctly
- [ ] Accessibility OK (keyboard, screen reader)

## /simplify Review
- [ ] Zero findings remaining
- [ ] No files over 2,000 lines

## Security Review
- [ ] All B.3 items passed
- [ ] Documented in SECURITY_REVIEW.md

## GATE RESULT: [ PASS / FAIL ]
```

## Handoff for Security Review

If you are NOT the Security Agent, request the review:

```
HANDOFF: [Your Agent] → Security Agent: Complete security review for Phase [NN].
All implementation work is done. Changed files: [list key files].
Please run the full B.3 checklist and document in planning/phase-NN/SECURITY_REVIEW.md.
```

## Critical Rule

**Phase N+1 CANNOT begin until Phase N's gate is marked PASS.** No exceptions. If you are asked to start work on the next phase and the current gate is not PASS, refuse and explain what's blocking.
