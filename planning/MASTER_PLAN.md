# LPA Platform — Master Plan

**Version:** 1.0
**Tech Stack:** FastAPI (Python backend) + Next.js (TypeScript frontend) + PostgreSQL
**Architecture:** COLA (Clean Object-oriented Layered Architecture)
**Process:** Defined in `docs/DEVELOPMENT_RULEBOOK.MD`

---

## Project Structure

Two-service monorepo. The service boundary enforces COLA layer separation.

```
LPA_VIBE2/
├── CLAUDE.md                             # Agent rules and architecture constraints
├── docs/
│   ├── LPA_BUSINESS_CASE.MD             # Functional requirements and acceptance criteria
│   ├── LPA_DESIGN_LANGUAGE.MD           # Visual design system specification
│   └── DEVELOPMENT_RULEBOOK.MD          # Development process rules
├── planning/
│   ├── MASTER_PLAN.md                   # This file
│   └── phase-NN-name/                   # Sub-plan per phase
│
├── backend/                              # FastAPI — Python 3.12+
│   ├── pyproject.toml                   # Dependencies, ruff, mypy config
│   ├── alembic.ini
│   ├── alembic/                         # Database migrations
│   ├── app/
│   │   ├── main.py                      # FastAPI app entry point
│   │   ├── api/                         # === ADAPTER LAYER ===
│   │   │   ├── routes/
│   │   │   │   ├── auth.py             # Login, register, magic link
│   │   │   │   ├── members.py          # Member CRUD, profile
│   │   │   │   ├── memberships.py      # Join, renew, cancel
│   │   │   │   ├── trainings.py        # Catalog, registration
│   │   │   │   ├── certifications.py   # Applications, verification
│   │   │   │   ├── directory.py        # Search, profiles
│   │   │   │   ├── content.py          # News, resources, events
│   │   │   │   ├── admin.py            # Admin-only endpoints
│   │   │   │   └── webhooks.py         # Payment provider callbacks
│   │   │   ├── middleware/
│   │   │   │   ├── auth.py             # JWT validation
│   │   │   │   ├── cors.py             # CORS configuration
│   │   │   │   └── rate_limit.py       # Rate limiting
│   │   │   └── dependencies.py         # Dependency injection wiring
│   │   │
│   │   ├── application/                 # === APPLICATION LAYER ===
│   │   │   ├── use_cases/
│   │   │   │   ├── membership/
│   │   │   │   │   ├── join_membership.py
│   │   │   │   │   ├── renew_membership.py
│   │   │   │   │   ├── cancel_membership.py
│   │   │   │   │   └── check_status.py
│   │   │   │   ├── training/
│   │   │   │   │   ├── register_for_training.py
│   │   │   │   │   ├── cancel_registration.py
│   │   │   │   │   ├── promote_from_waitlist.py
│   │   │   │   │   └── manage_training.py
│   │   │   │   ├── certification/
│   │   │   │   │   ├── submit_application.py
│   │   │   │   │   ├── review_application.py
│   │   │   │   │   ├── verify_credential.py
│   │   │   │   │   └── record_cpd.py
│   │   │   │   ├── directory/
│   │   │   │   │   ├── apply_for_verification.py
│   │   │   │   │   └── search_directory.py
│   │   │   │   └── content/
│   │   │   │       ├── publish_article.py
│   │   │   │       └── manage_resource.py
│   │   │   ├── services/
│   │   │   │   ├── notification_service.py
│   │   │   │   └── audit_service.py
│   │   │   ├── ports/                   # Interfaces (Python ABCs)
│   │   │   │   ├── payment_gateway.py
│   │   │   │   ├── email_sender.py
│   │   │   │   ├── file_storage.py
│   │   │   │   └── search_engine.py
│   │   │   └── dto/                     # Data transfer objects (Pydantic)
│   │   │       ├── membership_dto.py
│   │   │       ├── training_dto.py
│   │   │       ├── certification_dto.py
│   │   │       └── directory_dto.py
│   │   │
│   │   ├── domain/                      # === DOMAIN LAYER (pure Python) ===
│   │   │   ├── entities/
│   │   │   │   ├── member.py
│   │   │   │   ├── organization.py
│   │   │   │   ├── membership.py
│   │   │   │   ├── training.py
│   │   │   │   ├── session.py
│   │   │   │   ├── enrollment.py
│   │   │   │   ├── certificate.py
│   │   │   │   ├── cpd_record.py
│   │   │   │   ├── instructor_profile.py
│   │   │   │   ├── studio_profile.py
│   │   │   │   ├── news_article.py
│   │   │   │   └── resource.py
│   │   │   ├── value_objects/
│   │   │   │   ├── email.py
│   │   │   │   ├── money.py
│   │   │   │   ├── membership_status.py  # Active | Grace | Lapsed
│   │   │   │   ├── certificate_id.py
│   │   │   │   ├── locale.py             # LV | EN | RU
│   │   │   │   ├── date_range.py
│   │   │   │   └── capacity.py
│   │   │   ├── errors/
│   │   │   │   ├── membership_error.py
│   │   │   │   ├── capacity_exceeded_error.py
│   │   │   │   ├── payment_required_error.py
│   │   │   │   └── validation_error.py
│   │   │   ├── events/
│   │   │   │   ├── membership_activated.py
│   │   │   │   ├── seat_reserved.py
│   │   │   │   ├── certificate_issued.py
│   │   │   │   └── verification_approved.py
│   │   │   └── rules/
│   │   │       ├── membership_status_rules.py
│   │   │       ├── seat_availability_rules.py
│   │   │       └── cpd_requirements_rules.py
│   │   │
│   │   ├── infrastructure/              # === INFRASTRUCTURE LAYER ===
│   │   │   ├── database/
│   │   │   │   ├── models.py            # SQLAlchemy table models
│   │   │   │   ├── session.py           # Database session factory
│   │   │   │   └── repositories/
│   │   │   │       ├── member_repository.py
│   │   │   │       ├── membership_repository.py
│   │   │   │       ├── training_repository.py
│   │   │   │       ├── certification_repository.py
│   │   │   │       ├── directory_repository.py
│   │   │   │       └── content_repository.py
│   │   │   ├── payments/
│   │   │   │   └── provider_adapter.py   # Implements PaymentGateway port (provider TBD)
│   │   │   │   └── payment_factory.py   # Provider selection
│   │   │   ├── email/
│   │   │   │   ├── resend_adapter.py    # Implements EmailSender port
│   │   │   │   └── templates/
│   │   │   │       ├── welcome.py
│   │   │   │       ├── renewal_reminder.py
│   │   │   │       ├── payment_receipt.py
│   │   │   │       └── ...
│   │   │   ├── storage/
│   │   │   │   └── s3_adapter.py        # Implements FileStorage port
│   │   │   └── config/
│   │   │       ├── env.py               # Pydantic Settings — fail loudly on missing vars
│   │   │       └── constants.py         # Non-secret app constants
│   │   │
│   │   └── lib/                         # Shared utilities
│   │       ├── result.py                # Result[T, E] type
│   │       ├── errors.py                # Base error classes
│   │       └── logger.py               # Structured logging
│   │
│   └── tests/                           # Mirrors app/ structure
│       ├── conftest.py                  # Shared fixtures, test DB setup
│       ├── domain/
│       ├── application/
│       ├── api/
│       ├── infrastructure/
│       └── e2e/
│
├── frontend/                             # Next.js — TypeScript strict
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts               # LPA design tokens mapped
│   ├── next.config.ts
│   ├── playwright.config.ts
│   ├── vitest.config.ts
│   ├── public/
│   │   ├── fonts/                       # Songer, Montserrat, Winterlady
│   │   ├── images/
│   │   └── locales/
│   │       ├── lv/                      # Primary language
│   │       ├── en/
│   │       └── ru/
│   └── src/
│       ├── app/
│       │   └── [locale]/                # i18n URL prefix routing
│       │       ├── layout.tsx
│       │       ├── page.tsx             # Home
│       │       ├── (public)/            # No auth required
│       │       │   ├── about/
│       │       │   ├── join/
│       │       │   ├── trainings/
│       │       │   ├── directory/
│       │       │   ├── news/
│       │       │   ├── resources/
│       │       │   ├── verify/          # Public credential verification
│       │       │   └── contact/
│       │       ├── (auth)/              # Login required
│       │       │   ├── profile/
│       │       │   ├── my-trainings/
│       │       │   ├── my-certificates/
│       │       │   └── my-payments/
│       │       └── (admin)/             # Admin role required
│       │           └── admin/
│       │               ├── layout.tsx
│       │               ├── dashboard/
│       │               ├── members/
│       │               ├── trainings/
│       │               ├── certifications/
│       │               ├── content/
│       │               └── settings/
│       ├── components/
│       │   ├── ui/                      # Design system primitives
│       │   │   ├── Button.tsx
│       │   │   ├── Card.tsx
│       │   │   ├── Input.tsx
│       │   │   ├── Modal.tsx
│       │   │   ├── Badge.tsx
│       │   │   └── Toast.tsx
│       │   ├── membership/
│       │   ├── training/
│       │   ├── directory/
│       │   ├── certification/
│       │   ├── content/
│       │   └── layout/
│       │       ├── Header.tsx
│       │       ├── Footer.tsx
│       │       ├── MobileNav.tsx
│       │       └── LanguageSwitcher.tsx
│       ├── hooks/
│       ├── lib/
│       │   ├── api-client.ts            # Typed fetch wrapper for backend API
│       │   └── i18n.ts                  # i18n configuration
│       └── __tests__/
│
├── docker-compose.yml                    # Backend + PostgreSQL + Frontend (dev)
├── .env.example                          # Template with placeholder values only
├── .gitignore
└── scripts/
    ├── check_file_size.py               # Pre-commit: reject >2000 lines
    ├── check_cola_imports.py            # Pre-commit: reject wrong-layer imports
    └── security_scan.py                 # Pre-commit: detect hardcoded secrets
```

