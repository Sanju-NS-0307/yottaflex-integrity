import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "outputs" / "integrity_cases.db"

connection = sqlite3.connect(DB)
connection.execute("PRAGMA foreign_keys = ON")

def expect_rejected(name, setup, statement, params, expected_message):
    connection.execute("SAVEPOINT workflow_test")
    try:
        for sql, values in setup:
            connection.execute(sql, values)

        try:
            connection.execute(statement, params)
        except sqlite3.DatabaseError as exc:
            if expected_message not in str(exc):
                raise AssertionError(
                    f"{name}: unexpected database error: {exc}"
                ) from exc
            print(f"PASS: {name}")
        else:
            raise AssertionError(
                f"FAIL: {name} was accepted but should have been rejected"
            )
    finally:
        connection.execute("ROLLBACK TO workflow_test")
        connection.execute("RELEASE workflow_test")


try:
    next_case = connection.execute(
        "SELECT MAX(case_id) + 1 FROM case_record"
    ).fetchone()[0]

    expect_rejected(
        "Case cannot reference another submission's report",
        [],
        """INSERT INTO case_record
           (case_id, case_ref, submission_id, similarity_report_id,
            opened_at, case_status, priority)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (next_case, "TEST-MISMATCH", 1, 2,
         "2026-10-28T10:00:00+00:00", "open", "normal"),
        "Case submission must match report submission",
    )

    reviewer_id = 1
    conflict_id = connection.execute(
        "SELECT MAX(conflict_id) + 1 FROM reviewer_conflict"
    ).fetchone()[0]
    assignment_id = connection.execute(
        "SELECT MAX(assignment_id) + 1 FROM reviewer_assignment"
    ).fetchone()[0]

    expect_rejected(
        "Conflicted reviewer cannot be assigned",
        [
            (
                """INSERT INTO reviewer_conflict
                   (conflict_id, case_id, reviewer_id, conflict_type,
                    declared_at, resolution_status, resolution_note)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (conflict_id, 299, reviewer_id, "test_conflict",
                 "2026-10-28T10:00:00+00:00", "unresolved", "Test only"),
            ),
        ],
        """INSERT INTO reviewer_assignment
           (assignment_id, case_id, reviewer_id, assigned_at,
            unassigned_at, assignment_reason)
           VALUES (?, ?, ?, ?, NULL, ?)""",
        (assignment_id, 299, reviewer_id,
         "2026-10-28T10:01:00+00:00", "Test assignment"),
        "Conflicted reviewer cannot be assigned",
    )

    conflict_id = connection.execute(
        "SELECT MAX(conflict_id) + 1 FROM reviewer_conflict"
    ).fetchone()[0]
    decision_id = connection.execute(
        "SELECT MAX(decision_id) + 1 FROM decision"
    ).fetchone()[0]

    expect_rejected(
        "Conflicted reviewer cannot record a decision",
        [
            (
                """INSERT INTO reviewer_conflict
                   (conflict_id, case_id, reviewer_id, conflict_type,
                    declared_at, resolution_status, resolution_note)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (conflict_id, 299, reviewer_id, "test_conflict",
                 "2026-10-28T10:00:00+00:00", "unresolved", "Test only"),
            ),
        ],
        """INSERT INTO decision
           (decision_id, case_id, reviewer_id, decision_type,
            rationale, decided_at, integrity_rule_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (decision_id, 299, reviewer_id, "no_breach",
         "Test decision", "2026-10-28T10:02:00+00:00", 1),
        "Conflicted reviewer cannot record a decision",
    )

    appeal_id = connection.execute(
        "SELECT MAX(appeal_id) + 1 FROM appeal"
    ).fetchone()[0]

    expect_rejected(
        "Appeal cannot close before independent review",
        [
            (
                """INSERT INTO appeal
                   (appeal_id, appeal_ref, case_id, original_decision_id,
                    grounds, submitted_at, appeal_status, outcome)
                   VALUES (?, ?, ?, ?, ?, ?, ?, NULL)""",
                (appeal_id, "TEST-APPEAL", 299, 299,
                 "Test appeal", "2026-10-28T10:00:00+00:00",
                 "under_independent_review"),
            ),
        ],
        "UPDATE appeal SET appeal_status = 'closed' WHERE appeal_id = ?",
        (appeal_id,),
        "Appeal requires independent review before completion",
    )

    original_reviewer = connection.execute(
        "SELECT reviewer_id FROM decision WHERE decision_id = 1"
    ).fetchone()[0]
    review_id = connection.execute(
        "SELECT MAX(appeal_review_id) + 1 FROM appeal_review"
    ).fetchone()[0]

    expect_rejected(
        "Original decision-maker cannot review their own appeal",
        [],
        """INSERT INTO appeal_review
           (appeal_review_id, appeal_id, reviewer_id, review_rationale,
            review_outcome, reviewed_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (review_id, 1, original_reviewer, "Test review", "upheld",
         "2026-10-28T10:00:00+00:00"),
        "Appeal reviewer must differ from original reviewer",
    )

    evidence_id = connection.execute(
        "SELECT MAX(evidence_item_id) + 1 FROM evidence_item"
    ).fetchone()[0]

    expect_rejected(
        "Post-decision evidence requires an audit event",
        [],
        """INSERT INTO evidence_item
           (evidence_item_id, evidence_ref, case_id, evidence_type,
            source_reference, description, added_at, added_by_reviewer_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (evidence_id, "TEST-EVIDENCE", 299, "test",
         "TEST-REF", "Test evidence",
         "2099-01-01T00:00:00+00:00", None),
        "Post-decision evidence requires a matching audit event",
    )

    event_id = connection.execute(
        "SELECT MIN(event_id) FROM audit_event"
    ).fetchone()[0]

    expect_rejected(
        "Audit events cannot be edited",
        [],
        "UPDATE audit_event SET event_details = 'tampered' WHERE event_id = ?",
        (event_id,),
        "Audit events cannot be updated",
    )

    expect_rejected(
        "Audit events cannot be deleted",
        [],
        "DELETE FROM audit_event WHERE event_id = ?",
        (event_id,),
        "Audit events cannot be deleted",
    )

    expect_rejected(
        "Invalid case lifecycle transition is blocked",
        [],
        "UPDATE case_record SET case_status = 'open' WHERE case_id = 100",
        (),
        "Invalid case lifecycle transition",
    )

    print("\nAll workflow rejection tests passed.")

finally:
    connection.close()
