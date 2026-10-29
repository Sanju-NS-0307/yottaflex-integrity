import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "src" / "schema.sql"
OUTPUT = ROOT / "docs" / "DATA_DICTIONARY.md"


def main():
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA.read_text(encoding="utf-8-sig"))

    tables = db.execute("""
        SELECT name, sql
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    lines = [
        "# Data Dictionary",
        "",
        "Generated from `src/schema.sql`.",
        "",
        "This document describes the implemented SQLite schema. "
        "Business meanings and lifecycle rules are documented separately "
        "in `DATA_MODEL.md` and `src/workflow_triggers.sql`.",
        "",
    ]

    for table, create_sql in tables:
        lines.extend([f"## `{table}`", ""])

        columns = db.execute(
            f'PRAGMA table_info("{table}")'
        ).fetchall()

        foreign_keys = db.execute(
            f'PRAGMA foreign_key_list("{table}")'
        ).fetchall()

        indexes = db.execute(
            f'PRAGMA index_list("{table}")'
        ).fetchall()

        unique_constraints = []
        for index in indexes:
            if index[2]:
                index_name = index[1].replace('"', '""')
                index_columns = db.execute(
                    f'PRAGMA index_info("{index_name}")'
                ).fetchall()

                names = [item[2] for item in index_columns]
                if names:
                    unique_constraints.append(names)

        lines.extend([
            "| Column | SQLite type | Required? | Key / uniqueness | "
            "Default | References |",
            "|---|---|---|---|---|---|",
        ])

        for col in columns:
            cid, name, col_type, not_null, default, pk = col
            required = "Yes" if not_null or pk else "No"
            key_parts = []

            if pk:
                key_parts.append("Primary key")

            if [name] in unique_constraints:
                key_parts.append("Unique (single-column)")

            key = ", ".join(key_parts) if key_parts else "—"

            fk_targets = [
                f"{fk[2]}.{fk[4]}"
                for fk in foreign_keys
                if fk[3] == name
            ]
            reference = ", ".join(fk_targets) if fk_targets else "—"
            default_text = str(default) if default is not None else "—"

            lines.append(
                f"| `{name}` | `{col_type or 'unspecified'}` | "
                f"{required} | {key} | `{default_text}` | {reference} |"
            )

        lines.extend(["", "**Declared SQL constraints**", ""])
        lines.append("```sql")
        lines.append(create_sql)
        lines.append("```")
        lines.append("")

        composite_constraints = [
            names for names in unique_constraints if len(names) > 1
        ]
        if composite_constraints:
            lines.extend(["**Composite unique constraints**", ""])
            for names in composite_constraints:
                columns_text = ", ".join(f"`{name}`" for name in names)
                lines.append(f"- Together, {columns_text} must be unique.")
            lines.append("")

    lines.extend([
        "## Interpretation notes",
        "",
        "- Similarity scores are percentages on a 0–100 scale.",
        "- Boolean-like fields use SQLite integers constrained to 0 or 1.",
        "- Timestamps are stored as ISO-formatted text; the schema does not "
        "enforce a timezone format.",
        "- Enumerated values and range constraints are shown in each table's "
        "SQL definition above.",
        "- Composite uniqueness and relationship rules should be reviewed in "
        "`DATA_MODEL.md` and `src/workflow_triggers.sql`.",
        "- This generated reference documents the current implementation; "
        "it does not claim that every business rule is enforced by SQL.",
        "",
    ])

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    db.close()

    print(f"PASS: Created {OUTPUT}")
    print(f"PASS: Documented {len(tables)} tables.")


if __name__ == "__main__":
    main()