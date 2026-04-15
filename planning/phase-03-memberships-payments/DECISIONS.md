# Phase 3 — Decisions Log

Locked decisions that constrain Phase 3 (Memberships & Payments) planning and implementation. Update this file as the user resolves each open question; do not silently change a locked entry.

## Locked decisions

### D1 — Payment provider: EveryPay (default), Montonio (future-ready)

**Date:** 2026-04-14
**Decision:** EveryPay Baltics (LHV-owned) is the **default and only implemented** payment provider for Phase 3. Montonio is the **designated secondary** — not implemented in Phase 3, but the architecture must keep a Montonio adapter trivially addable in a future phase.

**Rationale:**
- EveryPay supports the four largest Latvian banks (Swedbank, SEB, Citadele, Luminor) — covers the vast majority of the member base.
- EveryPay natively supports `token_agreement` / Subscriptions, leaving the door open to true auto-renewal if the project later wants it (Montonio bank-only cannot do this).
- LHV ownership = working with an actual Baltic bank, not a fintech intermediary.
- Montonio remains attractive for its wider bank list (Indexo, N26, Revolut) and simpler JWT callback model — worth keeping as a switchable option.

**Architectural implications:**
- `backend/app/application/ports/payment_gateway.py` (PaymentGateway ABC) MUST be written provider-neutral. No EveryPay-specific field names, enums, or error types leak out of the port. The ABC must be expressive enough that a future Montonio adapter slots in without changing the port signature or any application/use_case code.
- `backend/app/infrastructure/payments/` will contain ONE adapter sub-package in Phase 3: `everypay/`. A `montonio/` sub-package may be added in a later phase.
- Provider selection is wired via DI in `backend/app/main.py` and configured via env var (e.g., `PAYMENT_PROVIDER=everypay`). The DI container resolves the concrete adapter; no other code references the provider by name.
- The webhook route MUST be provider-aware at the URL level (`/webhooks/payments/everypay`) so that adding Montonio later means adding a new route, not branching inside an existing one. Each provider has its own signature scheme (EveryPay = HMAC-SHA1 of sorted form params; Montonio = JWT HS256) and they should not share verification code.
- Tests cover the EveryPay adapter concretely. The port itself gets contract tests using a fake adapter so a future Montonio adapter has a target to pass.

**What this does NOT decide (still open):**
- Whether to enable EveryPay's Cards + `token_agreement=recurring` for true auto-renewal, or stick to bank-only with reminder-driven manual renewal. See D2 (open).
- Whether to enable EveryPay's native Subscriptions/Plans object or model membership lifecycle entirely in our own domain. See D3 (open).

---

### D2 — Auto-renewal: customer chooses at checkout

**Date:** 2026-04-14
**Decision:** At checkout / membership purchase, the customer chooses between **(a) one-off bank payment with annual reminder emails** or **(b) automatic recurring renewal via EveryPay card-on-file (`token_agreement=recurring` / MIT)**. Both flows must work in Phase 3.

**Implications:**
- EveryPay must be configured with **both** `bank_link` and `card` payment methods enabled. Cards must be enabled in the EveryPay merchant portal and in our `PAYMENT_METHODS_ENABLED` env list.
- Two distinct purchase flows in the use cases layer: `purchase_membership_oneoff` (returns hosted page URL → bank link or one-off card) and `purchase_membership_recurring` (first charge as CIT card payment that captures a token, subsequent renewals as MIT charges via scheduled task).
- The `PaymentGateway` port must expose: `create_oneoff_charge()`, `create_cit_charge_with_token()` (returns a token reference), `charge_with_token()` (MIT). Token storage is in our DB, NOT delegated to EveryPay's customer object — keeps the port provider-neutral so a future Montonio adapter can no-op the recurring methods.
- Token records are first-class domain entities under `backend/app/domain/entities/payment_token.py`. They reference the member, the provider, the provider-side token id, expiry (from card expiry month/year), and a "last 4 / brand" display string.
- PCI scope: SAQ-A. Card details are entered on EveryPay's hosted page only; we never see PAN, only the token. Document this in `SECURITY_REVIEW.md` for Phase 3.
- Member dashboard must show: which model they chose, when next renewal will charge (recurring) or expire (one-off), saved card display string + "remove card" action, and "switch model" action.
- A removed card cancels the recurring schedule and converts the membership back to one-off mode (next renewal will require manual action).
- Failed MIT charges on renewal day → retry policy (e.g., +1d, +3d, +7d), then drop to manual-renewal mode with a notification email. Specifics go in 03e (scheduler + emails) sub-phase plan.

