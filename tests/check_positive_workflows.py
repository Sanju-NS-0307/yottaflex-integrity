import sqlite3
from pathlib import Path

db_path = Path("outputs/integrity_cases.db")
if not db_path.exists():
    raise SystemExit(f"FAIL: Database not found: {db_path}")

db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row
db.execute("PRAGMA foreign_keys = ON")

checks = [
    (
        "Appealed cases are closed",
        """
        SELECT COUNT(*) FROM case_record c
        JOIN appeal a ON a.case_id = c.case_id
        WHERE c.case_status = 'closed'
          AND a.appeal_status = 'closed'
        """,
        60,
    ),
    (
        "Non-appealed cases remain decision_recorded",
        """
        SELECT COUNT(*) FROM case_record c
        WHERE c.case_status = 'decision_recorded'
          AND NOT EXISTS (
              SELECT 1 FROM appeal a WHERE a.case_id = c.case_id
          )
        """,
        240,
    ),
    (
        "Closed appeals have an independent review",
        """
        SELECT COUNT(*) FROM appeal a
        JOIN decision d ON d.decision_id = a.original_decision_id
        JOIN appeal_review ar ON ar.appeal_id = a.appeal_id
        WHERE a.appeal_status = 'closed'
          AND ar.reviewer_id <> d.reviewer_id
        """,
        60,
    ),
    (
        "Closed appeals have outcomes",
        """
        SELECT COUNT(*) FROM appeal
        WHERE appeal_status = 'closed'
          AND outcome IS NOT NULL
          AND TRIM(outcome) <> ''
        """,
        60,
    ),
]

failed = False
for label, query, expected in checks:
    actual = db.execute(query).fetchone()[0]
    if actual == expected:
        print(f"PASS: {label} ({actual})")
    else:
        print(f"FAIL: {label}; expected {expected}, found {actual}")
        failed = True

db.close()
if failed:
    raise SystemExit(1)

print("PASS: All successful-workflow checks passed.")
