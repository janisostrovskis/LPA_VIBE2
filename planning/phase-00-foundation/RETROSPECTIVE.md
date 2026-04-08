# Phase 0 Sub-bootstrap 00a — Retrospective

**Session:** `14c1f101-7a32-426e-be7c-7b14ad1c78c9`
**Date:** 2026-04-08
**Scope reviewed:** Efficiency Agent introduction, Phase 0a plan authoring, devops-agent handoff for `backend/pyproject.toml`, `.github/workflows/ci.yml`, and three `scripts/` enforcement tools, plus main-session verification.

## Context

This was the first agent handoff of the project. The main session wrote `planning/phase-00-foundation/PLAN.md`, then delegated implementation of six deliverables to devops-agent. Verification caught two defects before commit: a hallucinated `build-backend` string and an unconditional `semgrep` dev dependency that does not support Windows. Both were fixed in the main session. The purpose of this retrospective is to determine which of those are systemic (warranting process/doc amendments) and which are one-off noise.

## Findings

### Finding 1 — Hallucinated `build-backend` string in `pyproject.toml`

**Evidence.** Turn 314 (verification read-back): *"I see one bug — the `build-backend` value is wrong. The agent wrote `setuptools.backends.legacy:build`, which doesn't exist. The correct value is `setuptools.build_meta`."* Turn 318 applied the Edit fix.

**Root cause (five-whys).**
1. Why was the value wrong? devops-agent wrote a string that does not exist in setuptools.
2. Why did devops-agent invent it? The handoff prompt (turn 291) specified `build-system = setuptools>=69` but did NOT specify the `build-backend` string, leaving it to the agent's memory.
3. Why is model memory unreliable for this? PEP 517 backend strings are low-frequency tokens where the model's training data contains both the current name (`setuptools.build_meta`) and older/competing names; generating without a lookup has observable error rate.
4. Why wasn't it verified? No rule in devops-agent.md (or anywhere) requires verifying config strings against upstream docs before writing them.
5. Why didn't the handoff specify it? The main session assumed the agent knew the canonical value.

**Classification:** **systemic**. This is the exact class of bug that repeats whenever an agent writes config in a tool it doesn't have cached local docs for. The fix must be a generalizable rule, not "always specify setuptools backend in handoffs."