---

### D3 — Subscription orchestration: own-domain

**Date:** 2026-04-14
**Decision:** LPA owns the entire membership lifecycle in its own domain layer. EveryPay is treated as a charge engine only — we do **not** use EveryPay's native Plans/Subscriptions object.

**Why:**
- Keeps the `PaymentGateway` port honest. A future Montonio adapter (which has no subscriptions concept) can implement the same port.
- Lifecycle state machine (Active → Grace → Lapsed) lives in pure domain code, fully testable without provider sandbox.
- Admin UI controls (override status, extend grace, manual activation) operate on our own entities, not on a remote provider object that may be eventually-consistent.
- We can change scheduling behavior (e.g., charge 7 days before expiry instead of on expiry) without coordinating with EveryPay.

**How to apply:**
- The scheduled task (Celery beat, reusing 02g infrastructure) iterates LPA's own `Membership` rows, computes who needs charging today, and calls `PaymentGateway.charge_with_token()` per row. EveryPay never decides "when to charge."
- No code path may call EveryPay's `/subscriptions` or `/plans` endpoints. Add a CI grep guard in `scripts/check_cola_imports.py` (or a sibling script) if needed.

---

### D4 — Membership types: admin-editable, 1-year default, future-flex schema

**Date:** 2026-04-14
**Decision:** Membership types are **admin-editable** entities (not hardcoded enums). Phase 3 ships with one default type — **"Annual Individual Membership"**, 12-month duration — but the schema MUST support multiple types with different durations, prices, and perk sets.

**Schema requirements:**
- `MembershipType` table — id, code (slug), name (translatable LV/EN/RU), description (translatable), duration_months (int), price_cents (int), currency (default EUR), is_active (bool), created_at, updated_at, sort_order.
- `MembershipTypePerk` join — what perks come with the type. At minimum in Phase 3:
  - `display_in_public_directory` (bool) — type confers visibility in the instructor catalog (Phase 6).
  - `discount_on_trainings_pct` (int, default 0) — placeholder for Phase 4.
  - Other perk flags addable in later phases without migration headaches → consider a `perks JSONB` column with a versioned schema, OR a strict `MembershipTypePerk` enum table. **Recommend JSONB with Pydantic validation at the application layer** — gives admin flexibility, validates at write time, no migrations to add a perk.
- `Membership` table — id, member_id, membership_type_id (FK, snapshot type at purchase time), starts_at, expires_at, status (Active/Grace/Lapsed/Cancelled), renewal_mode (oneoff/recurring), payment_token_id (nullable, FK), grace_period_days (snapshot from type at purchase), created_at, updated_at.
- **Snapshot pattern:** when a member purchases, we snapshot the price and key fields onto the `Payment` / `Invoice` row, so a later admin price change does not retroactively affect existing memberships or audit history.
- Admin console (Phase 8 will polish, but Phase 3 ships a basic CRUD): list types, create new type, edit existing type (with warning that existing memberships are unaffected), deactivate type (existing memberships continue, no new purchases).
- Grace period length is **per-type**, defaulting to 10 days. Stored on `MembershipType.grace_period_days`.
- Multilingual: `name` and `description` use the same translation pattern as content entities (LV primary, EN/RU optional, falls back to LV).

**What this does NOT include in Phase 3:** auto-pricing tiers, promo codes, family/group memberships, discount stacking. These are explicitly deferred — schema must not preclude them but no UI or use case in Phase 3.

---

### D5 — Latvian invoices: sequential numbering, VAT, PDF — in scope

**Date:** 2026-04-14
**Decision:** Phase 3 ships **fully Latvia-compliant invoices**: sequential numbering, VAT line items, legal entity details, and on-demand PDF generation. Members can download invoices for any past payment from their dashboard.

