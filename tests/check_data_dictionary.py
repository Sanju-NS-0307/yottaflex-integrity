from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DICTIONARY = ROOT / "docs" / "DATA_DICTIONARY.md"

content = DICTIONARY.read_text(encoding="utf-8")

checks = {
    "appeal review columns are not individually unique": (
        "| `appeal_id` | `INTEGER` | Yes | — |" in content
        and "| `reviewer_id` | `INTEGER` | Yes | — |" in content
    ),
    "appeal review composite uniqueness is documented": (
        "Together, `appeal_id`, `reviewer_id` must be unique." in content
    ),
    "integrity rule composite uniqueness is documented": (
        "Together, `rule_ref`, `rule_version` must be unique." in content
    ),
    "submission composite uniqueness is documented": (
        "Together, `learner_id`, `assessment_id`, `submitted_at` "
        "must be unique." in content
    ),
    "submission learner_id is not individually unique": (
        "| `learner_id` | `INTEGER` | Yes | — |" in content
    ),
    "submission assessment_id is not individually unique": (
        "| `assessment_id` | `INTEGER` | Yes | — |" in content
    ),
    "submission submitted_at is not individually unique": (
        "| `submitted_at` | `TEXT` | Yes | — |" in content
    ),
}

failed = []

for description, passed in checks.items():
    if passed:
        print(f"PASS: {description}")
    else:
        print(f"FAIL: {description}")
        failed.append(description)

if failed:
    raise SystemExit(f"{len(failed)} data dictionary regression check(s) failed.")

print(f"PASS: All {len(checks)} data dictionary regression checks passed.")