import sqlite3
from pathlib import Path

schema_path = Path("src/schema.sql")
schema = schema_path.read_text(encoding="utf-8-sig")

connection = sqlite3.connect(":memory:")
connection.execute("PRAGMA foreign_keys = ON")

try:
    connection.executescript(schema)

    tables = {
        row[0]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }

    required_tables = {
        "learner",
        "assessment",
        "submission",
        "similarity_report",
        "integrity_rule",
        "case_record",
        "evidence_item",
        "reviewer",
        "decision",
        "appeal",
    }

    supporting_tables = {
        "reviewer_assignment",
        "reviewer_conflict",
        "appeal_review",
        "audit_event",
    }

    missing = (required_tables | supporting_tables) - tables

    if missing:
        raise RuntimeError(f"Missing tables: {sorted(missing)}")

    foreign_keys_enabled = connection.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    if foreign_keys_enabled != 1:
        raise RuntimeError("Foreign-key enforcement is disabled")

    print("PASS: SQL schema executed successfully.")
    print(f"PASS: {len(required_tables)} required entities found.")
    print(f"PASS: {len(supporting_tables)} supporting tables found.")
    print("PASS: Foreign-key enforcement is enabled.")
    print("PASS: Schema smoke test completed.")

finally:
    connection.close()