---

## Phase Roadmap

### Phase 0: Project Foundation

**Objective:** Bootable project with all tooling, CI, and COLA enforcement in place. Zero features — only guardrails.

**Deliverables:**
1. Git repository initialized with comprehensive `.gitignore`
2. `docker-compose.yml` with FastAPI + PostgreSQL + Next.js services
3. Backend: `pyproject.toml` with FastAPI, SQLAlchemy, Alembic, Pydantic, ruff, mypy, pytest
4. Frontend: `package.json` with Next.js, TypeScript, Tailwind, ESLint, Vitest, Playwright
5. Full folder structure created (empty `__init__.py` and index files)
6. `scripts/check_file_size.py` — pre-commit hook, rejects files >2000 lines
7. `scripts/check_cola_imports.py` — pre-commit hook, rejects wrong-layer imports
8. `scripts/security_scan.py` — pre-commit hook, detects hardcoded secrets
9. `backend/app/lib/result.py` — `Result[T, E]` type
10. `backend/app/lib/errors.py` — base error classes
11. `backend/app/lib/logger.py` — structured logging setup
12. `backend/app/infrastructure/config/env.py` — Pydantic Settings with fail-loudly validation
13. ESLint config: `no-empty` catch, `no-floating-promises`, import restrictions
14. Ruff + mypy config: strict typing, bare-except ban
15. CI pipeline: lint, type-check, test, file-size check, COLA import check

