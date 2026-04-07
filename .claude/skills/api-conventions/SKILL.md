---
name: api-conventions
description: FastAPI route patterns, use case orchestration, DTO design, Result-to-HTTP mapping, and dependency injection. For Backend Agent.
disable-model-invocation: true
user-invocable: false
---

# API & Application Layer Conventions

## Route → Use Case → Result → HTTP Response

Every API endpoint follows this pattern:

```python
# backend/app/api/routes/memberships.py
from fastapi import APIRouter, Depends, HTTPException
from backend.app.application.use_cases.membership.join_membership import JoinMembershipUseCase
from backend.app.application.dto.membership_dto import JoinRequest, MembershipResponse
from backend.app.api.dependencies import get_join_membership_use_case, get_current_user
from backend.app.lib.result import Ok, Err

router = APIRouter(prefix="/memberships", tags=["memberships"])

@router.post("/join", response_model=MembershipResponse, status_code=201)
async def join_membership(
    request: JoinRequest,                              # Pydantic DTO validates input
    use_case: JoinMembershipUseCase = Depends(get_join_membership_use_case),
    current_user = Depends(get_current_user),          # Auth middleware
):
    result = await use_case.execute(                    # Call use case
        member_id=current_user.id,
        plan=request.plan,
    )
    match result:                                       # Map Result to HTTP
        case Ok(membership):
            return MembershipResponse.from_entity(membership)
        case Err(error):
            raise HTTPException(
                status_code=error.http_status,
                detail=error.message,
            )
```

**Rules:**
- Routes contain ZERO business logic — they validate input, call a use case, and format output
- Routes use Pydantic DTOs for request/response, never domain entities directly
- Routes map `Result` errors to HTTP status codes
- Routes never import from `infrastructure/`

## Use Case Pattern

```python
# backend/app/application/use_cases/membership/join_membership.py
from dataclasses import dataclass
from backend.app.domain.entities.member import Member
from backend.app.domain.entities.membership import Membership
from backend.app.domain.errors.membership_error import MembershipError
from backend.app.domain.rules.membership_status_rules import can_join
from backend.app.application.ports.payment_gateway import PaymentGateway
from backend.app.lib.result import Ok, Err, Result

@dataclass
class JoinMembershipUseCase:
    member_repo: MemberRepository        # Injected via port
    membership_repo: MembershipRepository
    payment_gateway: PaymentGateway      # Port — not concrete provider

    async def execute(self, member_id: str, plan: str) -> Result[Membership, MembershipError]:
        # 1. Load data
        member = await self.member_repo.find_by_id(member_id)
        if member is None:
            return Err(MembershipError.member_not_found(member_id))

        # 2. Check business rules (domain layer)
        if not can_join(member):
            return Err(MembershipError.already_active())

        # 3. Execute business operation
        membership = Membership.create(member, plan)

        # 4. Persist
        await self.membership_repo.save(membership)

        return Ok(membership)
```

**Rules:**
- One use case per file, one public method (`execute`)
- Dependencies injected as constructor args (ports, not concrete classes)
- Returns `Result[T, DomainError]` for expected failures
- Unexpected failures (DB down, network error) propagate as exceptions
- Uses domain rules from `domain/rules/` for business invariant checks

## DTO Pattern

```python
# backend/app/application/dto/membership_dto.py
from pydantic import BaseModel, Field
from datetime import date

class JoinRequest(BaseModel):
    plan: str = Field(..., pattern="^(individual|studio|supporter)$")

class MembershipResponse(BaseModel):
    id: str
    plan: str
    status: str
    start_date: date
    end_date: date

    @classmethod
    def from_entity(cls, entity: Membership) -> "MembershipResponse":
        return cls(
            id=entity.id,
            plan=entity.plan,
            status=entity.status.value,
            start_date=entity.start_date,
            end_date=entity.end_date,
        )
```

**Rules:**
- DTOs are Pydantic models (NOT domain entities)
- Request DTOs validate input (Field constraints, patterns, etc.)
- Response DTOs have `from_entity()` class method for domain → DTO mapping
- DTOs live in `application/dto/`, not in `domain/`

## Dependency Injection

```python
# backend/app/api/dependencies.py
from functools import lru_cache
from backend.app.application.use_cases.membership.join_membership import JoinMembershipUseCase
from backend.app.infrastructure.database.repositories.member_repository import MemberRepository
from backend.app.infrastructure.database.session import get_session

def get_join_membership_use_case(
    session = Depends(get_session),
) -> JoinMembershipUseCase:
    return JoinMembershipUseCase(
        member_repo=MemberRepository(session),
        membership_repo=MembershipRepository(session),
        payment_gateway=get_payment_gateway(),
    )
```

This is the ONLY place where infrastructure concrete classes are wired to application ports.

## Error HTTP Status Mapping

| Domain Error | HTTP Status | When |
|-------------|-------------|------|
| `NotFoundError` | 404 | Entity not found |
| `ValidationError` | 422 | Business rule violation |
| `UnauthorizedError` | 401 | Not authenticated |
| `ForbiddenError` | 403 | Not authorized for this action |
| `ConflictError` | 409 | Duplicate, already exists |
| `PaymentRequiredError` | 402 | Payment needed |
| `CapacityExceededError` | 409 | No seats available |

## Testing

```bash
# Run application + API tests:
cd backend && python -m pytest tests/application/ tests/api/ -v
```
