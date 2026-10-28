from __future__ import annotations

import argparse
import csv
import json
import random
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "src" / "schema.sql"
TRIGGERS_PATH = ROOT / "src" / "workflow_triggers.sql"
OUTPUT_DIR = ROOT / "outputs"
DEFAULT_SEED = 20261022
YEAR = 2026


def timestamp(day_offset: int, hour: int = 12) -> str:
    base = datetime(YEAR, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
    return (base + timedelta(days=day_offset)).isoformat()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def export_table(connection: sqlite3.Connection, table: str) -> int:
    rows = [
        dict(row)
        for row in connection.execute(f'SELECT * FROM "{table}" ORDER BY 1')
    ]
    write_csv(OUTPUT_DIR / f"{table}.csv", rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate reproducible synthetic academic-integrity data."
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--submissions", type=int, default=10000)
    parser.add_argument("--flags", type=int, default=1000)
    parser.add_argument("--cases", type=int, default=300)
    args = parser.parse_args()

    if args.submissions < 1:
        raise SystemExit("--submissions must be at least 1.")
    if not 0 <= args.cases <= args.flags <= args.submissions:
        raise SystemExit("Require 0 <= cases <= flags <= submissions.")

    rng = random.Random(args.seed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    database_path = OUTPUT_DIR / "integrity_cases.db"
    if database_path.exists():
        database_path.unlink()

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        connection.executescript(
            SCHEMA_PATH.read_text(encoding="utf-8-sig")
        )
        connection.executescript(
            TRIGGERS_PATH.read_text(encoding="utf-8-sig")
        )

        # Parent/master records first.
        learners = []
        for i in range(1, args.submissions + 1):
            learners.append((
                i, f"LRN-{i:06d}", f"COHORT-{2024 + (i % 3)}",
                timestamp(i % 300), 1
            ))

        connection.executemany(
            """INSERT INTO learner
               (learner_id, learner_ref, cohort, created_at, is_active)
               VALUES (?, ?, ?, ?, ?)""",
            learners,
        )

        connection.executemany(
            """INSERT INTO assessment
               (assessment_id, assessment_ref, title, assessment_type,
                opens_at, closes_at, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    i, f"ASM-{i:04d}", f"Assessment {i}",
                    "coursework" if i % 2 else "exam",
                    timestamp(1), timestamp(365), timestamp(0)
                )
                for i in range(1, 11)
            ],
        )

        connection.execute(
            """INSERT INTO integrity_rule
               (integrity_rule_id, rule_ref, rule_version, threshold,
                effective_from, effective_to, rule_description)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                1, "SIMILARITY-THRESHOLD", "1.0", 70.0,
                timestamp(0), None,
                "Scores at or above 70 trigger human review; they do not establish guilt."
            ),
        )

        reviewer_roles = [
            "instructor",
            "academic_administrator",
            "support_staff",
            "platform_administrator",
        ]
        connection.executemany(
            """INSERT INTO reviewer
               (reviewer_id, reviewer_ref, role, is_active, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            [
                (i, f"REV-{i:04d}", reviewer_roles[(i - 1) % 4], 1, timestamp(0))
                for i in range(1, 21)
            ],
        )

        # Operational submissions and reports.
        # Labels are held only in memory here and exported separately below.
        ground_truth = []
        submission_rows = []
        report_rows = []

        for i in range(1, args.submissions + 1):
            is_flagged = i <= args.flags

            if is_flagged:
                score = round(rng.uniform(70.0, 99.9), 2)
                category = [
                    "suspected_breach",
                    "legitimate_quotation",
                    "shared_template",
                    "false_positive",
                ][(i - 1) % 4]
            else:
                score = round(rng.uniform(0.0, 69.99), 2)
                category = "unflagged"

            submission_ref = f"SUB-{YEAR}-{i:06d}"
            report_ref = f"SIM-{submission_ref}-01"
            assessment_id = ((i - 1) % 10) + 1
            learner_id = i

            submission_rows.append((
                i, submission_ref, learner_id, assessment_id,
                timestamp(i % 300, 10 + (i % 10)),
                f"sha256-synthetic-{i:08d}", "submitted"
            ))

            report_rows.append((
                i, report_ref, i, 1, score, timestamp(i % 300, 14),
                "flagged" if is_flagged else "not_flagged",
                f"SYNTHETIC-REF-{i:06d}"
            ))

            ground_truth.append({
                "submission_ref": submission_ref,
                "issue_type": category,
                "ground_truth_label": (
                    "potential_breach" if category == "suspected_breach"
                    else "legitimate_or_false_positive"
                    if category in {"legitimate_quotation", "shared_template", "false_positive"}
                    else "no_flag_expected"
                ),
                "expected_review": (
                    "human_review_required" if is_flagged else "no_review_triggered"
                ),
            })

        connection.executemany(
            """INSERT INTO submission
               (submission_id, submission_ref, learner_id, assessment_id,
                submitted_at, content_hash, submission_status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            submission_rows,
        )

        connection.executemany(
            """INSERT INTO similarity_report
               (similarity_report_id, report_ref, submission_id,
                integrity_rule_id, similarity_score, generated_at,
                flag_status, evidence_reference)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            report_rows,
        )

        # Cases and review workflow. Every case gets an eligible reviewer,
        # evidence, a reasoned decision, and an audit trail.
        decisions = []
        appeals = []
        appeal_reviews = []
        assignments = []
        conflicts = []
        evidence = []
        audit_events = []
        case_rows = []

        appeal_count = min(args.cases // 5, args.cases)

        for i in range(1, args.cases + 1):
            submission_id = i
            case_ref = f"INT-{YEAR}-{i:06d}"
            reviewer_id = ((i - 1) % 20) + 1
            score = report_rows[i - 1][4]
            category = ground_truth[i - 1]["issue_type"]

            case_rows.append((
                i, case_ref, submission_id, i,
                timestamp(i % 300, 15),
                "decision_recorded",
                "high" if score >= 90 else "normal"
            ))

            # Some conflicts are explicitly recorded and resolved by recusal.
            if i % 10 == 0:
                conflicts.append((
                    len(conflicts) + 1, i, reviewer_id,
                    "prior_relationship", timestamp(i % 300, 15),
                    "recused", "Reviewer recused; reassigned to an eligible reviewer."
                ))
                reviewer_id = (reviewer_id % 20) + 1

            assignments.append((
                len(assignments) + 1, i, reviewer_id,
                timestamp(i % 300, 15), None, "Initial eligible reviewer assignment"
            ))

            evidence_type = (
                "quotation_context" if category == "legitimate_quotation"
                else "template_comparison" if category == "shared_template"
                else "similarity_excerpt"
            )
            evidence_id = len(evidence) + 1
            evidence.append((
                evidence_id, f"EVD-{case_ref}-001", i, evidence_type,
                f"SYNTHETIC-REF-{i:06d}",
                "Synthetic evidence reference; inspect context before deciding.",
                timestamp(i % 300, 16), reviewer_id
            ))

            if category == "suspected_breach" and score >= 85:
                decision_type = "breach_found"
                rationale = (
                    "High similarity score and reviewed synthetic evidence support "
                    "a breach finding under the documented rule."
                )
            elif category in {"legitimate_quotation", "shared_template", "false_positive"}:
                decision_type = "no_breach"
                rationale = (
                    "Review of synthetic context indicates that similarity alone "
                    "does not establish a breach."
                )
            else:
                decision_type = "inconclusive"
                rationale = (
                    "The available synthetic evidence is insufficient for a "
                    "confident finding; no automatic guilt inference was made."
                )

            decision_id = i
            decisions.append((
                decision_id, i, reviewer_id, decision_type, rationale,
                timestamp(i % 300, 17), 1
            ))

            audit_events.extend([
                (
                    len(audit_events) + 1, i, "case_opened", "system", None,
                    timestamp(i % 300, 15), None, "open",
                    "Case created from a flagged similarity report."
                ),
                (
                    len(audit_events) + 2, i, "reviewer_assigned", "system", None,
                    timestamp(i % 300, 15), "open", "assigned",
                    f"Assigned to reviewer {reviewer_id}."
                ),
                (
                    len(audit_events) + 3, i, "review_started", "reviewer",
                    reviewer_id, timestamp(i % 300, 15), "assigned",
                    "under_review", "Human review started."
                ),
                (
                    len(audit_events) + 4, i, "evidence_added", "reviewer",
                    reviewer_id, timestamp(i % 300, 16), None, None,
                    "Synthetic evidence added before the decision."
                ),
                (
                    len(audit_events) + 5, i, "decision_recorded", "reviewer",
                    reviewer_id, timestamp(i % 300, 17), "under_review",
                    "decision_recorded", decision_type
                ),
            ])

            if i <= appeal_count:
                appeal_id = i
                appeal_ref = f"APL-{case_ref}-01"
                appeals.append((
                    appeal_id, appeal_ref, i, decision_id,
                    "Request for independent review of the original decision.",
                    timestamp((i % 300) + 1, 10),
                    "under_independent_review",
                    None
                ))

                independent_reviewer = (reviewer_id % 20) + 1
                appeal_reviews.append((
                    appeal_id, appeal_id, independent_reviewer,
                    "Independent review completed without relying solely on the similarity score.",
                    "upheld", timestamp((i % 300) + 2, 10)
                ))

                audit_events.extend([
                    (
                        len(audit_events) + 1, i, "appeal_submitted", "system", None,
                        timestamp((i % 300) + 1, 10),
                        "decision_recorded", "appealed",
                        "Appeal submitted after the original decision."
                    ),
                    (
                        len(audit_events) + 2, i, "independent_review_completed",
                        "reviewer", independent_reviewer,
                        timestamp((i % 300) + 2, 10),
                        "appealed", "closed",
                        "Independent reviewer completed appeal review."
                    ),
                ])

        connection.executemany(
            """INSERT INTO case_record
               (case_id, case_ref, submission_id, similarity_report_id,
                opened_at, case_status, priority)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            case_rows,
        )

        # Apply legal case lifecycle transitions for cases with appeals.
        # Each UPDATE is checked by the database lifecycle trigger.
        for case_id in range(1, appeal_count + 1):
            connection.execute(
                "UPDATE case_record SET case_status = 'appealed' "
                "WHERE case_id = ? AND case_status = 'decision_recorded'",
                (case_id,),
            )
            connection.execute(
                "UPDATE case_record "
                "SET case_status = 'under_independent_review' "
                "WHERE case_id = ? AND case_status = 'appealed'",
                (case_id,),
            )
            connection.execute(
                "UPDATE case_record SET case_status = 'closed' "
                "WHERE case_id = ? "
                "AND case_status = 'under_independent_review'",
                (case_id,),
            )

        connection.executemany(
            """INSERT INTO reviewer_assignment
               (assignment_id, case_id, reviewer_id, assigned_at,
                unassigned_at, assignment_reason)
               VALUES (?, ?, ?, ?, ?, ?)""",
            assignments,
        )

        connection.executemany(
            """INSERT INTO reviewer_conflict
               (conflict_id, case_id, reviewer_id, conflict_type, declared_at,
                resolution_status, resolution_note)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            conflicts,
        )

        connection.executemany(
            """INSERT INTO evidence_item
               (evidence_item_id, evidence_ref, case_id, evidence_type,
                source_reference, description, added_at, added_by_reviewer_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            evidence,
        )

        connection.executemany(
            """INSERT INTO decision
               (decision_id, case_id, reviewer_id, decision_type,
                rationale, decided_at, integrity_rule_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            decisions,
        )

        connection.executemany(
            """INSERT INTO appeal
               (appeal_id, appeal_ref, case_id, original_decision_id,
                grounds, submitted_at, appeal_status, outcome)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            appeals,
        )

        connection.executemany(
            """INSERT INTO appeal_review
               (appeal_review_id, appeal_id, reviewer_id, review_rationale,
                review_outcome, reviewed_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            appeal_reviews,
        )

        connection.execute(
            """UPDATE appeal
               SET appeal_status = 'closed',
                   outcome = 'Independent review completed; original decision upheld.'
               WHERE appeal_status = 'under_independent_review'"""
        )

        connection.executemany(
            """INSERT INTO audit_event
               (event_id, case_id, event_type, actor_type, actor_id,
                occurred_at, previous_state, new_state, event_details)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            audit_events,
        )

        connection.commit()

        # Operational exports contain no ground-truth or issue labels.
        counts = {}
        tables = [
            "learner", "assessment", "integrity_rule", "submission",
            "similarity_report", "reviewer", "case_record",
            "reviewer_assignment", "reviewer_conflict", "evidence_item",
            "decision", "appeal", "appeal_review", "audit_event",
        ]
        for table in tables:
            counts[table] = export_table(connection, table)

        write_csv(OUTPUT_DIR / "ground_truth.csv", ground_truth)
        with (OUTPUT_DIR / "ground_truth.json").open("w", encoding="utf-8") as file:
            json.dump(ground_truth, file, indent=2)

        validation = {
            "seed": args.seed,
            "submissions_requested": args.submissions,
            "flags_requested": args.flags,
            "cases_requested": args.cases,
            "submission_count": counts["submission"],
            "flagged_report_count": connection.execute(
                "SELECT COUNT(*) FROM similarity_report WHERE flag_status = 'flagged'"
            ).fetchone()[0],
            "case_count": counts["case_record"],
            "appeal_count": counts["appeal"],
            "foreign_key_violations": len(
                connection.execute("PRAGMA foreign_key_check").fetchall()
            ),
            "table_counts": counts,
        }

        with (OUTPUT_DIR / "validation_summary.json").open("w", encoding="utf-8") as file:
            json.dump(validation, file, indent=2)

        if validation["submission_count"] != args.submissions:
            raise RuntimeError("Submission count does not match requested scale.")
        if validation["flagged_report_count"] != args.flags:
            raise RuntimeError("Flagged report count does not match requested scale.")
        if validation["case_count"] != args.cases:
            raise RuntimeError("Case count does not match requested scale.")
        if validation["foreign_key_violations"] != 0:
            raise RuntimeError("Foreign-key violations detected.")

        print("PASS: Synthetic dataset generated.")
        print(f"Seed: {args.seed}")
        print(f"Submissions: {validation['submission_count']}")
        print(f"Flagged reports: {validation['flagged_report_count']}")
        print(f"Cases: {validation['case_count']}")
        print(f"Appeals: {validation['appeal_count']}")
        print("Foreign-key violations: 0")
        print(f"Outputs: {OUTPUT_DIR}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
