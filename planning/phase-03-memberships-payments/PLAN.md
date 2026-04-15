# Phase 03 — Memberships & Payments

## Context

Phase 02 (Accounts & Auth) is complete with all gates passed. Phase 03 adds the first paid capability to LPA: annual memberships with automatic lifecycle management, integrated payment processing, admin-editable membership types, Latvia-compliant invoicing, and the scheduler infrastructure that later phases (trainings, certification expiry) will reuse.

Per `planning/MASTER_PLAN.md` Phase 3 definition, and the decisions locked in `DECISIONS.md` (D1–D8 + O1–O5):

- **D1** — Payment provider: **EveryPay Baltics** (default/only implemented). Montonio designated secondary for future.
- **D2** — Auto-renewal: customer chooses at checkout between **one-off** (bank link, manual annual renewal) and **recurring** (EveryPay card-on-file MIT charges).
- **D3** — LPA owns the membership lifecycle in pure domain code. EveryPay is a charge engine only, no `/subscriptions` or `/plans` API calls.
- **D4** — `MembershipType` is an admin-editable entity. Ship with one default: "Annual Individual Membership", 12 months, translatable, perks in JSONB.
- **D5** — Invoices: sequential numbering `LPA-{YYYY}-{NNNNNN}`, VAT fields present but default 0% (O1 — LPA not VAT-registered), PDF via WeasyPrint, stored in R2.
- **D6** — No public refund flow. Admin-only manual refund action with mandatory reason + audit log.
- **D7** — Webhook idempotency via `WebhookEvent` table with unique constraint on `(provider, provider_event_id)`.
- **D8** — Five sub-phases: 03a schema+domain, 03b ports+EveryPay+R2+webhook, 03c use cases+API, 03d UI+admin, 03e scheduler+emails+i18n.

## Scope

**Must deliver:**

1. DB schema — `MembershipType`, `Membership`, `Payment`, `Invoice`, `PaymentToken`, `WebhookEvent`
2. Domain — `MembershipStatus` VO with transition rules (Active → Grace → Lapsed → Cancelled), `Money` VO (EUR-only guard), `InvoiceNumber` VO
3. Payment port + **EveryPay adapter** — `PaymentGateway` ABC, EveryPay concrete implementation, HMAC webhook verifier
4. Object storage port + **R2 adapter** — `ObjectStorage` ABC, R2 concrete implementation, MinIO container for local dev
5. Invoice generation — WeasyPrint PDF templates (LV/EN/RU), sequential numbering via Postgres sequence
6. Use cases — purchase (one-off and recurring), renew, cancel, charge_with_token, process_webhook, generate_invoice, admin manual refund
7. API routes — member-facing membership endpoints + EveryPay webhook handler + invoice download
8. Frontend — join page, membership dashboard, payment history, invoice download, switch-renewal-mode, remove-card
9. Admin — membership types CRUD, member list, manual refund with reason, status override with reason
10. Scheduled tasks — renewal MIT charges (T+0/+2/+5/+9), status transitions, reminder emails
11. Email templates — welcome, T-30/-7/-1 reminders, grace period, lapsed, receipt, failed renewal
12. Multilingual coverage — LV/EN/RU for all new user-facing strings and email templates

**Not in scope (deferred):**

- Training registration and capacity (Phase 4)
- Certificate PDFs (Phase 5 — will reuse R2 adapter from 03b)
- Directory listings / "LPA Verified" badge display (Phase 6 — membership just sets `display_in_public_directory` perk flag)
- Promo codes, discount stacking, family memberships, group billing
- Credit notes (schema-ready but no UI)
- VAT registration flow (schema-ready, admin toggle deferred to Phase 8)
- Auto-detection of 50k threshold (Phase 8 dashboard widget)
- Auth for admin console polish (Phase 8)
- Public refund request UI (out of scope per D6)

## Sub-phases