**Fix location:** `.claude/agents/devops-agent.md` — add a "do not invent config identifiers" rule with a concrete verification fallback (read the installed package's own metadata, or fail the task and ask).

**Cross-platform check:** rule is text-only, platform-agnostic.

---

### Finding 2 — Unconditional `semgrep` dev dependency broke Windows install

**Evidence.**
- Turn 291 handoff prompt contained literal text: `"semgrep>=1.95"` in the dev deps list with no platform marker.
- `.claude/agents/devops-agent.md` line 80 already listed: *"`semgrep` — multi-language SAST"* as a required Python dev dependency with no Windows caveat.
- Turn 363: *"Found a real cross-platform issue: **semgrep does not support Windows.** The plan didn't account for this."*
- Turn 364 Edit: added PEP 508 marker `semgrep>=1.95; sys_platform != 'win32'` with a comment citing semgrep/semgrep#1330.

**Root cause (five-whys).**
1. Why did Windows `pip install -e .[dev]` fail? semgrep has no Windows wheel and no Windows source support.
2. Why was semgrep listed without a marker? devops-agent.md line 80 lists it as an unconditional dev dep; the phase plan copied that list verbatim.
3. Why did the agent file list it unconditionally? The agent file was written assuming a single-platform CI environment and did not apply a cross-platform filter to its *own* tooling recommendations. The only Windows hint in the file is a `winget install gitleaks` line for a different tool.
4. Why wasn't the inconsistency caught when devops-agent wrote pyproject.toml? devops-agent.md has no checklist instructing the agent to test each dependency for dual-platform support before adding it.
5. Why does this matter specifically? The user develops on BOTH Windows and macOS, per the efficiency-agent.md cross-platform rubric. But that rubric only binds efficiency-agent. No other agent file repeats the constraint as a write-time rule.

**Classification:** **systemic, high-priority**. This is the exact failure mode efficiency-agent was designed to catch. The root cause is dual: (a) the devops-agent.md contained a latent Windows-hostile recommendation, and (b) no agent-file-level rule forces a dependency to be validated for both platforms before being added. Left alone, this WILL recur for any future tool (e.g., `uvloop`, `pywin32`, `fcntl`-based tools) added without thought.

**Fix location:**
- `.claude/agents/devops-agent.md` — (i) fix the latent semgrep line to reflect the Windows exclusion, and (ii) add a pre-flight "dual-platform dependency check" rule that applies to every dependency the agent adds, with a concrete checklist and the PEP 508 marker pattern.
- `CLAUDE.md` — add a single-line cross-platform baseline statement. The efficiency-agent rubric already exists but only binds that one agent. A short project-level note ensures every agent inherits the constraint. Narrow and visible, not duplicated.

**Cross-platform check:** the rules being added describe *both* Windows and macOS/Linux paths in the same edit (PEP 508 marker syntax works on all three platforms). Passed.

---

### Finding 3 — Defect-free items (no amendment)

The rest of the cycle ran cleanly:
- Scripts (`check_file_size.py`, `check_cola_imports.py`, `security_scan.py`) passed self-tests on first run.
- CI workflow YAML passed verification.
- PLAN.md authoring did not require rework.
- Handoff/subagent delegation mechanics worked.

**Classification:** no action. Over-amending for a clean cycle is process bloat.

---

### Finding 4 — Task list staleness (observed, not amended)

The harness surfaced a reminder that task tracking tools existed. Main session did not use `TaskCreate`/`TaskUpdate` proactively during the cycle. No user friction resulted; the reminder was advisory.

**Classification:** **one-off**. No pattern evidence. No amendment.

## Amendments Made

1. **`.claude/agents/devops-agent.md`** — Added a `## Dependency & Config Pre-Flight` section with two rules: (a) dual-platform dependency verification with the PEP 508 marker pattern illustrated, and (b) no-invented-identifiers rule for build/config strings, with instruction to verify against the installed package or fail loudly. Fixed the latent `semgrep` line to note Windows exclusion with the same marker. Each rule includes a "Why:" line citing the Phase 00a incident.

2. **`CLAUDE.md`** — Added one short "Dual-platform development" subsection under Technical Constraints stating that every agent-written command, dependency, and script must work on both Windows Git Bash and macOS/Linux bash. One sentence, one "Why:" line. No duplication with the efficiency-agent rubric — the rubric is still the detailed checklist; CLAUDE.md just makes it bind all agents.

## Deferred / Rejected Amendments

- **Do not amend `docs/DEVELOPMENT_RULEBOOK.MD`.** The rulebook is a process document; this is an agent-behavior gap. Adding it there would duplicate the devops-agent.md rule. Narrower scope wins.
- **Do not add a generic "always verify handoff prompts are complete" rule.** That is the kind of vague advice the efficiency-agent anti-patterns section forbids. The concrete fix (no-invented-identifiers + pre-flight check) already addresses the observable failure.
- **Do not add a pyproject.toml template to the devops-agent file.** Templating invites drift; the rule-based fix is more durable.
- **Do not amend efficiency-agent.md.** It did what it was supposed to do — the user invoked it and it is now catching the pattern. No internal gap observed.
- **Do not introduce new pre-commit hooks for dependency validation.** Cannot be done cross-platform without significant tooling work, and the rule-based fix removes the incentive. If the pattern recurs despite the rule, revisit.

---

## Cycle 2 (00a + 00b cumulative)

**Date:** 2026-04-08
**Scope reviewed:** Phase 00b devops-agent handoff producing `docker-compose.yml`, `.env.example`, and related compose wiring; main-session verification step 5 (raw `psycopg.connect`).

### Context

Phase 00b just landed. devops-agent generated a third defect of the same general class as 00a's two: a plausible-looking string that does not work in its actual consumer. The Cycle 1 retrospective added a "Dependency & Config Pre-Flight" section to `.claude/agents/devops-agent.md` (Rule 1 dual-platform, Rule 2 no-invented-identifiers) — and that section was in place when 00b ran. Defect C still happened. This cycle's question is whether Rule 2 needs hardening or replacement.

### New Findings

**Finding 5 — Defect C: hallucinated `postgresql+psycopg://` URL scheme.**

*Evidence.* devops-agent wrote `DATABASE_URL=postgresql+psycopg://lpa:lpa@db:5432/lpa` in both `docker-compose.yml` and `.env.example`. The `+psycopg` form is a SQLAlchemy URL-dialect convention; raw psycopg3, libpq, and the MCP postgres server cannot parse it. Caught by 00b verification step 5 (`psycopg.connect(url)` raised `ProgrammingError: missing "=" after ...`). Current `docker-compose.yml:29` now reads `postgresql://lpa:lpa@db:5432/lpa` (corrected). Note: `.github/workflows/ci.yml:134` still uses the `+psycopg` form, which is correct *there* because it is consumed by SQLAlchemy in tests — same string, different consumer, different correctness. This is exactly why the rule must be "verify against the actual consumer," not "memorize the right string."

*Root cause (five-whys).*
1. Why was the string wrong? `+psycopg` is a SQLAlchemy URL convention, not a libpq/psycopg one, and the consumer in compose/`.env.example` is raw `psycopg.connect()`.
2. Why didn't Rule 2 catch it? Rule 2 says "verify against the installed package or fail loudly" but provides no enforcement step. The agent classified `postgresql+psycopg://` as well-known (it is, in SQLAlchemy contexts) and never reached for verification.
3. Why no enforcement step? Rule 2 was written as a behavioral norm ("never invent"), not as a procedure ("run X before declaring done"). Behavioral norms degrade under model uncertainty about what counts as "inventing"; procedures don't.
4. Why is this the third instance? All three defects (A: `setuptools.backends.legacy:build`; B: unconditional `semgrep`; C: `postgresql+psycopg://`) share a single shape: a *string* that looks plausible but breaks when actually consumed. None are catchable by reading docs in isolation; all three are catchable by executing the consumer once.
5. Why does executing the consumer work where rule-reading doesn't? Strings produced by the model live in a fuzzy space of "things that occur near related concepts in training data." The only deterministic test is the actual program that parses them. This is the same reason we lint code instead of asking models to write lint-clean code.

*Common root cause across A, B, C (one sentence).* All three defects are model-generated *strings* (an entry-point identifier, a package name in a platform context, a URL scheme) that look plausible from training-data adjacency but fail when fed to their real consumer; none can be caught by reading documentation, only by executing the code path that parses the string.

*Classification.* **Systemic, escalated.** Defect C alone might be one-off; Defect C *despite the post-A amendment* is a process-rule failure. The Cycle 1 fix was necessary but insufficient. The rule lacked an enforcement mechanism.

*Why Rule 2 specifically failed.* See `.claude/agents/devops-agent.md:75-79`. The rule's three sub-points are: "read installed package metadata," "fetch upstream docs or fail loudly," "never invent." None of these are *triggered* by anything observable to the agent at write-time. The agent has to first decide "this is a string I might be inventing" before the rule fires. For a string the agent is confident about, the rule is dormant. Confidence is exactly the failure mode — the agent was confident about `setuptools.backends.legacy:build` too. The rule needs to fire on *every* config string, regardless of confidence, and the trigger needs to be mechanical (a verification command), not introspective (a self-doubt check).

*Fix location.* `.claude/agents/devops-agent.md` Pre-Flight section. Add a Rule 3 that mandates execution-based verification for every config string before HANDOFF COMPLETE, with a concrete table of (artifact → verification command) pairs covering at minimum: `pyproject.toml`, database URLs, Docker image tags, GitHub Actions refs, framework config keys, entry-point strings. The table must be extendable as new config types appear. The rule must explicitly forbid declaring HANDOFF COMPLETE on unverified strings — strings the agent could not verify must be marked PENDING-VERIFICATION in the handoff so the main session knows to check.

*Cross-platform check.* All proposed verification commands (`pip install`, `psycopg.connect`, `docker pull`, `python -c "import ..."`) work identically on Windows Git Bash and macOS bash. Rule 3 maintains the dual-platform constraint introduced in Cycle 1.

*Is the existing Pre-Flight section structurally sound?* Yes — Rules 1 and 2 are still correct and still pull weight (Rule 1 is a write-time gate on dependency platform support; Rule 2 establishes intent). The gap is purely the missing enforcement layer. **Add Rule 3, do not rewrite Rules 1 or 2.** Rewriting Rule 2 would lose the "Why" anchor for Defect A and risk regressing to vagueness.

### Amendments Made

1. **`.claude/agents/devops-agent.md`** — Added **Rule 3 — Verify every config string by executing the code path that consumes it** to the `## Dependency & Config Pre-Flight` section. Includes a mechanical verification table (pyproject → `pip install`; DB URL → `psycopg.connect` or SQLAlchemy `create_engine` per consumer; image tag → `docker pull`; GHA ref → resolves on github.com; framework keys → start the framework; entry points → `importlib.import_module`). Mandates PENDING-VERIFICATION marking when execution is impossible. Forbids reporting HANDOFF COMPLETE on unverified config strings. Includes "Why:" line citing Defect C and the failure of Rule 2 to prevent it.

### Deferred / Rejected Amendments

- **Do not amend `CLAUDE.md`.** The new rule is devops-specific in its trigger surface (config files devops-agent owns: pyproject, compose, .env.example, Dockerfiles, CI YAML). Other agents don't write the same artifact classes. The Cycle 1 dual-platform bullet in CLAUDE.md was correctly cross-cutting; this one is not. Adding it to CLAUDE.md would be process bloat and would dilute the existing dual-platform line.
- **Do not rewrite Rule 2.** It still anchors Defect A. Rule 3 layers enforcement on top of Rule 2's intent; deleting Rule 2 would remove the "no inventing" norm and leave only the verification gate, weakening the system.
- **Do not amend `docs/DEVELOPMENT_RULEBOOK.MD`.** Same reasoning as Cycle 1 — agent-behavior gap, narrower scope wins.
- **Do not introduce a pre-commit hook that runs `psycopg.connect` against compose URLs.** Requires a running database; cannot be made hermetic and cross-platform without significant tooling. The behavioral rule is sufficient if the agent obeys it; if Defect D appears despite Rule 3, revisit and consider a hook in CI specifically.
- **Do not file an amendment against efficiency-agent.md.** It is doing its job — caught the pattern, escalating now.