**Requirements:**
- `Invoice` table — id, invoice_number (string, unique, sequential), payment_id (FK), member_id, issued_at, due_at (= issued_at for paid invoices), total_cents, vat_rate_pct, vat_amount_cents, net_amount_cents, currency, member_snapshot (JSONB: name, address, personal/company id), issuer_snapshot (JSONB: LPA legal entity details, registration number, VAT number, address), line_items (JSONB array), pdf_storage_key (nullable), pdf_generated_at (nullable).
- **Sequential numbering** is a hard legal requirement in Latvia: format `LPA-{YYYY}-{NNNNNN}` (year prefix, six-digit zero-padded sequence). Generated by a Postgres sequence + transactional `INSERT` to guarantee no gaps and no duplicates. **Never reuse numbers, never skip.** A failed payment that produced an invoice number must produce a credit note, not deletion.
- **VAT rate** stored on the invoice (snapshot, not lookup) so a later VAT change does not mutate historical invoices. Phase 3 default: 21% standard rate. Confirm with user whether LPA membership is VAT-exempt (associations sometimes are) — see open question O1 below.
- **Issuer snapshot** stored per invoice so a later change to LPA's legal address / VAT number does not rewrite history.
- **PDF generation** — server-side, generated on-demand on first download and cached to object storage. Use a templated approach (Jinja2 → HTML → WeasyPrint or wkhtmltopdf). Templates live in `backend/app/infrastructure/invoices/templates/` and are translatable LV/EN/RU.
- **Storage:** invoice PDFs go to S3-compatible object storage (whatever the project picks for general file storage — likely an open question for Phase 3 or Phase 7).
- **Credit notes:** out of scope for Phase 3 *unless* the refund flow needs them. D6 says no refunds in normal flow → no credit notes in Phase 3 either. Schema must allow them later (`Invoice.is_credit_note` bool, `Invoice.related_invoice_id` FK).
- **Email delivery:** receipt email after successful payment includes a link to download the invoice PDF (not an attachment, to avoid email size and attachment-scanning issues).

**Open question to resolve before 03a starts:**
- **O1** — Is LPA membership VAT-exempt under Latvian law (non-profit association exemption), or does it bear standard 21% VAT? This determines whether Phase 3 ships with VAT calculation as 0% or 21%. The schema is the same either way, but the default value and the line-item display change.

---

### D6 — Refund policy: no refunds in normal flow, exceptions out-of-scope for dev

**Date:** 2026-04-14
**Decision:** **No refunds** for memberships or training registrations in the normal flow. Once purchased, the spot/membership is reserved. Two exceptions exist but are **handled outside the dev process** (manual admin action, not a self-service flow):
1. **Serious health problems** with a doctor's note → training can be deferred to the next instance of the same event, or refunded.
2. **Legitimate dispute over education quality** → reviewed case by case.

**Implications for Phase 3 dev work:**
- Public-facing refund UI: **none.** No "request refund" button in the member dashboard.
- Admin console: a "manual refund" action exists for site admins only. Requires a mandatory `reason` text field (audit log entry). Triggers EveryPay refund API call. Creates a credit note invoice (deferred to whichever phase actually needs to ship credit notes — schema is ready in D5).
- Cancellation policy text must be displayed at checkout (legal requirement + UX). i18n keys for the policy go in 03 i18n handoff.
- The `PaymentGateway.refund()` port method is implemented in Phase 3 (because admin needs it), but is NOT exposed via any public API route. It is only callable from an authenticated admin route.
- No automated refund logic anywhere — no "auto-refund on cancel within X days" rules. The admin reviews, decides, clicks.

---

### D7 — Webhook idempotency: store in our DB

**Date:** 2026-04-14
**Decision:** Webhook idempotency is enforced by **storing every processed payment reference in our own database**. We do not rely on EveryPay's dedupe.

**How:**
- `WebhookEvent` table — id, provider (string, default 'everypay'), provider_event_id (string, unique with provider), received_at, signature_verified (bool), processed_at (nullable), payload (JSONB), result_status (string), error_message (nullable text).
- Composite unique index on `(provider, provider_event_id)`.
- Webhook handler logic:
  1. Verify HMAC signature → reject 400 if invalid.
  2. Insert `WebhookEvent` row inside a transaction. If unique constraint violation → log and return 200 (already processed, idempotent replay).
  3. Process the event (update payment, membership, invoice).
  4. Update `processed_at` and `result_status` on the same row.
- Replay-safe by construction. No race condition because the unique constraint is the gate.
- Retention: keep events forever (audit trail). They are small JSONB rows — not a storage concern for the next 5+ years.

---

### D8 — Sub-phase slicing: confirmed

**Date:** 2026-04-14
**Decision:** Phase 3 splits into five sub-phases as proposed:

- **03a** — Database schema + domain entities + value objects. `MembershipType`, `Membership`, `Payment`, `Invoice`, `PaymentToken`, `WebhookEvent`. Domain rules for status transitions (Active → Grace → Lapsed). Money value object.
- **03b** — `PaymentGateway` port + EveryPay infrastructure adapter + webhook route + signature verification. Sandbox-tested end-to-end.
- **03c** — Application use cases (purchase_oneoff, purchase_recurring, renew, cancel, charge_token, process_webhook, generate_invoice) + API routes for member-facing operations.
- **03d** — Frontend UI (join page, membership dashboard, payment history, invoice download, "switch renewal mode", "remove card") + admin views (membership types CRUD, member list, manual refund, status override with reason).
- **03e** — Scheduled tasks (renewal-day MIT charges, status transitions, reminder emails, retry policy) + email templates (welcome, T-30/T-7/T-1 reminders, expiry, receipt with invoice link, failed renewal) + i18n for all of the above.

Each sub-phase ships independently with its own simplify pass, security review, testing gate, and retrospective.

---

## Resolved questions (previously O1–O5)

### O1 — VAT status: not VAT-registered (resolved 2026-04-15)

LPA is **not** currently registered as a VAT payer. Invoices issued in Phase 3 are **VAT-exempt by default** — no VAT line item, no VAT number on the issuer snapshot.

**Forward-compatibility requirement:** LPA may cross the **EUR 50,000 annual turnover** threshold in future, at which point VAT registration becomes mandatory and standard 21% VAT applies. The schema from D5 **already supports this** (`vat_rate_pct` and `vat_amount_cents` are per-invoice fields, issuer_snapshot JSONB already holds VAT number as nullable). At that future switch-over:
- A site-admin setting flips LPA into VAT-registered mode (stores PVN Nr., default VAT rate).
- All new invoices start carrying VAT. Historical invoices remain untouched (snapshot pattern protects them).
- Recommended: add an application-layer `TurnoverMonitor` or simple admin dashboard widget that warns when year-to-date sales approach 50k, so the admin has lead time to register. Not required in Phase 3 — nice-to-have for Phase 8 (admin console).

### O2 — Legal entity details: provided (resolved 2026-04-15)

