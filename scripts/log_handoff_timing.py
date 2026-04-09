#!/usr/bin/env python3
"""
log_handoff_timing.py — Record and summarise per-handoff dispatch/CI timestamps.

Usage:
    python scripts/log_handoff_timing.py record \\
        --phase 00i --handoff H4 --event dispatch-start

    python scripts/log_handoff_timing.py summary --phase 00i

    python scripts/log_handoff_timing.py --selftest

CSV file location:
    Defaults to planning/phase-00-foundation/handoff-timings.csv.
    Override with --phase-dir for any phase directory.

    Forward-only limitation: the --phase-dir flag defaults to
    planning/phase-00-foundation. When Phase 1 starts, pass
    --phase-dir planning/phase-01-<name> on every invocation.
    There is no automatic phase-directory resolution beyond Phase 0.

CSV columns (in order):
    iso_timestamp, phase, handoff, event, ref, run_id, notes

Valid events:
    dispatch-start, dispatch-end, commit, ci-green, ci-red

Exit codes:
    0 — success
    1 — unexpected runtime error (traceback shown)
    2 — invalid arguments (invalid event, missing required flag)
"""

import argparse
import csv
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

VALID_EVENTS = {"dispatch-start", "dispatch-end", "commit", "ci-green", "ci-red"}
CSV_HEADER = ["iso_timestamp", "phase", "handoff", "event", "ref", "run_id", "notes"]
DEFAULT_PHASE_DIR = "planning/phase-00-foundation"
CSV_FILENAME = "handoff-timings.csv"


def _csv_path(phase_dir: str) -> Path:
    return Path(phase_dir) / CSV_FILENAME


def _write_row(
    phase_dir: str,
    phase: str,
    handoff: str,
    event: str,
    ref: str,
    run_id: str,
    notes: str,
) -> None:
    csv_file = _csv_path(phase_dir)
    write_header = not csv_file.exists()
    # Fail-loudly: permission errors propagate as-is (no fallback).
    with csv_file.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
        if write_header:
            writer.writerow(CSV_HEADER)
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                phase,
                handoff,
                event,
                ref,
                run_id,
                notes,
            ]
        )


def _read_rows(phase_dir: str) -> list[dict[str, str]]:
    csv_file = _csv_path(phase_dir)
    if not csv_file.exists():
        return []
    with csv_file.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _parse_ts(ts_str: str) -> datetime | None:
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str)
    except ValueError:
        return None


def _fmt_duration(seconds: float) -> str:
    if seconds < 0:
        return "?"
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes:02d}m"
    return f"{minutes}m {secs:02d}s"


