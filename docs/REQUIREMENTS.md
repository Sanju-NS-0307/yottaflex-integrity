# Project Requirements and Verification Tracker

## Status definitions

- VERIFIED: implementation and relevant verification evidence are available.
- TESTED: a relevant automated test passed, but full requirement coverage is not established.
- IMPLEMENTED: implementation or documentation exists; verification remains incomplete.
- OPEN: unresolved or not yet demonstrated.

## A. Data Model

- [ ] R01 [TESTED]: Define all 10 required entities and their fields. Evidence: `python tests/check_schema.py`; data dictionary covers 14 tables.
- [ ] R02 [TESTED]: Document field types, required/optional status, enums, uniqueness and validation. Evidence: `docs/DATA_DICTIONARY.md`; `python tests/check_data_dictionary.py`.
- [ ] R03 [TESTED]: Define primary keys and foreign keys for every relationship. Evidence: `src/schema.sql`; `python tests/check_schema.py`, `python tests/check_data.py`.
- [ ] R04 [IMPLEMENTED]: Document cardinality, optional relationships, effective dates and lifecycle states. Evidence: `docs/DATA_MODEL.md`; detailed requirement audit remains.
- [ ] R05 [IMPLEMENTED]: Define immutable, deterministic IDs following required naming conventions. Evidence: `src/generate_data.py`; naming-convention audit remains.
- [ ] R06 [TESTED]: Add reviewer-assignment bridge tables and audit-event history. Evidence: schema and workflow tests.

## B. Synthetic Data Generation

- [ ] R07 [IMPLEMENTED]: Generate parent/master records before dependent records. Evidence: `src/generate_data.py`; generation-order audit remains.
- [ ] R08 [VERIFIED]: Generate 10,000 submissions, 1,000 similarity flags and 300 cases. Evidence: generator output and `python tests/check_data.py`.
- [ ] R09 [TESTED]: Use fixed seed 20261022 and parameterize dataset scale. Evidence: generator command and `python tests/check_reproducibility.py`.
- [ ] R10 [IMPLEMENTED]: Represent legitimate quotations, shared templates and false positives. Evidence: synthetic-data rules; coverage-specific verification remains.
- [ ] R11 [TESTED]: Represent multiple reviewers and successful appeals. Evidence: generated reviewer assignments, 60 appeals, and `python tests/check_positive_workflows.py`; full coverage audit remains.
- [ ] R12 [IMPLEMENTED]: Derive outcomes, totals, scores, dates and statuses from documented rules. Evidence: generator and model documentation; complete derivation audit remains.
- [ ] R13 [TESTED]: Store ground-truth labels separately from operational input data. Evidence: `python tests/check_data.py` confirms submission export excludes ground-truth labels and separate ground-truth CSV exists.

## C. Business Workflow and Due Process

- [ ] R14 [IMPLEMENTED]: Apply transparent thresholds that trigger review, not automatic guilt. Evidence: `docs/DECISIONS.md` and workflow design; threshold-specific audit remains.
- [ ] R15 [TESTED]: Support reviewer assignment and conflict-of-interest checks. Evidence: `python tests/check_workflow.py`.
- [ ] R16 [IMPLEMENTED]: Capture decisions, timestamps and rationales. Evidence: schema, generated data and data dictionary; full field-level audit remains.
- [ ] R17 [TESTED]: Preserve evidence references and case timelines. Evidence: workflow tests and audit-event checks.
- [ ] R18 [TESTED]: Support appeals and independent review. Evidence: `python tests/check_data.py` and `python tests/check_positive_workflows.py`.
- [ ] R19 [TESTED]: Enforce valid lifecycle transitions and case-closure rules. Evidence: `python tests/check_workflow.py` and `python tests/check_positive_workflows.py`.
- [ ] R20 [TESTED]: Record state changes and significant actions without overwriting history. Evidence: workflow rejection tests for audit-event update/delete and post-decision evidence.

## D. Required Negative Scenarios

