---
name: fail-loudly
description: Fail-loudly error handling rules and patterns. Preloaded into every agent to prevent silent error swallowing.
disable-model-invocation: true
user-invocable: false
---

# Fail-Loudly Principle

**Default rule:** Every error MUST surface to the nearest responsible party. Silent failure is a bug.

## Python Rules

### FORBIDDEN Patterns

```python
# NEVER do this:
except:                          # bare except
    pass

except Exception:                # catch-all with pass
    pass

except Exception as e:           # catch-all that only logs
    logger.info(e)               # INFO is not enough for errors

try:
    do_something()
except:                          # bare except
    return None                  # silent fallback — BUG
```

### REQUIRED Patterns

```python
# Use Result type for expected business failures:
from backend.app.lib.result import Ok, Err, Result

def join_membership(member_id: str, plan: str) -> Result[Membership, MembershipError]:
    member = repo.find(member_id)
    if member is None:
        return Err(MembershipError.member_not_found(member_id))
    if member.has_active_membership():
        return Err(MembershipError.already_active())
    membership = Membership.create(member, plan)
    return Ok(membership)

# For unexpected errors — let them propagate:
def process_webhook(payload: dict) -> Result[Payment, PaymentError]:
    # If signature verification throws, LET IT PROPAGATE
    # Only catch expected business errors
    verified = verify_signature(payload)  # may raise — that's correct
    ...

# Typed exception handling:
try:
    result = external_api.call()
except httpx.TimeoutError:
    logger.warning("External API timeout", extra={"service": "payment_provider"})
    return Err(PaymentError.provider_timeout())
except httpx.HTTPStatusError as e:
    logger.error("External API error", extra={"status": e.response.status_code})
    return Err(PaymentError.provider_error(e.response.status_code))
# No bare except — unknown errors propagate up
```

## TypeScript Rules

### FORBIDDEN Patterns

```typescript
// NEVER do this:
try { doSomething() } catch (e) {}           // empty catch
try { doSomething() } catch (e) { /* */ }    // empty catch with comment
fetchData()                                   // floating promise (no await)
fetchData().catch(() => {})                   // swallowed error
```

### REQUIRED Patterns

```typescript
// Always handle or propagate:
try {
  const data = await apiClient.get('/members');
  return data;
} catch (error) {
  if (error instanceof ApiError) {
    toast.error(error.message);  // Show to user
  }
  throw error;  // Re-throw unknown errors
}

// Always await promises:
await fetchData();

// Use error boundaries for React:
// Wrap pages in ErrorBoundary components
```

## Environment Validation

`backend/app/infrastructure/config/env.py` MUST:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str                    # Required — no default
    STRIPE_SECRET_KEY: str               # Required — no default
    STRIPE_WEBHOOK_SECRET: str           # Required — no default
    JWT_SECRET: str                      # Required — no default
    # If ANY of these are missing, app refuses to start with clear error
```

**No fallback defaults for critical config.** Missing = crash at startup.

## Payment-Specific Rules

- Every payment call MUST await confirmation
- Failed payment → enrollment stays `PENDING`, membership NOT activated
- Never fire-and-forget payment operations
- Double-charge prevention: check for existing pending payments before initiating

## Exception Process (FAIL-QUIET-EXCEPTION)

If you believe a case genuinely warrants a silent fallback:

1. Add comment: `# FAIL-QUIET-EXCEPTION: [rationale]`
2. Log at `WARNING` level minimum
3. Document in the phase plan with approval
4. Security agent reviews during phase review

Example:
```python
try:
    analytics.track("page_view", page=path)
except Exception as e:
    # FAIL-QUIET-EXCEPTION: Analytics failure must not block user navigation.
    # Approved in phase-01 plan. Re-evaluate at phase-04.
    logger.warning("Analytics tracking failed", extra={"error": str(e), "page": path})
```
