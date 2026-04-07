---
name: db-conventions
description: Database conventions for SQLAlchemy models, Alembic migrations, repository pattern, and domain entity mapping. For Database Agent.
disable-model-invocation: true
user-invocable: false
---

# Database Conventions

## Domain Entities vs SQLAlchemy Models

These are SEPARATE classes. Never conflate them.

| Aspect | Domain Entity | SQLAlchemy Model |
|--------|--------------|-----------------|
| Location | `backend/app/domain/entities/` | `backend/app/infrastructure/database/models.py` |
| Base class | `@dataclass` (Python stdlib) | `DeclarativeBase` (SQLAlchemy) |
| Framework imports | NONE | SQLAlchemy only |
| Purpose | Business logic, invariants | Database persistence |
| Used by | Use cases, domain rules | Repositories only |

### Mapping Pattern

Repositories handle the conversion:

```python
# In repository — convert between layers:
class MemberRepository:
    def find_by_id(self, member_id: str) -> Member | None:
        model = self.session.get(MemberModel, member_id)
        if model is None:
            return None
        return self._to_entity(model)  # SQLAlchemy → Domain

    def save(self, member: Member) -> None:
        model = self._to_model(member)  # Domain → SQLAlchemy
        self.session.merge(model)

    def _to_entity(self, model: MemberModel) -> Member:
        return Member(
            id=model.id,
            email=Email(model.email),
            name=model.name,
            preferred_language=Locale(model.preferred_language),
        )

    def _to_model(self, entity: Member) -> MemberModel:
        return MemberModel(
            id=entity.id,
            email=str(entity.email),
            name=entity.name,
            preferred_language=entity.preferred_language.value,
        )
```

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Table names | `snake_case`, plural | `members`, `training_sessions`, `cpd_records` |
| Column names | `snake_case` | `first_name`, `created_at`, `membership_status` |
| Foreign keys | `{referenced_table_singular}_id` | `member_id`, `training_id` |
| Index names | `ix_{table}_{columns}` | `ix_members_email` |
| Constraint names | `ck_{table}_{description}` | `ck_memberships_status_valid` |
| Migration files | Auto-generated with descriptive message | `add_membership_status_column` |

## Alembic Migration Rules

1. **Every migration must be reversible.** Always implement both `upgrade()` and `downgrade()`.
2. **One concern per migration.** Don't mix schema changes with data migrations.
3. **Test both directions:** Run `alembic upgrade head` then `alembic downgrade -1` then `alembic upgrade head`.
4. **Data migrations** (changing existing data) must be separate from schema migrations.
5. **Never drop columns in production** without a deprecation migration first.
6. **Add NOT NULL with a default** — never add NOT NULL to existing columns without a default value.

```bash
# Create a new migration:
cd backend && alembic revision --autogenerate -m "add_membership_type_column"

# Test both directions:
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

## Index Strategy

- Primary keys: auto-indexed
- Foreign keys: always add explicit index
- Frequently filtered columns: add index (email, status, locale, city)
- Composite filters: add composite index (e.g., `ix_trainings_city_date`)
- Full-text search: PostgreSQL GIN indexes for `tsvector` columns

## Value Objects in Domain

```python
# backend/app/domain/value_objects/email.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        if "@" not in self.value:
            raise ValueError(f"Invalid email: {self.value}")

    def __str__(self) -> str:
        return self.value
```

Value objects are immutable (`frozen=True`), validate on creation, and have no framework dependencies.

## Testing

```bash
# Run database tests:
cd backend && python -m pytest tests/domain/ tests/infrastructure/ -v

# Test with a real test database (not mocks):
# Integration tests use a test PostgreSQL instance via Docker
```