| Sub-phase | Goal                                                                              | Owner(s)                                                                  | Parallel?                           |
| --------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------- |
| **03a**   | DB schema + Alembic + domain entities + value objects + status rules              | database-agent ‖ backend-agent                                            | Yes (disjoint files)                |
| **03b**   | Ports (PaymentGateway, ObjectStorage) + EveryPay adapter + R2 adapter + webhooks  | backend-agent (ports) ‖ payments-agent (EveryPay) ‖ devops-agent (R2+MinIO) | Yes (3-way parallel)                |
| **03c**   | Use cases + API routes + invoice generation service                              | backend-agent                                                             | No (needs 03b)                      |
| **03d**   | Frontend member pages + admin views + i18n keys                                  | frontend-agent ‖ i18n-agent (locales in parallel)                         | Yes                                 |
| **03e**   | Celery beat tasks + email templates + integration tests + close gates            | backend-agent ‖ i18n-agent (email bodies)                                 | Yes                                 |

---

## Sub-phase 03a: Database schema + domain

**Owners:** database-agent (H1) ‖ backend-agent (H2) — parallel, disjoint files

**H1 deliverables (database-agent):**

- `backend/app/domain/entities/membership_type.py` — dataclass: id, code, name_i18n, description_i18n, duration_months, price_cents, currency, grace_period_days, perks (dict), is_active, sort_order, created_at, updated_at
- `backend/app/domain/entities/membership.py` — dataclass: id, member_id, membership_type_id, starts_at, expires_at, status, renewal_mode (oneoff/recurring), payment_token_id, grace_period_days (snapshot), membership_type_snapshot (JSONB), created_at, updated_at
- `backend/app/domain/entities/payment.py` — dataclass: id, provider, provider_payment_id, member_id, membership_id (nullable), amount_cents, currency, status (pending/succeeded/failed/refunded), payment_method, created_at, updated_at
- `backend/app/domain/entities/invoice.py` — dataclass: id, invoice_number, payment_id, member_id, issued_at, due_at, total_cents, vat_rate_pct, vat_amount_cents, net_amount_cents, currency, member_snapshot (JSONB), issuer_snapshot (JSONB), line_items (JSONB), pdf_storage_key (nullable), pdf_generated_at (nullable), is_credit_note, related_invoice_id (nullable)
- `backend/app/domain/entities/payment_token.py` — dataclass: id, member_id, provider, provider_token_id, card_brand, card_last4, card_expires_month, card_expires_year, is_active, created_at
- `backend/app/domain/entities/webhook_event.py` — dataclass: id, provider, provider_event_id, received_at, signature_verified, processed_at, payload, result_status, error_message
- `backend/app/domain/value_objects/money.py` — `Money` frozen dataclass with `amount_cents: int`, `currency: str`; `__post_init__` enforces `currency == 'EUR'` (domain error on violation)
- `backend/app/domain/value_objects/invoice_number.py` — `InvoiceNumber` frozen dataclass with format validation `LPA-{YYYY}-{NNNNNN}`
- `backend/app/infrastructure/database/models.py` — SQLAlchemy models for all six tables above, using Mapped[] syntax
- `backend/alembic/versions/0004_memberships_payments.py` — migration creating all tables, indexes, and the `invoice_number_seq` Postgres sequence
- `backend/tests/domain/test_money.py` — unit tests (EUR-only constraint)
- `backend/tests/domain/test_invoice_number.py` — format validation tests

**H2 deliverables (backend-agent):**

- `backend/app/domain/value_objects/membership_status.py` — `MembershipStatus` enum: ACTIVE, GRACE, LAPSED, CANCELLED
- `backend/app/domain/value_objects/renewal_mode.py` — `RenewalMode` enum: ONEOFF, RECURRING
- `backend/app/domain/rules/membership_status_rules.py` — pure functions: `compute_status(membership, now) -> MembershipStatus`, `can_transition(from_status, to_status) -> bool`, `next_status_transition_at(membership) -> datetime`
- `backend/app/domain/errors/payment_error.py` — `PaymentError`, `WebhookSignatureInvalidError`, `PaymentRefusedError`, `TokenExpiredError`
- `backend/app/domain/errors/membership_error.py` — `MembershipError`, `MembershipAlreadyActiveError`, `InvalidStatusTransitionError`
- `backend/app/domain/errors/storage_error.py` — `StorageError`, `ObjectNotFoundError`
- `backend/tests/domain/test_membership_status_rules.py` — transition matrix tests, time-based status computation tests
- `backend/tests/domain/test_membership_entity.py` — dataclass invariants