**Testing gate:** Both services start via Docker Compose. Pre-commit hooks reject a deliberately oversized file AND a deliberately wrong-layer import. CI pipeline passes on a clean commit.

**Acceptance criteria ref:** N/A (infrastructure phase)

---

### Phase 1: Design System & Layout Shell

**Objective:** All LPA design tokens implemented in code. Layout skeleton with navigation, footer, language switching. No backend data — static content only.

**Deliverables:**
1. `frontend/tailwind.config.ts` with all `--lpa-*` tokens mapped
2. Font loading: Songer, Montserrat, Winterlady
3. UI primitives in `frontend/src/components/ui/`: Button, Card, Input, Modal, Badge, Toast
4. Layout components: Header, Footer, MobileNav, LanguageSwitcher
5. `frontend/src/app/[locale]/layout.tsx` with i18n routing (next-intl)
6. Static placeholder pages for all public routes
7. WCAG AA compliance verified on all interactive primitives

**Testing gate:** Design tokens match `docs/LPA_DESIGN_LANGUAGE.MD` exactly. Keyboard navigation works on all interactive elements. Language switcher changes URL prefix. All primitives pass contrast checks. Mobile nav works at 375px.

**Acceptance criteria ref:** Business case sections 3.9, 3.14, 3.17

---

### Phase 2: Accounts & Authentication

**Objective:** Users and organizations can register, log in, manage profiles. Role system enforced. Admin route protection in place.

**Sub-phases:**
1. Database schema — User, Organization, Role SQLAlchemy models + Alembic migration
2. Domain entities — Member, Organization, Email value object, Locale value object
3. Auth infrastructure — JWT issuance, magic link flow, session management
4. Use cases — register, login, update profile, manage org team, invite member
5. API routes — auth endpoints, member CRUD, organization CRUD
6. UI pages — registration form, login (email + magic link), profile editor, org dashboard
7. Middleware — JWT validation dependency, role-check dependency

**Testing gate:** Full registration flow (individual + organization). Login via password and magic link. Role-based access enforced (unauthorized = 403). Profile data persists across sessions. GDPR data export endpoint returns user data as JSON. Admin can access admin shell.

**Acceptance criteria ref:** Business case section 3.1

---

### Phase 3: Memberships & Payments

**Objective:** Full membership lifecycle with automated status management, payment processing, and admin oversight.