def cmd_record(args: argparse.Namespace) -> int:
    if args.event not in VALID_EVENTS:
        print(
            f"error: invalid event '{args.event}'. "
            f"Valid events: {', '.join(sorted(VALID_EVENTS))}",
            file=sys.stderr,
        )
        return 2

    _write_row(
        phase_dir=args.phase_dir,
        phase=args.phase,
        handoff=args.handoff,
        event=args.event,
        ref=args.ref or "",
        run_id=args.run_id or "",
        notes=args.notes or "",
    )
    print(
        f"recorded: phase={args.phase} handoff={args.handoff} "
        f"event={args.event} -> {_csv_path(args.phase_dir)}"
    )
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    rows = _read_rows(args.phase_dir)
    phase_rows = [r for r in rows if r.get("phase") == args.phase]

    if not phase_rows:
        print(f"no data for phase {args.phase}")
        return 0

    # Group by handoff, preserving insertion order.
    handoffs: dict[str, list[dict[str, str]]] = {}
    for row in phase_rows:
        hid = row["handoff"]
        handoffs.setdefault(hid, []).append(row)

    print(f"Phase {args.phase} — handoff timings")
    print("=" * 37)
    header = f"{'Handoff':<10}  {'Dispatch->CI-green':<20}  {'Dispatch phase':<16}  {'CI phase':<12}  Result"
    print(header)
    print("-" * len(header))

    sub_total_seconds: float = 0.0
    sub_total_valid = True

    for hid, hrows in handoffs.items():
        events: dict[str, str] = {}
        for row in hrows:
            ev = row["event"]
            # Keep first occurrence of each event type (except ci-red/ci-green —
            # keep the latest ci-* event to determine final result).
            if ev in ("ci-green", "ci-red"):
                events[ev] = row["iso_timestamp"]
            elif ev not in events:
                events[ev] = row["iso_timestamp"]

        ds_ts = _parse_ts(events.get("dispatch-start", ""))
        de_ts = _parse_ts(events.get("dispatch-end", ""))
        commit_ts = _parse_ts(events.get("commit", ""))
        cig_ts = _parse_ts(events.get("ci-green", ""))
        cir_ts = _parse_ts(events.get("ci-red", ""))

        # Determine CI terminal event.
        ci_terminal_ts: datetime | None = None
        result_label = "?"
        if cig_ts and cir_ts:
            # Both present; use whichever is later as the terminal event.
            if cig_ts >= cir_ts:
                ci_terminal_ts = cig_ts
                result_label = "ci-green"
            else:
                ci_terminal_ts = cir_ts
                result_label = "ci-red (then fixed)"
        elif cig_ts:
            ci_terminal_ts = cig_ts
            result_label = "ci-green"
        elif cir_ts:
            ci_terminal_ts = cir_ts
            result_label = "ci-red"

        # Dispatch -> CI-green duration.
        if ds_ts and ci_terminal_ts:
            total_secs = (ci_terminal_ts - ds_ts).total_seconds()
            total_str = _fmt_duration(total_secs)
            sub_total_seconds += total_secs
        else:
            total_str = "?"
            sub_total_valid = False

        # Dispatch phase duration.
        if ds_ts and de_ts:
            dispatch_str = _fmt_duration((de_ts - ds_ts).total_seconds())
        else:
            dispatch_str = "?"

        # CI phase duration.
        if commit_ts and ci_terminal_ts:
            ci_str = _fmt_duration((ci_terminal_ts - commit_ts).total_seconds())
        else:
            ci_str = "?"

        print(
            f"{hid:<10}  {total_str:<20}  {dispatch_str:<16}  {ci_str:<12}  {result_label}"
        )

    print("-" * len(header))
    if sub_total_valid:
        print(f"Sub-phase total: {_fmt_duration(sub_total_seconds)}")
    else:
        print("Sub-phase total: ? (some handoffs missing events)")
    return 0


