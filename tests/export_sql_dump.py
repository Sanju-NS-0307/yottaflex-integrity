import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "outputs" / "integrity_cases.db"
OUTPUT = ROOT / "outputs" / "integrity_cases_dump.sql"


def table_counts(connection):
    tables = connection.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    return {
        table: connection.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        ).fetchone()[0]
        for (table,) in tables
    }


def main():
    if not DATABASE.exists():
        raise SystemExit(f"ERROR: Database not found: {DATABASE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE) as source:
        sql_dump = "\n".join(source.iterdump()) + "\n"
        expected_counts = table_counts(source)

    OUTPUT.write_text(sql_dump, encoding="utf-8")
    print(f"PASS: SQL dump written to {OUTPUT}")

    # Restore into a fresh database. The dump contains its own schema,
    # data, indexes, and triggers. Disable FK checks during import, then
    # explicitly validate referential integrity after restoring.
    with sqlite3.connect(":memory:") as restored:
        restored.execute("PRAGMA foreign_keys = OFF")
        restored.executescript(sql_dump)
        restored.execute("PRAGMA foreign_keys = ON")

        actual_counts = table_counts(restored)
        violations = restored.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if actual_counts != expected_counts:
            raise SystemExit(
                "ERROR: Restored table counts differ from source.\n"
                f"Source:   {expected_counts}\n"
                f"Restored: {actual_counts}"
            )

        if violations:
            raise SystemExit(
                f"ERROR: Restored database has FK violations: {violations[:10]}"
            )

        integrity = restored.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise SystemExit(f"ERROR: SQLite integrity check failed: {integrity}")

        print(f"PASS: All {len(actual_counts)} table counts match.")
        print("PASS: Restored database has zero foreign-key violations.")
        print("PASS: SQLite integrity_check returned ok.")

    print("PASS: SQL export and restore verification completed.")


if __name__ == "__main__":
    main()