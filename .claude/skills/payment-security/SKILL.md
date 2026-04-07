---
name: payment-security
description: Payment security rules — provider-agnostic. Idempotency, callback verification, double-charge prevention, and PCI compliance. For Payments Agent.
disable-model-invocation: true
user-invocable: false
---

# Payment Security Rules

**Payment provider is NOT yet selected.** All code must be fully provider-agnostic. Likely candidates: Montonio, Kevin., Klix by Citadele, or other Baltic online banking gateways.

## Architecture

```
frontend → backend API → use case → PaymentGateway port (ABC) → [provider] adapter → Provider API
```

- Provider SDK is ONLY imported in `backend/app/infrastructure/payments/`
- `application/ports/payment_gateway.py` defines the abstract interface using domain types (Money, PaymentIntent, PaymentStatus)
- The frontend NEVER handles payment secrets — it receives a redirect URL or client token from the backend
- When a provider is chosen, create ONE adapter file (e.g., `montonio_adapter.py`) implementing the port

## Never Log These

```python
# FORBIDDEN to log, store, or include in error messages:
card_number           # NEVER
cvv / cvc             # NEVER
bank_account_number   # NEVER (IBAN only last 4 if needed)
raw_payment_token     # NEVER (only token IDs are OK)
provider_secret_key   # NEVER
bank_credentials      # NEVER

# OK to log:
payment_id            # safe
last_four_digits      # safe
payment_status        # "succeeded" — safe
amount_cents          # 5000 — safe
provider_name         # "montonio" — safe
```

## Callback/Webhook Verification (MANDATORY)

Every incoming callback from the payment provider MUST be verified BEFORE processing:

```python
# backend/app/infrastructure/payments/base_adapter.py
from abc import ABC, abstractmethod

class PaymentProviderAdapter(ABC):
    @abstractmethod
    def verify_callback(self, payload: bytes, signature: str) -> dict:
        """Verify callback authenticity. Raise WebhookVerificationError if invalid."""
        ...

# Each adapter implements its provider-specific verification:
# - HMAC signature check (most Baltic providers)
# - IP whitelist check (some providers)
# - Request signing verification
```

**Unverified callbacks MUST be rejected with HTTP 400.** No exceptions.

## Idempotency

All payment operations MUST be idempotent:

```python
# Generate deterministic idempotency key from operation context:
idempotency_key = f"join-{member_id}-{plan}-{date.today().isoformat()}"

# Pass to provider adapter — each adapter handles idempotency per provider's API
result = await self.payment_gateway.create_payment(
    amount=Money(cents=5000, currency="EUR"),
    idempotency_key=idempotency_key,
    description=f"LPA membership: {plan}",
    return_url=f"{settings.FRONTEND_URL}/payment/callback",
)
```

## Double-Charge Prevention

Before initiating ANY payment:

```python
async def execute(self, enrollment_id: str) -> Result:
    # CHECK for existing payment first
    existing = await self.payment_repo.find_pending_or_completed(enrollment_id)
    if existing is not None:
        if existing.status == "completed":
            return Err(PaymentError.already_paid())
        if existing.status == "pending":
            return Ok(existing)  # Return existing pending payment
    # Only create new payment if none exists
    ...
```

## Status Flow

```
Enrollment: PENDING → (payment initiated) → PENDING → (callback: success) → CONFIRMED
                                                    → (callback: failed)  → FAILED

Membership: NONE → (payment initiated) → PENDING → (callback: success) → ACTIVE
                                                  → (callback: failed)  → NONE
```

**CRITICAL:** Status changes to CONFIRMED/ACTIVE happen ONLY in the callback handler, NEVER in the initial payment request. The initial request creates a PENDING status only.

## Port Interface Pattern

```python
# backend/app/application/ports/payment_gateway.py
from abc import ABC, abstractmethod
from backend.app.domain.value_objects.money import Money

class PaymentGateway(ABC):
    @abstractmethod
    async def create_payment(
        self, amount: Money, idempotency_key: str,
        description: str, return_url: str,
    ) -> PaymentIntent: ...

    @abstractmethod
    async def verify_callback(self, payload: bytes, signature: str) -> PaymentEvent: ...

    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentStatus: ...

    @abstractmethod
    async def refund(self, payment_id: str, amount: Money | None = None) -> RefundResult: ...
```

Domain types only in the port. Provider-specific types stay inside the adapter.

## Error Handling

| Scenario | Action |
|----------|--------|
| Provider timeout | Return `Err(PaymentError.provider_timeout())`. Log WARNING. Do NOT retry automatically. |
| Payment declined | Return `Err(PaymentError.declined(reason))`. Show user-safe message. |
| Provider 500 | Return `Err(PaymentError.provider_error())`. Log ERROR. Alert admin. |
| Callback delivery failure | Log ERROR. Provider will retry. Ensure handler is idempotent. |
| Unknown error | Let it propagate. Do NOT catch with bare except. |

## Testing Requirements

- Mock the provider API in all tests — never hit real payment APIs
- Test both success and failure paths for every payment operation
- Test callback verification (valid signature, invalid signature, missing signature)
- Test idempotency: same operation twice → same result, single charge
- Test race condition: concurrent requests → no double charge
- Test refund flow: full and partial refunds update status correctly