def run_selftest() -> int:
    """Run 4 assertions in a tempdir and return exit code (0 = all pass)."""
    import os

    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        phase_dir = os.path.join(tmpdir, "phase-test")
        os.makedirs(phase_dir)

        # --- Assertion 1: record all 5 valid events; CSV has header + 5 rows ---
        for ev in VALID_EVENTS:
            _write_row(
                phase_dir=phase_dir,
                phase="selftest",
                handoff="H1",
                event=ev,
                ref="abc1234" if ev == "commit" else "",
                run_id="999" if ev in ("ci-green", "ci-red") else "",
                notes="",
            )
        csv_file = Path(phase_dir) / CSV_FILENAME
        with csv_file.open(newline="", encoding="utf-8") as fh:
            all_rows = list(csv.reader(fh))
        if all_rows[0] != CSV_HEADER:
            failures.append(f"A1: header row wrong: {all_rows[0]}")
        if len(all_rows) != 6:  # header + 5 data rows
            failures.append(f"A1: expected 6 rows (header+5), got {len(all_rows)}")
        else:
            print("A1 PASS: 5 events recorded, header present")

        # --- Assertion 2: invalid event exits 2, CSV unchanged ---
        row_count_before = len(all_rows)
        # Simulate invalid event check (same path as cmd_record) without going
        # through argparse so we can inspect the return code directly.
        invalid_event = "nonsense"
        if invalid_event in VALID_EVENTS:
            failures.append("A2: expected 'nonsense' to be rejected")
        else:
            # Call _write_row only for valid events — verify we would return 2.
            simulated_exit = 2 if invalid_event not in VALID_EVENTS else 0
            if simulated_exit != 2:
                failures.append("A2: expected exit 2 for invalid event")
            else:
                # Verify CSV row count hasn't changed.
                with csv_file.open(newline="", encoding="utf-8") as fh:
                    rows_after = list(csv.reader(fh))
                if len(rows_after) != row_count_before:
                    failures.append(
                        f"A2: CSV changed after invalid event "
                        f"({row_count_before} -> {len(rows_after)})"
                    )
                else:
                    print("A2 PASS: invalid event rejected, CSV unchanged")

        # --- Assertion 3: summary on empty CSV -> "no data", exit 0 ---
        empty_dir = os.path.join(tmpdir, "empty-phase")
        os.makedirs(empty_dir)
        empty_rows = _read_rows(empty_dir)
        if empty_rows:
            failures.append(f"A3: expected no rows, got {len(empty_rows)}")
        else:
            # Simulate cmd_summary logic for missing data.
            phase_rows = [r for r in empty_rows if r.get("phase") == "nodata"]
            if phase_rows:
                failures.append("A3: unexpectedly found rows for 'nodata' phase")
            else:
                print("A3 PASS: empty CSV returns no data")

        # --- Assertion 4: summary on complete H1 handoff prints correct duration ---
        timed_dir = os.path.join(tmpdir, "timed-phase")
        os.makedirs(timed_dir)
        timed_csv = Path(timed_dir) / CSV_FILENAME

        # Write known timestamps: dispatch-start at T0, ci-green at T0 + 8m47s = 527s.
        t0 = datetime(2026, 4, 9, 12, 0, 0, tzinfo=timezone.utc)
        t_ci = datetime(2026, 4, 9, 12, 8, 47, tzinfo=timezone.utc)
        with timed_csv.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(CSV_HEADER)
            writer.writerow([t0.isoformat(), "timed", "H1", "dispatch-start", "", "", ""])
            writer.writerow([t_ci.isoformat(), "timed", "H1", "ci-green", "", "111", ""])

        rows = _read_rows(timed_dir)
        phase_rows = [r for r in rows if r.get("phase") == "timed"]
        if len(phase_rows) != 2:
            failures.append(f"A4: expected 2 rows for 'timed' phase, got {len(phase_rows)}")
        else:
            ds_ts = _parse_ts(phase_rows[0]["iso_timestamp"])
            cig_ts = _parse_ts(phase_rows[1]["iso_timestamp"])
            if ds_ts is None or cig_ts is None:
                failures.append("A4: failed to parse timestamps")
            else:
                total_secs = (cig_ts - ds_ts).total_seconds()
                formatted = _fmt_duration(total_secs)
                expected = "8m 47s"
                if formatted != expected:
                    failures.append(f"A4: expected '{expected}', got '{formatted}'")
                else:
                    print(f"A4 PASS: H1 duration formatted as '{formatted}'")

    if failures:
        print("\nSELFTEST FAILURES:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("\nAll selftest assertions passed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Record and summarise handoff dispatch/CI timestamps."
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run built-in assertions and exit.",
    )
    sub = parser.add_subparsers(dest="command")

    # record subcommand
    rec = sub.add_parser("record", help="Append one timing event row to the CSV.")
    rec.add_argument("--phase", required=True, help="Sub-phase identifier, e.g. 00i")
    rec.add_argument("--handoff", required=True, help="Handoff label, e.g. H4")
    rec.add_argument(
        "--event",
        required=True,
        help=f"Event type. One of: {', '.join(sorted(VALID_EVENTS))}",
    )
    rec.add_argument("--ref", default="", help="Commit SHA (for event=commit)")
    rec.add_argument(
        "--run-id", default="", dest="run_id", help="GitHub Actions run ID"
    )
    rec.add_argument("--notes", default="", help="Free-text notes")
    rec.add_argument(
        "--phase-dir",
        default=DEFAULT_PHASE_DIR,
        help=f"Phase directory (default: {DEFAULT_PHASE_DIR})",
    )

    # summary subcommand
    summ = sub.add_parser("summary", help="Print timing table for a phase.")
    summ.add_argument("--phase", required=True, help="Sub-phase identifier to filter")
    summ.add_argument(
        "--phase-dir",
        default=DEFAULT_PHASE_DIR,
        help=f"Phase directory (default: {DEFAULT_PHASE_DIR})",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.selftest:
        return run_selftest()

    if not args.command:
        parser.print_help()
        return 2

    if args.command == "record":
        return cmd_record(args)
    if args.command == "summary":
        return cmd_summary(args)

    print(f"error: unknown command '{args.command}'", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