**Key constraints:**

- All domain entities are **pure Python dataclasses**, no SQLAlchemy, no Pydantic BaseModel
- All monetary values as `int` minor units (cents), never `float`
- All timestamps UTC
- `issuer_snapshot` and `member_snapshot` on `Invoice` are **write-once at issue time** — never mutated
- `invoice_number_seq` is a Postgres sequence; year prefix applied in Python inside the transaction that inserts the Invoice row
- `WebhookEvent` unique constraint on `(provider, provider_event_id)` is the idempotency gate (D7)
- `Membership.status` is a stored value that is periodically recomputed by the scheduler (03e). Not a computed column — actual DB state so admin can override.

**Verification:**

- `(cd backend && python -m pytest tests/domain/)` passes all new tests
- `(cd backend && alembic upgrade head)` applies cleanly on a fresh DB
- `(cd backend && alembic downgrade -1 && alembic upgrade head)` round-trips cleanly
- `scripts/check_cola_imports.py` passes (no framework imports in domain)

---

## Sub-phase 03b: Ports + EveryPay adapter + R2 adapter + webhooks

**Owners:** backend-agent (H3) ‖ payments-agent (H4) ‖ devops-agent (H5) — three-way parallel, disjoint files

**H3 deliverables (backend-agent — ports + webhook route skeleton):**

- `backend/app/application/ports/payment_gateway.py` — `PaymentGateway` ABC with methods:
  - `create_oneoff_charge(amount: Money, reference: str, return_url: str, notification_url: str, locale: str) -> PaymentInitResult`
  - `create_cit_charge_with_token(amount: Money, reference: str, return_url: str, notification_url: str, locale: str) -> PaymentInitResult` — first charge that captures a reusable token
  - `charge_with_token(amount: Money, reference: str, token: PaymentToken) -> ChargeResult` — MIT
  - `verify_webhook(headers: Mapping[str, str], body: bytes) -> WebhookPayload` — raises `WebhookSignatureInvalidError`
  - `refund(provider_payment_id: str, amount: Money | None) -> RefundResult`
- `backend/app/application/ports/object_storage.py` — `ObjectStorage` ABC: `put_object`, `get_object`, `generate_presigned_get_url`, `delete_object`, `object_exists`
- `backend/app/application/dto/payment_dto.py` — DTOs `PaymentInitResult`, `ChargeResult`, `WebhookPayload`, `RefundResult` as frozen dataclasses, fully provider-neutral
- `backend/app/api/routes/webhooks.py` — FastAPI route `POST /api/webhooks/payments/everypay`: (1) reads body+headers, (2) calls `PaymentGateway.verify_webhook()`, (3) inserts `WebhookEvent` row (idempotency gate), (4) calls application use case `process_payment_webhook`, (5) returns 200/400. No business logic in the route.
- `backend/tests/application/ports/test_payment_gateway_contract.py` — contract tests using a `FakePaymentGateway` that any future adapter must also pass
- `backend/tests/application/ports/test_object_storage_contract.py` — same pattern with `FakeObjectStorage`

**H4 deliverables (payments-agent — EveryPay concrete):**

- `backend/app/infrastructure/payments/everypay/__init__.py`
- `backend/app/infrastructure/payments/everypay/client.py` — HTTP client wrapping EveryPay API (`api_username` + `api_secret` HTTP Basic auth)
- `backend/app/infrastructure/payments/everypay/adapter.py` — `EveryPayGateway(PaymentGateway)` implementing all five port methods; maps EveryPay fields (`payment_method=bank_link`, `preferred_country=LV`, `token_agreement=recurring`) to provider-neutral DTOs
- `backend/app/infrastructure/payments/everypay/signature.py` — HMAC-SHA1 verifier for webhook callbacks (sorted form params concatenated, shared-secret hex digest)
- `backend/app/infrastructure/payments/everypay/config.py` — Pydantic Settings sub-model: `EVERYPAY_API_USERNAME`, `EVERYPAY_API_SECRET` (SecretStr), `EVERYPAY_ACCOUNT_NAME`, `EVERYPAY_BASE_URL`, `EVERYPAY_WEBHOOK_SECRET` (SecretStr)
- `backend/tests/infrastructure/payments/everypay/test_adapter.py` — unit tests against recorded sandbox responses (`responses` or `httpx.MockTransport`)
- `backend/tests/infrastructure/payments/everypay/test_signature.py` — HMAC verification vectors
- `backend/app/main.py` — DI wiring: select adapter based on `PAYMENT_PROVIDER` env var

