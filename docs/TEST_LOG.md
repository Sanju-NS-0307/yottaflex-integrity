# Test Log

## Environment
- Operating system: Windows
- Database: SQLite
- Dataset seed: 20261022

## Dataset Generation
- Result: PASS
- Submissions: 10,000
- Flagged similarity reports: 1,000
- Cases: 300
- Appeals: 60
- Foreign-key violations: 0

## Schema Validation
- Result: PASS
- Required entities found: 10
- Supporting tables found: 4
- Foreign-key enforcement verified.

## Data Integrity
- Result: PASS
- Expected record counts verified.
- Exactly 1,000 reports flagged.
- Case/report submission consistency verified.
- Audit event IDs unique.
- Every case has an audit trail.
- Independent appeal reviewers differ from original decision-makers.
- Ground-truth labels excluded from operational submission exports.

## Workflow Rejection Tests
- Result: PASS
- Mismatched case/report relationships rejected.
- Conflicted reviewer assignment and decisions rejected.
- Premature appeal closure rejected.
- Original decision-maker cannot review their own appeal.
- Post-decision evidence requires an audit event.
- Audit event updates and deletions rejected.
- Invalid case lifecycle transition rejected.

## Successful Workflow Tests
- Result: PASS
- 60 appealed cases closed.
- 240 non-appealed cases remain in decision_recorded.
- All 60 closed appeals have an independent review and outcome.

## Reproducibility
- Result: PASS
- All 17 CSV/JSON exports matched byte-for-byte across repeated runs using seed 20261022.

## Limitations
These tests cover the implemented schema, baseline dataset, selected workflow protections, successful outcomes, and export reproducibility. They do not prove that every possible workflow path is correct.
