

# Project Requirements and Verification Tracker



## Status definitions

- NOT STARTED

- IMPLEMENTED

- TESTED

- VERIFIED



## A. Data Model

- \[ ] R01: Define all 10 required entities and their fields.

- \[ ] R02: Document field types, required/optional status, enums, uniqueness and validation.

- \[ ] R03: Define primary keys and foreign keys for every relationship.

- \[ ] R04: Document cardinality, optional relationships, effective dates and lifecycle states.

- \[ ] R05: Define immutable, deterministic IDs following the required naming conventions.

- \[ ] R06: Add reviewer-assignment bridge tables and audit-event history where needed.



## B. Synthetic Data Generation

- \[ ] R07: Generate parent/master records before dependent records.

- \[ ] R08: Generate 10,000 submissions, 1,000 similarity flags and 300 cases.

- \[ ] R09: Use fixed seed 20261022 and parameterize dataset scale.

- \[ ] R10: Represent legitimate quotations, shared templates and false positives.

- \[ ] R11: Represent multiple reviewers and successful appeals.

- \[ ] R12: Derive outcomes, totals, scores, dates and statuses from documented rules.

- \[ ] R13: Store ground-truth labels separately from operational input data.



## C. Business Workflow and Due Process

- \[ ] R14: Apply transparent thresholds that trigger review, not automatic guilt.

- \[ ] R15: Support reviewer assignment and conflict-of-interest checks.

- \[ ] R16: Capture decisions, timestamps and rationales.

- \[ ] R17: Preserve evidence references and complete case timelines.

- \[ ] R18: Support appeals and independent review.

- \[ ] R19: Enforce valid lifecycle transitions and case-closure rules.

- \[ ] R20: Record state changes and significant actions without overwriting history.



## D. Required Negative Scenarios

- \[ ] R21: Detect or reject a flag automatically treated as guilt.

- \[ ] R22: Prevent a conflicted reviewer from deciding the case.

- \[ ] R23: Detect or prevent evidence added after a decision without audit history.

- \[ ] R24: Prevent appeal closure without independent review.



## E. Validation and Reproducibility

- \[ ] R25: Validate primary-key uniqueness and foreign-key integrity.

- \[ ] R26: Validate enums, date ordering, joins and duplicate records.

- \[ ] R27: Validate lifecycle transitions and arithmetic reconciliation.

- \[ ] R28: Generate a validation summary and measurable evaluation metrics.

- \[ ] R29: Run the same seed twice and compare row counts and checksums.



## F. Deliverables

- \[ ] R30: Export CSV data.

- \[ ] R31: Export JSON data.

- \[ ] R32: Export SQL schema and seed data.

- \[ ] R33: Document the schema and data dictionary.

- \[ ] R34: Document the generator command, seed and dataset parameters.

- \[ ] R35: Include a source manifest and validation summary.

- \[ ] R36: Include clear setup, execution and verification instructions.

- \[ ] R37: Maintain the complete AI prompt history required by the FAQ.

- \[ ] R38: Document assumptions, decisions, limitations and incomplete work.



## G. Final Submission

- \[ ] R39: Verify a clean setup and repeatable execution.

- \[ ] R40: Review Git history and exclude secrets and prohibited content.

- \[ ] R41: Push to a dedicated public GitHub repository.

- \[ ] R42: Verify public access and submit the repository link before the deadline.



## Verification Evidence

Record for every requirement:

- Implementation location

- Verification command or procedure

- Expected result

- Actual result

- Evidence or log reference

- Status