**H5 deliverables (devops-agent — R2 + local MinIO):**

- `backend/app/infrastructure/storage/__init__.py`
- `backend/app/infrastructure/storage/r2_object_storage.py` — `R2ObjectStorage(ObjectStorage)` using `boto3` with custom endpoint URL; presigned URLs via `generate_presigned_url('get_object', ...)`; error wrapping into `StorageError`
- `backend/app/infrastructure/storage/fake_object_storage.py` — in-memory implementation used in tests and local dev when R2 creds unavailable
- `backend/app/infrastructure/storage/config.py` — `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` (SecretStr), `R2_SECRET_ACCESS_KEY` (SecretStr), `R2_BUCKET_NAME`, `R2_ENDPOINT_URL` (validator-derived), `STORAGE_PROVIDER` (literal `'r2'|'minio'|'fake'`), `R2_PRESIGNED_URL_TTL_SECONDS` (default 300)
- `docker-compose.yml` — add MinIO service for local dev (`minio/minio:latest`, port 9000, init container creates bucket `lpa-dev`)
- `docs/INFRASTRUCTURE.md` (new) — runbook: how to provision R2 buckets (EU jurisdiction), how to rotate keys, how to sign Cloudflare DPA, lists P1–P5 prerequisite tasks
- `.env.example` — add all new env vars with placeholder values
- `backend/app/infrastructure/config/env.py` — merge new fields into `Settings`
- `backend/tests/infrastructure/storage/test_r2_adapter.py` — integration test against local MinIO (skipped if unreachable)
- `backend/tests/infrastructure/storage/test_fake_storage.py` — unit tests for the fake

**Key constraints:**

- **Provider namespacing in URLs.** Webhook route is `/api/webhooks/payments/everypay`, never `/api/webhooks/payments`. Adding Montonio later means adding a new route, never branching inside an existing one.
- **Port purity.** No EveryPay-specific types (e.g., `payment_method=bank_link` string values) leak past `backend/app/infrastructure/payments/everypay/`. The DTOs use domain enums.
- **No `boto3` imports outside `backend/app/infrastructure/storage/`.** Enforced by `scripts/check_cola_imports.py`.
- **No EveryPay `/subscriptions` or `/plans` endpoints.** D3 forbids them. Add a grep guard.
- **Contract tests run against fakes in CI.** Real EveryPay sandbox tests are gated behind `EVERYPAY_SANDBOX_TESTS=1` env flag and only run on manual invocation.

**Verification:**

- `docker-compose up minio` starts, bucket created
- `(cd backend && python -m pytest tests/infrastructure/storage/)` passes
- `(cd backend && python -m pytest tests/infrastructure/payments/)` passes
- `(cd backend && python -m pytest tests/application/ports/)` passes contract tests
- Manual: hit `POST /api/webhooks/payments/everypay` with a bogus signature → 400; with a valid sandbox signature → 200 and `WebhookEvent` row inserted

---

## Sub-phase 03c: Use cases + API routes + invoice generation

**Owner:** backend-agent (H6)

**Deliverables:**