**Sub-phases:**
1. Database schema — Membership, Payment, Invoice, MembershipType models
2. Domain — MembershipStatus value object with transition rules, Money value object
3. Payment port + provider adapter — `payment_gateway.py` ABC + provider adapter (provider TBD — likely Montonio, Kevin., or Klix)
4. Use cases — join, renew, cancel, check-status, process-webhook
5. Automated status transitions — scheduled task: Active → Grace → Lapsed
6. Email notifications — welcome, renewal reminders (30/7/1 days), expiry, receipt
7. API routes — membership endpoints + webhook handler
8. UI — Join page, membership dashboard, payment history, invoice download
9. Admin views — member list, status override (with mandatory reason note), payment dashboard

**Testing gate:** End-to-end payment with provider test/sandbox credentials. Callback processes correctly (verified signature). Status transitions fire on schedule. Reminder emails send at correct intervals. Admin override creates audit log entry. Refund updates status and sends notification.

**Acceptance criteria ref:** Business case section 3.2

---

### Phase 4: Trainings & Registration

**Objective:** Training catalog with capacity-controlled registration, payment-gated seat confirmation, and waitlist management.

**Sub-phases:**
1. Database schema — Training, Session, Enrollment, Waitlist models
2. Domain — Training entity, Capacity value object, seat availability rules
3. Use cases — create training, register, pay, confirm seat, cancel, waitlist promote
4. API routes — training CRUD, enrollment endpoints
5. UI — catalog with filters (level, city, date, price), detail page, registration flow, waitlist, my-trainings
6. Admin views — manage trainings, view enrollments, export attendee CSV, mark attendance
7. Email notifications — confirmation, change notice, waitlist promotion, start reminder

**Testing gate:** Cannot oversell seats (capacity enforced). Waitlist promotes correctly when seat opens. Registration without payment stays PENDING. Catalog filters work across LV/EN/RU. Admin can export valid CSV. Cancellation policy text displays.

**Acceptance criteria ref:** Business case section 3.3

---

### Phase 5: Certification & CPD

**Objective:** Credential lifecycle from application through review to issuance. Public verification. CPD tracking.

**Sub-phases:**
1. Database schema — Certificate, CPDRecord, CertificationLevel, Application models
2. Domain — Certificate entity, CertificateId value object, CPD requirements rules
3. Use cases — submit application, review, issue certificate, verify credential, record CPD, check CPD totals
4. API routes — certification endpoints, public verify endpoint
5. UI — certification info page, application form, CPD dashboard, public verify page
6. Admin/reviewer views — application queue, review form with comments, certificate management
7. Email notifications — application received, decision, expiry reminder

**Testing gate:** Application workflow from submit to decision. CertificateId verification returns correct status on public page. CPD totals calculate correctly. Expired certificates show as expired. Reviewer can approve/decline with comments visible to applicant.

**Acceptance criteria ref:** Business case section 3.4

---

### Phase 6: Directory & LPA Verified

**Objective:** Public instructor and studio directory with search, filtering, verification badge workflow.

**Sub-phases:**
1. Database schema — InstructorProfile, StudioProfile, VerificationApplication models
2. Domain — profile entities, verification status rules, expiry/renewal logic
3. Use cases — apply for verification, review, search directory, report profile
4. API routes — directory search, profile CRUD, verification workflow, report submission
5. UI — directory listing with filters (city, specialization, equipment, verified status), profile pages, verification application form, report form
6. Admin views — verification queue, profile management
7. Search — PostgreSQL full-text search across LV/EN/RU with typo tolerance

**Testing gate:** Search returns relevant results with filters. LPA Verified badge displays for verified profiles only. Verification workflow: apply → review → approve/decline. Expiry reminders fire. "Report an issue" form reaches admin. Search handles basic typos.

**Acceptance criteria ref:** Business case section 3.5

---

### Phase 7: Content Management

**Objective:** Blog/news system and resource library with multilingual content, scheduling, and access control.

**Sub-phases:**
1. Database schema — NewsArticle, Resource, Category, StaticPage models
2. Domain and use cases — publish, schedule, categorize, access-control
3. Admin content editor — create, edit, preview, schedule, publish in LV/EN/RU
4. Public pages — news listing with pagination, article pages with related content, resource library with filters
5. Members-only access control on resources — enforce login for restricted items
6. SEO — Open Graph meta tags, structured data, sitemap generation

**Testing gate:** Editor can publish articles in three languages. Scheduled posts publish on time. Members-only resources enforce login (redirects to login page). SEO metadata renders correctly. Related content suggestions display. Pagination works.

**Acceptance criteria ref:** Business case sections 3.7, 3.8