- [x] R21 [TESTED]: Verify that a flagged similarity report alone creates no case or decision. Evidence: `python tests/check_no_automatic_guilt.py`; broader decision-path coverage remains open.
- [ ] R22 [TESTED]: Prevent a conflicted reviewer from deciding the case. Evidence: `python tests/check_workflow.py`.
- [ ] R23 [TESTED]: Detect or prevent evidence added after a decision without audit history. Evidence: `python tests/check_workflow.py`.
- [ ] R24 [TESTED]: Prevent appeal closure without independent review. Evidence: `python tests/check_workflow.py`.

## E. Validation and Reproducibility

- [ ] R25 [TESTED]: Validate primary-key uniqueness and foreign-key integrity. Evidence: `python tests/check_data.py`; SQL dump restoration also reports zero foreign-key violations. A full uniqueness audit of every table remains.
- [ ] R26 [IMPLEMENTED]: Validate enums, date ordering, joins and duplicate records. Evidence: schema and data checks; complete validation-coverage audit remains.
- [ ] R27 [TESTED]: Validate lifecycle transitions and arithmetic reconciliation. Lifecycle checks pass; full arithmetic-reconciliation coverage remains.
- [ ] R28 [TESTED]: Generate a validation summary and measurable evaluation metrics. Evidence: `outputs/validation_summary.json`; metric completeness review remains.
- [ ] R29 [VERIFIED]: Run the same seed twice and compare row counts and checksums. Evidence: `python tests/check_reproducibility.py` confirms all 21 CSV/JSON exports are byte-for-byte identical.

## F. Deliverables

- [ ] R30 [VERIFIED]: Export CSV data. Evidence: generated CSV files and data checks.
- [ ] R31 [VERIFIED]: Export JSON data. Evidence: generated JSON files and reproducibility checks.
- [ ] R32 [TESTED]: Export SQL schema and seed data. Evidence: `outputs/integrity_cases_dump.sql`; `python tests/export_sql_dump.py` verifies restoration and table counts.
- [ ] R33 [TESTED]: Document schema and data dictionary. Evidence: `docs/DATA_MODEL.md`, `docs/DATA_DICTIONARY.md`, and schema checks.
- [ ] R34 [VERIFIED]: Document generator command, seed and dataset parameters. Evidence: `README.md` and `docs/SOURCE_MANIFEST.md`.
- [ ] R35 [TESTED]: Include source manifest and validation summary. Evidence: `docs/SOURCE_MANIFEST.md` and `outputs/validation_summary.json`; final content review remains.
- [ ] R36 [TESTED]: Include setup, execution and verification instructions. Evidence: Clean-clone setup and validation passed on Python 3.12.9.
- [ ] R37 [TESTED]: Maintain the AI prompt record required by the assessment FAQ. `docs/AI_PROMPT_HISTORY.md` identifies ChatGPT as the only AI tool reported, summarizes recoverable project-related assistance, and discloses that the record is not a verbatim transcript. The FAQ permits a reasonable record when a complete prompt export is unavailable.
- [ ] R38 [IMPLEMENTED]: Document assumptions, decisions, limitations and incomplete work. Evidence: `docs/DECISIONS.md`, `docs/PROJECT_STATE.md`, `docs/DATA_MODEL.md`, and `README.md`; final consistency review remains.

## G. Final Submission

- [ ] R39 [VERIFIED]: A fresh public-repository clone passed schema, data, workflow, no-automatic-guilt, edge-case, positive-workflow, reproducibility, data-dictionary, and SQL dump restore checks on Python 3.12.9.
- [ ] R40 [TESTED]: Review Git history and exclude secrets and prohibited content. Current-file and reachable-history scans found no matches for the specific credential patterns checked. These scans are not comprehensive; the broader security and prohibited-content review remains incomplete.
- [x] R41 [VERIFIED]: Final reviewed documentation changes were pushed to the dedicated public GitHub repository and verified at commit 82fb763.
- [ ] R42 [OPEN]: Submit the public repository link from the same email address used during recruitment, following the provided submission instructions. Public repository access is verified; actual submission is pending.
## Verification Evidence

Evidence cited above refers to the commands and files recorded during the current project review. Rerun the checks against the final committed state. Do not treat a passing test as proof of requirements that the test does not cover.

Final submission remains incomplete until the outstanding requirements and assessment restrictions have been resolved.
