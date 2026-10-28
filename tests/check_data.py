import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "outputs" / "integrity_cases.db"
OUT = ROOT / "outputs"

def check(condition, message):
    if not condition:
        raise AssertionError(f"FAIL: {message}")
    print(f"PASS: {message}")

connection = sqlite3.connect(DB)
connection.row_factory = sqlite3.Row
connection.execute("PRAGMA foreign_keys = ON")

try:
    # Baseline record counts.
    expected = {
        "submission": 10000,
        "similarity_report": 10000,
        "case_record": 300,
        "appeal": 60,
    }
    for table, expected_count in expected.items():
        actual = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        check(actual == expected_count,
              f"{table}: expected {expected_count}, found {actual}")

    flagged = connection.execute(
        "SELECT COUNT(*) FROM similarity_report WHERE flag_status = 'flagged'"
    ).fetchone()[0]
    check(flagged == 1000, "Exactly 1,000 similarity reports are flagged")

    fk_violations = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()
    check(not fk_violations, "No foreign-key violations")

    # Verify every case links a report to the same submission.
    mismatched_cases = connection.execute("""
        SELECT COUNT(*)
        FROM case_record c
        JOIN similarity_report r
          ON r.similarity_report_id = c.similarity_report_id
        WHERE c.submission_id <> r.submission_id
    """).fetchone()[0]
    check(mismatched_cases == 0,
          "Every case and its similarity report reference the same submission")

    # Audit event primary keys must be unique and every case must have history.
    event_count, distinct_event_ids = connection.execute("""
        SELECT COUNT(*), COUNT(DISTINCT event_id) FROM audit_event
    """).fetchone()
    check(event_count == distinct_event_ids,
          "Audit event IDs are unique")

    cases_without_events = connection.execute("""
        SELECT COUNT(*)
        FROM case_record c
        WHERE NOT EXISTS (
            SELECT 1 FROM audit_event e WHERE e.case_id = c.case_id
        )
    """).fetchone()[0]
    check(cases_without_events == 0,
          "Every case has an audit trail")

    # Each appeal must have an independent review by a different reviewer.
    invalid_appeals = connection.execute("""
        SELECT COUNT(*)
        FROM appeal a
        JOIN decision d ON d.decision_id = a.original_decision_id
        WHERE a.appeal_status IN ('closed', 'upheld', 'overturned', 'partially_upheld')
          AND NOT EXISTS (
              SELECT 1
              FROM appeal_review ar
              WHERE ar.appeal_id = a.appeal_id
                AND ar.reviewer_id <> d.reviewer_id
          )
    """).fetchone()[0]
    check(invalid_appeals == 0,
          "Every completed appeal has a different reviewing reviewer")

    # Operational submission CSV must not expose ground-truth labels.
    submission_csv = OUT / "submission.csv"
    with submission_csv.open(newline="", encoding="utf-8") as file:
        headers = next(csv.reader(file))
    check(
        "ground_truth_label" not in headers and "issue_type" not in headers,
        "Submission export does not expose ground-truth labels",
    )

    truth_csv = OUT / "ground_truth.csv"
    check(truth_csv.exists(), "Separate ground_truth.csv exists")

    print("\nAll current data-integrity checks passed.")

finally:
    connection.close()