---

### Phase 8: Admin Console & Analytics

**Objective:** Complete admin dashboard with reporting, activity audit logs, data exports.

**Sub-phases:**
1. Dashboard — key metrics (membership count by type, training revenue, upcoming expiries, failed payments)
2. Audit log viewer — filterable by action type, user, date range
3. CSV export — all major entities (members, enrollments, payments, certifications)
4. Periodic reports — monthly/quarterly summaries exportable for board meetings
5. Analytics integration — privacy-respecting, GDPR-compliant (e.g., Plausible or similar)
6. **VAT threshold tracker** — year-to-date gross sales widget on the admin dashboard. Tracks cumulative revenue across memberships + trainings + any other paid items per calendar year. Shows a large progress bar against the **EUR 50,000** Latvian VAT-registration threshold. State machine: Green (< EUR 35k, 70%) → Yellow (EUR 35k–45k, 70%–90%) → Orange (EUR 45k–50k, 90%–100%) → Red (≥ EUR 50k, threshold crossed — mandatory VAT registration triggered by law). Yellow and above trigger an admin notification email weekly; Red triggers immediate daily reminders until acknowledged. Widget links to a help page explaining the VAT registration process and the consequences of crossing. Historical years archived and viewable in a sub-tab. Driven by a single SQL aggregation over `Invoice.total_cents` filtered by `issued_at BETWEEN {year_start} AND {year_end}` and `status IN (paid)` — no new schema, lives entirely in the application layer as a read-only use case.

**Testing gate:** Dashboard shows accurate counts matching database. Audit logs capture all sensitive operations from phases 2-7. CSV exports produce valid files. Reports cover all success metrics from business case section 6. Role-based access enforced — only admins see the console. VAT tracker widget shows correct YTD total matching a manual SQL sum over invoices; state transitions fire at the documented thresholds; notification emails deliver at the right tier.

**Acceptance criteria ref:** Business case sections 3.12, 3.13

---

### Phase 9: Notifications & GDPR

**Objective:** Complete email template set, notification preferences, full GDPR compliance.

**Sub-phases:**
1. Email templates — all templates from business case Appendix A in LV/EN/RU
2. Notification preferences — per-user opt-in/opt-out by category
3. GDPR data export — user can download all their data as JSON
4. GDPR data deletion — user can request account deletion, personal data is purged
5. Consent tracking — record what user consented to and when
6. Cookie consent banner — compliant with EU requirements

**Testing gate:** Every email template renders correctly in LV/EN/RU. Opt-out stops emails in that category. Data export includes all user data. Deletion removes all personal data (verify with database query). Consent records are queryable by admin.

**Acceptance criteria ref:** Business case sections 3.11, 3.15

---

### Phase 10: Performance, Polish & Launch

**Objective:** Production-ready quality. Performance optimized. All edge cases handled. Launch preparation complete.

**Sub-phases:**
1. Performance audit — Core Web Vitals, load testing under expected concurrent users
2. Accessibility audit — full WCAG 2.2 AA pass across all pages
3. Cross-browser testing — Chrome, Firefox, Safari, Edge; iOS Safari, Android Chrome
4. Error handling review — every error path tested, no unhandled states
5. Content population — migration of existing materials, content inventory tracker
6. Launch checklist — DNS, SSL, monitoring, backups, rollback plan, health checks
7. Admin documentation — how-to guides for common tasks

**Testing gate:** Core Web Vitals pass (LCP <2.5s, FID <100ms, CLS <0.1). Lighthouse accessibility score 95+. All E2E tests green across 3 languages. Load test confirms performance under expected traffic. Rollback procedure tested and documented.

**Acceptance criteria ref:** Business case sections 3.14, 3.16, 3.18, 3.19, 3.20

---

## Phase Dependencies

```
Phase 0 (Foundation)
  └── Phase 1 (Design System)
       └── Phase 2 (Accounts & Auth)
            ├── Phase 3 (Memberships & Payments)
            │    ├── Phase 4 (Trainings & Registration)
            │    └── Phase 9 (Notifications & GDPR) — partial, emails
            ├── Phase 5 (Certification & CPD)
            ├── Phase 6 (Directory & LPA Verified)
            └── Phase 7 (Content Management)
                 └── Phase 8 (Admin & Analytics)
                      └── Phase 9 (Notifications & GDPR) — full
                           └── Phase 10 (Performance & Launch)
```

**Note:** Phases 3-7 depend on Phase 2 but are somewhat parallelizable across different agent teams if coordination is managed through handoff protocol. However, sequential execution is recommended for a single-team workflow to maintain quality gates.