- `backend/app/application/use_cases/membership/purchase_oneoff.py` — creates Membership (pending), creates Payment (pending), calls `PaymentGateway.create_oneoff_charge()`, returns hosted URL. Uses Result type.
- `backend/app/application/use_cases/membership/purchase_recurring.py` — same flow but `create_cit_charge_with_token()`. On webhook success, captures the returned token into `PaymentToken` row.
- `backend/app/application/use_cases/membership/process_payment_webhook.py` — core state machine: matches webhook event to payment by reference, updates payment status, activates/extends membership, triggers invoice generation, captures token if CIT flow
- `backend/app/application/use_cases/membership/charge_token_for_renewal.py` — used by the scheduler in 03e. Attempts MIT charge, records result, handles retries internally
- `backend/app/application/use_cases/membership/cancel_membership.py` — user-initiated cancellation. If recurring, flips to oneoff mode (stops future charges). Membership stays active until `expires_at`.
- `backend/app/application/use_cases/membership/remove_payment_token.py` — deletes token row, flips recurring membership back to oneoff
- `backend/app/application/use_cases/membership/switch_renewal_mode.py` — oneoff ↔ recurring. Recurring → oneoff is free. Oneoff → recurring requires capturing a new token (redirects to CIT flow).
- `backend/app/application/use_cases/admin/manual_refund.py` — site-admin only; requires `reason: str` (min length 10); calls `PaymentGateway.refund()`; creates audit log entry
- `backend/app/application/use_cases/admin/override_membership_status.py` — site-admin only; requires reason; audit log
- `backend/app/application/services/invoice_generator.py` — generates invoice number (inside the payment-success DB transaction, from sequence), populates snapshots from current settings + member, builds line items, saves `Invoice` row with `pdf_storage_key = None`
- `backend/app/application/services/invoice_pdf_renderer.py` — renders PDF on demand: checks `Invoice.pdf_storage_key`, if null renders Jinja2 → HTML → WeasyPrint → `ObjectStorage.put_object()`, saves key to row; returns presigned URL for download
- `backend/app/infrastructure/invoices/templates/invoice_lv.html` — Latvian template (primary)
- `backend/app/infrastructure/invoices/templates/invoice_en.html` — English
- `backend/app/infrastructure/invoices/templates/invoice_ru.html` — Russian
- `backend/app/infrastructure/invoices/templates/styles.css` — shared print styles
- `backend/app/api/routes/memberships.py` — `POST /api/memberships/purchase`, `GET /api/memberships/me`, `POST /api/memberships/me/cancel`, `POST /api/memberships/me/switch-mode`, `POST /api/memberships/me/remove-card`
- `backend/app/api/routes/invoices.py` — `GET /api/invoices/me` (list), `GET /api/invoices/{id}/download` (redirects to presigned R2 URL after auth check)
- `backend/app/api/routes/admin_memberships.py` — admin-only routes for types CRUD, member list, manual refund, status override
- New repositories: `MembershipRepository`, `PaymentRepository`, `InvoiceRepository`, `PaymentTokenRepository`, `WebhookEventRepository`, `MembershipTypeRepository` in `backend/app/infrastructure/database/repositories/`
- Tests: full application-layer unit tests against fake repositories and fake gateway. Integration tests for invoice PDF rendering (WeasyPrint — asserts output starts with `%PDF-`).

**Key constraints:**

- Use cases return `Result[T, DomainError]`, never raise for expected failures
- Invoice number assignment happens at payment-success webhook time, inside the same transaction that marks payment `succeeded`. PDF render is a separate, retryable step — keeps numbering gap-free.
- Admin override requires a `reason` field (audit requirement from D6)
- Manual refund checks: payment must be in `succeeded` status, refund amount ≤ original amount, not already refunded
- **GDPR:** member deletion (Phase 9) must anonymize `Invoice.member_snapshot` but NOT delete the invoice row or PDF (5-year accounting retention). Document this now in the repository comment so Phase 9 respects it.

**Verification:**

- `(cd backend && python -m pytest tests/application/use_cases/membership/)` passes
- `(cd backend && python -m pytest tests/application/services/test_invoice_generator.py)` passes
- Manual: `POST /api/memberships/purchase` → 200 + hosted URL; simulate EveryPay webhook → membership activates, invoice created, PDF downloadable via presigned URL

---

## Sub-phase 03d: Frontend + admin views + i18n

**Owners:** frontend-agent (H7) ‖ i18n-agent (H8) — parallel

**H7 deliverables (frontend-agent):**

