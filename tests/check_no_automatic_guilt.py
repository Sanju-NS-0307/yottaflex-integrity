import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "outputs" / "integrity_cases.db"

connection = sqlite3.connect(DB)
connection.execute("PRAGMA foreign_keys = ON")

try:
    connection.execute("SAVEPOINT no_automatic_guilt")

    report_id = connection.execute(
        "SELECT COALESCE(MAX(similarity_report_id), 0) + 1 "
        "FROM similarity_report"
    ).fetchone()[0]

    connection.execute(
        """
        INSERT INTO similarity_report (
            similarity_report_id, report_ref, submission_id,
            integrity_rule_id, similarity_score, generated_at,
            flag_status, evidence_reference
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            report_id,
            "TEST-NO-AUTO-GUILT",
            1,
            1,
            99.0,
            "2026-10-29T12:00:00+00:00",
            "flagged",
            "TEST-EVIDENCE",
        ),
    )

    case_count = connection.execute(
        "SELECT COUNT(*) FROM case_record WHERE similarity_report_id = ?",
        (report_id,),
    ).fetchone()[0]

    assert case_count == 0, (
        "FAIL: a flagged report automatically created a case"
    )

    decision_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM decision d
        JOIN case_record c ON c.case_id = d.case_id
        WHERE c.similarity_report_id = ?
        """,
        (report_id,),
    ).fetchone()[0]

    assert decision_count == 0, (
        "FAIL: a flagged report automatically resulted in a decision"
    )

    print("PASS: a similarity flag alone creates no case or decision.")

finally:
    connection.execute("ROLLBACK TO no_automatic_guilt")
    connection.execute("RELEASE no_automatic_guilt")
    connection.close()
