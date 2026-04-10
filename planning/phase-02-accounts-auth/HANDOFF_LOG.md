# HANDOFF_LOG — Phase 02 Accounts & Authentication

Receipt ledger for every agent handoff in Phase 02. Schema per entry (validated
by `scripts/check_handoff_log.py`):

```
## [sub-phase] — [agent] — [ISO date]

- **Task:** one-line summary
- **Scope (files changed):**
  - path1
  - path2
- **Skills invoked:**
  - `skill-name` — PASS | FAIL | N/A (reason)
- **Rule 3 verification:**
  - `<command>` → exit 0
  - `<command>` → exit 0
- **Result:** HANDOFF COMPLETE — PASS | FAIL
- **Notes:** free text. Include `retrofit: true` to mark historical entries
  reconstructed after the fact — the validator will skip strict checks.
```

Source-touching handoffs dated 2026-04-10 or later must:
- list `simplify — PASS` or `simplify — waived — <reason>` in **Skills invoked**
- terminate the **Rule 3 verification** sequence with `pre-commit run --files <changed>` → exit 0
- include a corresponding receipt file under `planning/phase-02-accounts-auth/simplify-receipts/<subphase>-<H#>-<agent>.md` when claiming `simplify — PASS`

---