Invoice issuer snapshot uses these values by default (stored per-invoice so later changes don't mutate history):

- **Legal name:** Latvijas Pilates Asociācija
- **Address:** Liepu iela 1-3, Carnikava, LV-2163, Latvia
- **Registration number (Reģ.Nr.):** 40008275984
- **VAT number (PVN Nr.):** *none* (see O1 — not VAT-registered)
- **Bank:** Swedbank AS
- **IBAN:** LV06HABA0551049722788
- **BIC/SWIFT:** HABALV22

These go into a default config block loaded from env vars (names TBD in 03a handoff), so the values are not hardcoded in source and can be changed via admin UI later. Each invoice issued snapshots the values at issue time.

### O4 — Grace period: 10 days confirmed (resolved 2026-04-15)

`MembershipType.grace_period_days` defaults to **10** for the Annual Individual Membership. Admin can override per-type. Status transitions from Active → Grace happen on `expires_at`, Grace → Lapsed on `expires_at + grace_period_days`.

**Reminder schedule adjusted to match the tighter 10-day grace window:**
- T-30 days: first reminder ("renewal in 1 month")
- T-7 days: second reminder
- T-1 day: final pre-expiry reminder
- T+0 (expiry day): "your membership expired, you have 10 days of grace"
- T+5 days: "5 days left before your listing is removed"
- T+10 days: Grace → Lapsed, "your membership has lapsed" notification

For recurring-renewal members, MIT charge retries are compressed to fit inside grace: T+0, T+2, T+5, T+9. If all four fail the membership drops to Lapsed on T+10 and the member falls back to manual-renewal mode.

### O5 — Currency: EUR only (resolved 2026-04-15)

Phase 3 ships **EUR only**. The domain-layer `Money` value object validates `currency == 'EUR'` and raises on any other code. The database column exists on every monetary row anyway, so multi-currency is a future schema-compatible flip (not a rewrite). No admin UI for currency selection in Phase 3.

---

### O3 — Object storage: Cloudflare R2 (resolved 2026-04-15)

**Decision:** Cloudflare R2 is the object storage backend for Phase 3 and all future file-storing phases (Phase 5 certificates, Phase 6 profile photos, Phase 7 resources/downloads, any future user uploads). S3-compatible API, zero egress fees, EU jurisdiction region, no lock-in.

**Why:** Detailed rationale above. Zero egress future-proofs against Phase 7 video content. S3 API compatibility means a later swap to AWS S3 / Scaleway / Backblaze / MinIO is a config change, not a code rewrite.

---

## R2 implementation plan (cross-phase)

This integration is a **devops-agent-owned cross-phase concern**. Phase 3 drives the need, but the adapter must be written once and reused by Phases 5, 6, and 7 without modification. Plan it as a proper port + adapter from day one.

### Architecture

**Port (application layer, new):** `backend/app/application/ports/object_storage.py` — Python ABC `ObjectStorage` with methods:

- `put_object(key: str, body: bytes, content_type: str, metadata: dict[str, str] | None = None) -> None` — upload.
- `get_object(key: str) -> bytes` — download (used for internal regeneration; most downloads go through signed URLs).
- `generate_presigned_get_url(key: str, expires_in_seconds: int) -> str` — returns a short-lived signed URL that the frontend redirects the user to for direct download. This is how member invoice downloads work — the backend never proxies the file body, Cloudflare serves it directly.
- `delete_object(key: str) -> None` — used for GDPR deletion flows (Phase 9).
- `object_exists(key: str) -> bool` — idempotency check before regenerating PDFs.

The port is **provider-neutral**. No R2-specific types leak through. Return types are primitives or domain types.

**Adapter (infrastructure layer, new):** `backend/app/infrastructure/storage/r2_object_storage.py` — concrete `R2ObjectStorage(ObjectStorage)` class using `boto3` with a custom endpoint URL (R2 speaks S3 API over a Cloudflare endpoint like `https://<account-id>.r2.cloudflarestorage.com`).

- Authentication: R2 access key ID + secret access key, read from env via Pydantic Settings.
- Region: `auto` (R2 handles routing).
- Signature version: `s3v4` (required by R2).
- Presigned URLs: generated via `boto3` `generate_presigned_url` — works identically to AWS S3.
- Error handling: wrap `botocore.exceptions.ClientError` into typed domain errors from `backend/app/domain/errors/storage_error.py` (new).

**Dependency injection:** wire `R2ObjectStorage` in `backend/app/main.py` via the existing DI pattern from Phase 02. Future env flag `STORAGE_PROVIDER=r2|s3|minio|fake` allows swapping adapters for tests or future providers without touching application code.

**Test double:** `backend/tests/infrastructure/storage/fake_object_storage.py` — in-memory implementation of the port. Used by all use case tests so nothing hits real R2 in CI.

### Bucket design

One bucket per environment, not one per domain entity. Segregation is by **key prefix**, not bucket:

- `invoices/{YYYY}/{invoice_number}.pdf` — invoice PDFs (Phase 3).
- `certificates/{certificate_id}.pdf` — certificate PDFs (Phase 5).
- `profile-photos/{profile_id}/{timestamp}.jpg` — instructor/studio photos (Phase 6).
- `resources/{resource_id}/{filename}` — member resources (Phase 7).
- `user-uploads/{user_id}/{uuid}.{ext}` — any user-submitted files (various phases).

**Why one bucket:** R2 bills per-bucket in some edge cases and simpler IAM. Prefix-based segregation gives you all the same security controls via bucket policy / path-scoped credentials, and keeps the adapter clean.

**Environments:**
- `lpa-dev` bucket — local dev and PR preview environments.
- `lpa-staging` bucket — staging.
- `lpa-prod` bucket — production.

Each environment has its own R2 access key pair, stored as env vars in the respective deployment target. **Never share credentials between environments.**

### Access control

- **Default bucket policy: fully private.** No public reads, no public writes. Every object is accessible only via the R2 API with credentials, or via a presigned URL generated by the backend.
- **Backend is the only credential holder.** The frontend never has R2 credentials. The frontend requests a download URL from the backend (`GET /api/invoices/{id}/download`), the backend checks authorization, generates a signed URL with a short TTL (e.g., 5 minutes), and redirects/returns it. The frontend then fetches the file directly from R2.
- **TTLs on presigned URLs:** 5 minutes for invoice downloads (user clicks → download starts immediately). 60 minutes for resource downloads in Phase 7 (accommodates slow connections / large files).
- **No public buckets ever.** Even "public" content like marketing images goes through the same signed-URL flow or through Cloudflare Images / Cloudflare Pages assets, not directly-public R2.

### Env vars (to add in 03b)

Add to `backend/app/infrastructure/config/env.py` as Pydantic Settings fields:

- `STORAGE_PROVIDER: Literal["r2", "fake"] = "r2"` — swap to `fake` in tests.
- `R2_ACCOUNT_ID: str` — Cloudflare account identifier (URL host component).
- `R2_ACCESS_KEY_ID: SecretStr` — R2 API access key.
- `R2_SECRET_ACCESS_KEY: SecretStr` — R2 API secret key.
- `R2_BUCKET_NAME: str` — environment-specific bucket name.
- `R2_ENDPOINT_URL: str` — computed from account ID (`https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com`). Pydantic validator can derive this if the user prefers.
- `R2_PRESIGNED_URL_TTL_SECONDS: int = 300` — default 5 minutes for most use cases.

All sensitive fields use `SecretStr` so they never appear in logs or error messages.

### GDPR compliance notes

- R2 EU jurisdiction option must be explicitly enabled at bucket creation. Document this in the bucket creation runbook (DevOps-owned).
- Data Processing Agreement (DPA) with Cloudflare must be signed and filed. Cloudflare publishes a standard DPA — link from `SECURITY_REVIEW.md` and keep a signed copy in a non-git secure location.
- Phase 9 (GDPR deletion) must cascade-delete all R2 objects owned by the deleted user. Add `ObjectStorage.delete_object()` calls to the user-deletion use case. Invoice PDFs are a special case — legally retained for 5 years for accounting, so they are NOT deleted on user deletion; only anonymized by redacting the member snapshot fields in the database. Document this carve-out in the deletion use case.
- Access logs: enable R2 access logging to a separate audit bucket. Retention per GDPR → 12 months rolling.

### Cost model (informational)

At LPA's expected scale for year 1 — 500 members, 500 invoices/year, average 100 KB each = 50 MB total invoice storage:

- **Storage cost:** 50 MB × $0.015/GB-month × 12 = **$0.009/year** (less than a cent).
- **Class A operations (writes):** ~1000/year × $4.50/M = **$0.0045/year**.
- **Class B operations (reads):** ~5000/year × $0.36/M = **$0.0018/year**.
- **Egress:** $0 (zero egress fees on R2).
- **Total year 1:** ~$0.02. Practically free.

Phase 7 video content will push the numbers, but storage is the only cost that grows (egress stays $0).

### Implementation sequencing

1. **03a (Phase 3 start)** — schema work only. No R2 code yet.
2. **03b (Payment port + EveryPay adapter)** — the same sub-phase introduces the `ObjectStorage` port + R2 adapter because it's a peer piece of infrastructure and 03c needs it. Handoff split: devops-agent writes `backend/app/infrastructure/storage/` + env vars + `docker-compose.yml` gets a MinIO container for local dev (MinIO is S3-compatible, lets devs work offline without hitting real R2). Backend-agent writes the port ABC + domain errors. Contract tests use the `FakeObjectStorage` double.
3. **03c (Use cases + API)** — invoice generation use case calls `ObjectStorage.put_object()`. Download endpoint calls `generate_presigned_get_url()`.
4. **03d (Frontend)** — member dashboard invoice download button calls the download endpoint, follows the 302 redirect to R2.
5. **DevOps pre-work before 03b lands** — provision R2 bucket (dev + staging + prod), create access keys, add to secrets manager (or env files for now), document in `docs/INFRASTRUCTURE.md` runbook (new file, DevOps scope).

### Open operational prerequisites (user action required before 03b ships)

These are **account-level** tasks the user must do outside the codebase:

- **P1** — Create Cloudflare account (if not already done) and enable R2 in the dashboard. R2 requires a payment method on file even though usage will be within free tier.
- **P2** — Create three R2 buckets: `lpa-dev`, `lpa-staging`, `lpa-prod`. Select **EU jurisdiction** at creation — cannot be changed later.
- **P3** — Create three sets of R2 API tokens (one per environment), each scoped to only its own bucket. Save access key + secret somewhere safe (password manager). Share dev-env credentials with the orchestrator via `.env.local` (gitignored).
- **P4** — Sign Cloudflare's standard Data Processing Agreement in the dashboard (required for GDPR).
- **P5** — Optional: set up a custom domain like `files.lpa.lv` pointing at R2 via Cloudflare DNS. Not required for MVP (presigned URLs work fine), but looks cleaner in the download URL. Can be deferred to Phase 10 polish.

Orchestrator cannot do P1–P4 — they require Cloudflare dashboard access with the user's account. Dispatch a message to the user when 03b is about to start, asking to complete these steps and provide credentials.