- `frontend/src/app/[locale]/(public)/join/page.tsx` — enhanced: membership type selection (shows all active types from API), pricing display, "One-off" vs "Recurring" toggle, cancellation policy disclosure, submit → redirect to EveryPay hosted page
- `frontend/src/app/[locale]/(member)/membership/page.tsx` — dashboard: current status badge (Active/Grace/Lapsed), expiry countdown, renewal mode indicator, saved card display (brand + last4), action buttons (switch mode, remove card, cancel)
- `frontend/src/app/[locale]/(member)/membership/payments/page.tsx` — payment history table with download-invoice buttons
- `frontend/src/app/[locale]/(member)/membership/return/page.tsx` — EveryPay return URL handler: "processing payment" state, polls for webhook result, shows success/failure
- `frontend/src/app/[locale]/(admin)/membership-types/page.tsx` — list + create
- `frontend/src/app/[locale]/(admin)/membership-types/[id]/page.tsx` — edit (with "existing memberships unaffected" warning)
- `frontend/src/app/[locale]/(admin)/members/page.tsx` — searchable list with status filter
- `frontend/src/app/[locale]/(admin)/members/[id]/page.tsx` — member detail: history, actions (manual refund, status override) opening modals that require a reason
- `frontend/src/lib/api-client.ts` — extend with membership, invoice, and admin endpoints
- `frontend/src/components/membership/StatusBadge.tsx` — Active/Grace/Lapsed/Cancelled
- `frontend/src/components/membership/RenewalModeToggle.tsx`
- `frontend/src/components/membership/SavedCardDisplay.tsx`
- `frontend/src/components/membership/CancellationPolicy.tsx` — shown at checkout
- Design system compliance: `--lpa-*` tokens only, pill buttons, 12px card radius, one primary button per view, WCAG AA

**H8 deliverables (i18n-agent):**

- `frontend/public/locales/lv/membership.json` — all new membership UI strings in Latvian (primary)
- `frontend/public/locales/en/membership.json` — English
- `frontend/public/locales/ru/membership.json` — Russian
- `frontend/public/locales/{lv,en,ru}/invoices.json`
- `frontend/public/locales/{lv,en,ru}/admin_membership.json`
- `frontend/public/locales/{lv,en,ru}/cancellation_policy.json` — legal text for D6 policy display

**Key constraints:**

- Frontend NEVER sees R2 credentials. Invoice download flow: click button → `GET /api/invoices/{id}/download` → backend returns 302 → browser follows to R2 presigned URL → file downloads
- No business logic in the frontend. Status computation comes from the backend.
- `next-intl` locale detection stays disabled (per CLAUDE.md — LV default, no Accept-Language auto-switch)
- All new locale keys must exist in LV, EN, RU. Missing key falls back to LV.

**Verification:**

- `(cd frontend && npm run build)` succeeds
- `(cd frontend && npm run test)` Vitest passes
- Manual: complete checkout flow against EveryPay sandbox (one-off and recurring), see membership activate, download invoice PDF
- All three locales render without raw keys visible

---

## Sub-phase 03e: Scheduler + emails + close gates

**Owners:** backend-agent (H9) ‖ i18n-agent (H10) — parallel

**H9 deliverables (backend-agent — tasks + email sending):**

- `backend/app/infrastructure/tasks/membership_tasks.py` — Celery beat tasks (reusing 02g Celery infrastructure):
  - `recompute_membership_statuses` — hourly; iterates memberships with status `ACTIVE|GRACE` and transitions based on `expires_at + grace_period_days` vs now
  - `charge_recurring_renewals` — daily 02:00 UTC; finds recurring memberships whose `expires_at` is within 1 day; calls `charge_token_for_renewal`
  - `retry_failed_renewals` — every 6 hours; finds failed renewal attempts in the retry window (T+2, T+5, T+9)
  - `send_renewal_reminders` — daily 08:00 UTC; finds memberships at T-30, T-7, T-1, T+0, T+5 boundaries; dispatches via existing `email_queue` port from 02g
  - `lapse_recurring_failures` — daily; memberships whose 4 retry attempts all failed → flip to oneoff mode, send "manual renewal required" email, transition to Lapsed on T+10
