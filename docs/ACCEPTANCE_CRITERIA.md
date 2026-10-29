

# Acceptance Criteria



## AC-01: Relational Data Model

- All 10 required entities exist.

- Every entity has a primary key.

- Relationships have appropriate foreign keys.

- Many-to-many relationships use bridge tables.

- Cardinalities, optional relationships, lifecycle states and effective dates are documented.

- Field types, allowed values, uniqueness and validation rules are documented.



Pass: Schema inspection and integrity checks succeed.



## AC-02: Synthetic Dataset

- Exactly 10,000 submissions.

- Exactly 1,000 flagged submissions.

- Exactly 300 cases.

- IDs follow the required deterministic conventions.

- Parent records exist before dependent records.

- Fixed seed: 20261022.

- Starter and full datasets use the same generator.



Pass: Row counts, identifiers and references are validated.



## AC-03: Realistic Coverage

- Legitimate quotations and shared templates are represented.

- False-positive flags are represented.

- Multiple-reviewer cases exist.

- Successful appeals exist.

- Ground-truth outcomes follow documented rules.



Pass: Coverage queries return supporting records.



## AC-04: Case Lifecycle

- Similarity flags trigger review, not automatic guilt.

- Reviewer assignments are recorded.

- Decisions include rationale and timestamps.

- Evidence references remain traceable.

- Appeals support independent review.

- Case closure follows documented rules.

- Historical actions are preserved.



Pass: Valid workflow tests succeed.



## AC-05: Negative Scenarios

- A flagged report alone does not automatically create a case or decision (tested by `python tests/check_no_automatic_guilt.py`).

- Conflicted reviewer decisions are detected or rejected.

- Untracked post-decision evidence is detected or rejected.

- Appeal closure without independent review is detected or rejected.

- Known anomalies have separate ground-truth labels.



Pass: Each required scenario has a recorded expected and actual result.



## AC-06: Validation

- Primary keys are unique.

- Foreign keys resolve.

- Enums contain allowed values.

- Dates follow valid ordering.

- Lifecycle transitions are valid.

- Derived values reconcile with source records.

- Duplicate checks succeed.

- Operational input data does not contain ground-truth labels.



Pass: Baseline validation succeeds and labelled anomalies are reported separately.



## AC-07: Reproducibility

- Two runs use identical seed and parameters.

- Exported row counts match.

- Checksums match for equivalent outputs.

- Output ordering and serialization are deterministic.



Pass: Reproducibility comparison reports no differences.



## AC-08: Exports and Documentation

- CSV export is available.

- JSON export is available.

- SQL schema and seed data are available.

- Data dictionary and source manifest are available.

- Generator command and fixed seed are documented.

- Validation summary is available.

- README explains installation, execution and verification.

- AI prompt history and contribution disclosure are complete.



Pass: A clean local setup reproduces the documented results.



## AC-09: Final Submission

- Repository is dedicated to this project.

- Repository is public.

- No secrets or unauthorized confidential materials are committed.

- Git history shows meaningful development progress.

- Repository can be opened in an incognito browser.

- Repository URL is submitted before the deadline.



Pass: Public access and submission are confirmed.
