# Academic Integrity Case Management Dataset

A reproducible, SQLite-backed synthetic dataset and workflow model for academic-integrity review.

The project models similarity reports, evidence, reviewer assignments, conflicts of interest, decisions, appeals, and audit history. A similarity score triggers review; it does not establish misconduct.

## Features

- Relational SQLite schema with primary keys, foreign keys, and constraints.
- Reproducible synthetic data generation using a fixed seed.
- Reviewer assignments and conflict-of-interest handling.
- Evidence records, decision rationales, and independent appeal reviews.
- Workflow protections implemented using SQLite triggers.
- Audit history to preserve important case events.
- CSV and JSON exports, validation summaries, and a data dictionary.
- SQL schema-and-data dump.
- Automated data-integrity, workflow, reproducibility, and data-dictionary tests.

## Requirements

- Python 3.10 or later recommended.
- No third-party packages required by the generator or validation scripts.
- SQLite support through Python's standard library.

## Quick Start

Run commands from the repository root.

Generate the default dataset:

```powershell
python src/generate_data.py --seed 20261022
```

Default dataset:

- 10,000 submissions
- 1,000 flagged similarity reports
- 300 cases
- 60 appeals
- Random seed: `20261022`

Generate a smaller dataset for testing:

```powershell
python src/generate_data.py --seed 20261022 --submissions 1000 --flags 100 --cases 30
```

The generator accepts `--seed`, `--submissions`, `--flags`, and `--cases`. It requires `0 <= cases <= flags <= submissions`.

Generated files are written to `outputs/`.

## Validation

Generate the default dataset before running the checks.

```powershell
python tests/check_schema.py
python tests/check_data.py
python tests/check_workflow.py
python tests/check_no_automatic_guilt.py
python tests/check_edge_cases.py
python tests/check_positive_workflows.py
python tests/check_reproducibility.py
python tests/check_data_dictionary.py
python tests/export_sql_dump.py
```

These checks cover schema creation, data integrity, invalid workflow actions, no automatic case or decision from a flag alone, valid workflow paths, CSV/JSON reproducibility, data-dictionary constraint documentation, and SQL dump restoration.

The SQL export test writes `outputs/integrity_cases_dump.sql` and restores it into a fresh in-memory database to compare table counts and check database integrity.

## Main Outputs

| File | Purpose |
|---|---|
| `outputs/integrity_cases.db` | SQLite database |
| `outputs/integrity_cases_dump.sql` | SQL schema-and-data dump |
| `outputs/submission.csv` | Operational submission records |
| `outputs/similarity_report.csv` | Similarity scores and flag statuses |
| `outputs/case_record.csv` | Case records and lifecycle statuses |
| `outputs/reviewer_assignment.csv` | Reviewer assignments |
| `outputs/reviewer_conflict.csv` | Conflict declarations and resolution |
| `outputs/evidence_item.csv` | Evidence records |
| `outputs/decision.csv` | Decisions and rationale |
| `outputs/appeal.csv` | Appeal records and outcomes |
| `outputs/appeal_review.csv` | Independent appeal reviews |
| `outputs/audit_event.csv` | Case event history |
| `outputs/ground_truth.csv` | Separate synthetic evaluation labels |
| `outputs/ground_truth.json` | Evaluation labels in JSON |
| `outputs/ground_truth_anomalies.csv` | Labelled edge-case scenarios in CSV |
| `outputs/ground_truth_anomalies.json` | Labelled edge-case scenarios in JSON |
| `outputs/validation_summary.json` | Generation and validation summary |
| `docs/DATA_DICTIONARY.md` | Implemented columns, types, and constraints |
| `docs/SOURCE_MANIFEST.md` | Data provenance and artifact manifest |

Additional CSV files contain learner, assessment, integrity-rule, and reviewer records.

Ground-truth labels are evaluation artifacts. They must not be treated as operational input features when evaluating a detection or decision process.

## Documentation

- `docs/REQUIREMENTS.md` — requirements checklist.
- `docs/DATA_MODEL.md` — entities and relationships.
- `docs/DATA_DICTIONARY.md` — implemented columns, types, and constraints.
- `docs/DECISIONS.md` — design decisions.
- `docs/ACCEPTANCE_CRITERIA.md` — acceptance checks.
- `docs/PROJECT_STATE.md` — implementation and submission status.
- `docs/TEST_LOG.md` — recorded test results.
- `docs/SOURCE_MANIFEST.md` — data provenance and generated artifacts.
- `src/schema.sql` — database schema.
- `src/workflow_triggers.sql` — workflow protections.
- `src/generate_data.py` — data generator.

## Design Principles

1. Similarity flags initiate human review; they do not establish guilt.
2. Decisions require a rationale.
3. Conflicted reviewers must not perform prohibited review actions.
4. Appeals require an independent reviewer who did not make the original decision.
5. Evidence and audit history should preserve what happened and when.
6. Synthetic anomalies are represented explicitly rather than by corrupting unrelated records.
7. Identical configurations and seeds should produce reproducible outputs.

## Limitations

This is a synthetic dataset and workflow prototype, not a production academic-integrity platform. Synthetic data does not establish real-world prevalence or model performance. Automated checks cover defined scenarios and do not prove that every possible workflow path is correct.

## Responsible Use

Use synthetic records for development, testing, and evaluation. Real academic-integrity processes require appropriate human review, privacy safeguards, transparent evidence handling, and meaningful appeal procedures.