- `backend/app/infrastructure/tasks/celery_app.py` — register new tasks + beat schedule entries
- `backend/app/infrastructure/email/translations/{lv,en,ru}.json` — translation bundles consumed by Jinja templates (scope split: i18n-agent owns the JSON, backend-agent owns the Jinja skeletons)
- `backend/app/infrastructure/email/templates/*.html` + `.txt` — thin Jinja skeletons (backend-agent) that render strings from the translation bundles (i18n-agent)
- `backend/tests/infrastructure/tasks/test_membership_tasks.py` — unit tests using `freezegun` + fake repositories
- `backend/tests/integration/test_full_renewal_flow.py` — create membership → simulate time passing → verify status transitions + email dispatches

**H10 deliverables (i18n-agent — email content strings):**

- `backend/app/infrastructure/email/translations/lv.json` — Latvian translations for all event types (welcome, reminder_30d, reminder_7d, reminder_1d, expired_grace, grace_ending, lapsed, receipt, recurring_charge_failed, manual_renewal_required)
- `backend/app/infrastructure/email/translations/en.json` — English
- `backend/app/infrastructure/email/translations/ru.json` — Russian
- Note: i18n-agent does NOT write Jinja templates — backend-agent owns those skeletons. i18n-agent owns the translation strings only. This keeps scope boundaries clean and lets i18n-agent operate on pure JSON.

**Close gates (main session at sub-phase end):**

- `/simplify` on all changed files, findings fixed
- `planning/phase-03-memberships-payments/SECURITY_REVIEW.md` completed (PCI SAQ-A scope, token storage, webhook signature verification, audit logs for refunds)
- `planning/phase-03-memberships-payments/TESTING_GATE.md` completed (E2E sandbox payment, status transitions, reminder emails, admin override flow, invoice download)
- `planning/phase-03-memberships-payments/RETROSPECTIVE.md` produced by efficiency-agent
- All CI green

**Verification:**

- Full E2E flow against EveryPay sandbox: sign up → purchase recurring → webhook activates → invoice downloadable → simulate time passing → renewal charge fires → new invoice → receipt email delivered
- Admin can manually refund with reason, audit log shows entry
- Pytest + Vitest + Playwright all green
- All three locales tested (LV/EN/RU)

---

## Cross-phase dependencies

- **02g Celery infrastructure** is reused directly (celery_app, email_queue port, email sender). Do not fork it.
- **R2 object storage** lands in 03b and will be reused by Phase 5 (certificate PDFs), Phase 6 (profile photos), Phase 7 (resources). The port and adapter are stable across these phases.
- **Phase 8 VAT tracker widget** reads `Invoice.total_cents` rows created in Phase 3. No schema changes needed in Phase 8.
- **Phase 9 GDPR deletion** must anonymize `Invoice.member_snapshot` but not delete invoices (retention).
- **Phase 4 training payments** will reuse the same `PaymentGateway` port and `EveryPayGateway` adapter.

## Parallel dispatch map

- **03a:** H1 (database-agent) and H2 (backend-agent) disjoint — parallel, single message
- **03b:** H3 (backend-agent), H4 (payments-agent), H5 (devops-agent) disjoint — **three-way parallel, single message** (biggest parallelism win in Phase 3)
- **03c:** H6 single handoff — sequential
- **03d:** H7 (frontend-agent) ‖ H8 (i18n-agent) — parallel, pre-flight required since both touch `frontend/**`
- **03e:** H9 (backend-agent) ‖ H10 (i18n-agent) — parallel, disjoint directories

Pre-flight per handoff: `python scripts/preflight_dispatch.py --agent <name> --files <list>` → exit 0 required.

## Handoff timing

Every handoff instrumented per CLAUDE.md:
```
python scripts/log_handoff_timing.py record --phase 03a --handoff H1 --event dispatch-start
```
Summary table in RETROSPECTIVE.md at sub-phase close.

## Testing strategy

| Layer             | Tool                    | Scope                                                          |
| ----------------- | ----------------------- | -------------------------------------------------------------- |
| Domain            | pytest (unit)           | Status rules, Money VO, InvoiceNumber VO, state machine        |
| Application       | pytest + fakes          | Use cases against FakePaymentGateway + FakeObjectStorage       |
| Infrastructure    | pytest + MinIO + mocks  | R2 adapter against MinIO, EveryPay against recorded responses  |
| API               | pytest + httpx          | Route-level auth, validation, response shape                   |
| Frontend unit     | Vitest                  | Component logic, status badge rendering                        |
| E2E               | Playwright              | Full sandbox flow with freezegun time-travel                   |
| Contract (port)   | pytest                  | Any future gateway/storage adapter must pass the same tests    |

## Critical files to be modified

Key new paths (full list in sub-phase deliverables above):

- `backend/app/domain/entities/{membership_type,membership,payment,invoice,payment_token,webhook_event}.py`
- `backend/app/domain/value_objects/{money,invoice_number,membership_status,renewal_mode}.py`
- `backend/app/domain/rules/membership_status_rules.py`
- `backend/app/domain/errors/{payment_error,membership_error,storage_error}.py`
- `backend/app/application/ports/{payment_gateway,object_storage}.py`
- `backend/app/application/use_cases/membership/*.py` (new directory)
- `backend/app/application/use_cases/admin/*.py` (new directory)
- `backend/app/application/services/{invoice_generator,invoice_pdf_renderer}.py`
- `backend/app/infrastructure/payments/everypay/*.py` (new directory)
- `backend/app/infrastructure/storage/*.py` (new directory)
- `backend/app/infrastructure/invoices/templates/*.html` + `.css`
- `backend/app/infrastructure/tasks/membership_tasks.py`
- `backend/app/infrastructure/email/translations/{lv,en,ru}.json`
- `backend/app/infrastructure/email/templates/*.{html,txt}`
- `backend/app/infrastructure/database/models.py` (extended)
- `backend/app/infrastructure/database/repositories/*.py` (extended + new)
- `backend/app/infrastructure/config/env.py` (extended)
- `backend/alembic/versions/0004_memberships_payments.py`
- `backend/app/api/routes/{memberships,invoices,admin_memberships,webhooks}.py`
- `backend/app/main.py` (DI wiring)
- `frontend/src/app/[locale]/(public)/join/page.tsx` (enhanced)
- `frontend/src/app/[locale]/(member)/membership/**` (new tree)
- `frontend/src/app/[locale]/(admin)/{membership-types,members}/**` (new)
- `frontend/src/components/membership/*.tsx`
- `frontend/src/lib/api-client.ts` (extended)
- `frontend/public/locales/{lv,en,ru}/{membership,invoices,admin_membership,cancellation_policy}.json`
- `docker-compose.yml` (MinIO service)
- `docs/INFRASTRUCTURE.md` (new — R2 runbook)
- `.env.example` (extended)

## Verification (phase close)

- All pytest, Vitest, Playwright green in CI
- `/simplify` clean on all changed files
- Full E2E flow demonstrated manually against EveryPay sandbox: one-off purchase + recurring purchase + reminder at T-7 + renewal MIT charge + refund by admin + cancellation
- Invoice PDF renders correctly in LV/EN/RU with correct sequential numbering
- Status transitions verified with freezegun time-travel in integration tests
- Security review complete: PCI SAQ-A scope documented, no secrets in code, webhook signature verified, audit logs for refund/override
- Retrospective written with handoff timing summary

## Prerequisite user actions before 03b can ship

From DECISIONS.md P1–P5 (Cloudflare R2 + operational setup):

1. Create Cloudflare account + enable R2
2. Create three buckets (`lpa-dev`, `lpa-staging`, `lpa-prod`) with **EU jurisdiction** (irreversible choice at creation)
3. Generate three scoped R2 API token pairs
4. Sign Cloudflare DPA in dashboard
5. (Optional) custom domain `files.lpa.lv` (deferrable to Phase 10)

EveryPay merchant onboarding (lead time — start immediately, do not wait for 03a to finish):

6. Open EveryPay Baltics merchant account via sales contact — Baltic PSPs don't usually have self-serve signup, expect multi-day review
7. Obtain sandbox `api_username` + `api_secret` + `account_name`
8. Enable both `bank_link` and `card` payment methods in EveryPay portal
9. Enable bank payment refunds (D6 admin flow)
10. Obtain webhook shared secret

Main session will remind the user at 03b dispatch. Items 6–10 have merchant-review lead time and should be started in parallel with 03a schema work.
