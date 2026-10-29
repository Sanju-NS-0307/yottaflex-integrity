# Data Model Specification

**Status:** Implemented baseline — verified against the current schema and defined workflow tests; the full requirements audit remains in progress.

## 1. Core Entities

### Learner

- **Purpose:** Synthetic learner identity.
- **Primary key:** `learner_id`
- **Key fields:** `learner_ref`, `cohort`, `created_at`, `is_active`

### Assessment

- **Purpose:** Assessment metadata and submission window.
- **Primary key:** `assessment_id`
- **Key fields:** `assessment_ref`, `title`, `assessment_type`, `opens_at`, `closes_at`, `created_at`

### Submission

- **Purpose:** A learner's submitted assessment work.
- **Primary key:** `submission_id`
- **Foreign keys:** `learner_id`, `assessment_id`
- **Key fields:** `submission_ref`, `submitted_at`, `content_hash`, `submission_status`

### SimilarityReport

- **Purpose:** Similarity measurements and review triggers.
- **Primary key:** `similarity_report_id`
- **Foreign key:** `submission_id`
- **Key fields:** `report_ref`, `similarity_score`, `threshold_applied`, `generated_at`, `flag_status`

### IntegrityRule

- **Purpose:** Versioned review and decision rules.
- **Primary key:** `integrity_rule_id`
- **Key fields:** `rule_ref`, `rule_version`, `threshold`, `effective_from`, `effective_to`, `rule_description`

### Case

- **Purpose:** Formal review of a flagged submission.
- **Primary key:** `case_id`
- **Foreign keys:** `submission_id`, `similarity_report_id`
- **Key fields:** `case_ref`, `opened_at`, `case_status`, `priority`

### EvidenceItem

- **Purpose:** Evidence references associated with a case.
- **Primary key:** `evidence_item_id`
- **Foreign key:** `case_id`
- **Key fields:** `evidence_ref`, `evidence_type`, `source_reference`, `added_at`, `added_by_reviewer_id`, `description`

### Reviewer

- **Purpose:** Synthetic reviewer identities and eligibility.
- **Primary key:** `reviewer_id`
- **Key fields:** `reviewer_ref`, `role`, `is_active`, `created_at`

### Decision

- **Purpose:** A recorded review decision.
- **Primary key:** `decision_id`
- **Foreign keys:** `case_id`, `reviewer_id`
- **Key fields:** `decision_type`, `rationale`, `decided_at`, `rule_version_applied`

### Appeal

- **Purpose:** An appeal against a prior decision.
- **Primary key:** `appeal_id`
- **Foreign keys:** `case_id`, `original_decision_id`
- **Key fields:** `appeal_ref`, `grounds`, `submitted_at`, `appeal_status`, `outcome`

## 2. Required Supporting Structures

### ReviewerAssignment

- **Purpose:** Many-to-many relationship between cases and reviewers, with assignment history.
- **Primary key:** `assignment_id`
- **Foreign keys:** `case_id`, `reviewer_id`
- **Key fields:** `assigned_at`, `unassigned_at`, `assignment_reason`

### ReviewerConflict

- **Purpose:** Records actual or declared conflicts of interest.
- **Primary key:** `conflict_id`
- **Foreign keys:** `reviewer_id`, `case_id`
- **Key fields:** `conflict_type`, `declared_at`, `resolution_status`

### AuditEvent

- **Purpose:** Records important case actions for traceability.
- **Primary key:** `event_id`
- **Foreign key:** `case_id`
- **Key fields:** `event_type`, `actor_type`, `actor_id`, `occurred_at`, `previous_state`, `new_state`, `event_details`

### AppealReview

- **Purpose:** Records independent appeal review.
- **Primary key:** `appeal_review_id`
- **Foreign keys:** `appeal_id`, `reviewer_id`
- **Key fields:** `review_rationale`, `review_outcome`, `reviewed_at`

## 3. Relationship Cardinality and Constraints

- Learner 1:N Submission.
- Assessment 1:N Submission.
- Submission 1:N SimilarityReport.
- Submission 0:N Case, subject to the active-case business rule.
- SimilarityReport 0:N Case, subject to the active-case business rule.
- Case 1:N EvidenceItem.
- Case N:M Reviewer through ReviewerAssignment.
- Case 1:N Decision.
- Case 0:N Appeal.
- Appeal 1:N AppealReview.
- Reviewer 1:N Decision.
- Case 1:N AuditEvent.

Optional relationships and uniqueness constraints are documented in this specification and the implemented schema. The data dictionary identifies the constraints enforced by SQLite. The schema and workflow tests provide the implementation baseline; they do not establish that every possible business rule or workflow path has been verified.

A submission may have historical cases, but duplicate active cases must be prevented according to the documented business rule. The enforcement mechanism and coverage of that rule should be confirmed against the current schema and tests rather than assumed from the relationship cardinalities alone.

## 4. Lifecycle States

The following lists describe the intended lifecycle states. They should not be interpreted as proof that every state or transition is enforced by the database.

**Submission**

- `draft`
- `submitted`
- `withdrawn`

**Similarity report**

- `generated`
- `flagged`
- `reviewed`
- `superseded`

**Case**

- `open`
- `assigned`
- `under_review`
- `decision_recorded`
- `appealed`
- `closed`

**Decision**

- `pending`
- `no_breach`
- `breach_found`
- `inconclusive`
- `overturned`

**Appeal**

- `submitted`
- `under_independent_review`
- `upheld`
- `overturned`
- `partially_upheld`
- `closed`

Case and appeal states represent connected lifecycles. In the current schema, `under_independent_review` is accepted as both a case status and an appeal status. The case workflow trigger also permits the transitions `appealed` → `under_independent_review` → `closed`. This overlap is a known design inconsistency that should be reviewed; the documentation reflects the current implementation rather than claiming the distinction is enforced.

The schema constraints, workflow implementation, and automated tests should be consulted to determine which states and transitions are actually accepted or rejected.

## 5. Integrity Principles

- Similarity scores trigger review; they do not establish guilt.
- Decisions require an eligible, non-conflicted reviewer.
- Evidence additions are timestamped and attributable.
- Historical decisions are preserved rather than overwritten.
- Appeals require independent review before closure.
- Ground-truth labels are stored outside operational inputs.
- Identifiers are immutable and consistent across exports.
- Rule versions are preserved for historical interpretation.

These principles describe the intended integrity properties. Their enforcement must be assessed against the schema, implementation, and defined tests.

## 6. Design Constraints and Remaining Verification

The following constraints guide implementation and review:

- **Reports and cases:** A submission may have multiple similarity reports and historical cases. Duplicate active cases must be prevented by an explicit business rule.
- **Multiple decisions:** A case may have multiple decisions. Each decision must preserve its author, timestamp, rationale, and applicable rule version.
- **Reviewer conflicts:** Conflicts must be recorded and checked before reviewer assignment and decision recording. Conflict resolution must be documented.
- **Lifecycle transitions:** Permitted case and appeal transitions must be distinguished and validated against the implemented workflow.
- **Timestamps:** Required and nullable timestamps must be checked against the schema and the data dictionary.
- **Anomaly handling:** Anomaly records must be identifiable without corrupting valid records or undermining the integrity of the generated dataset.
- **Historical context:** Earlier decisions and their supporting evidence context must remain traceable when new evidence, decisions, or appeals are recorded.

The requirements audit must confirm the exact database constraints, business-rule enforcement, and test coverage for these items. Where enforcement or coverage has not been verified, it must remain an explicit limitation.

## 7. Resolved Design Decisions

- A submission may have multiple similarity reports.
- Reports retain their generation time and status.
- A submission may have historical cases, but duplicate active cases must be prevented by an explicit business rule.
- A case may have multiple decisions, each preserving its author, timestamp, rationale, and applicable rule version.
- Reviewer assignments are many-to-many and time-aware.
- Reviewer conflicts are explicitly recorded and checked before assignment and decision recording.
- Evidence added after a decision must create an audit event.
- Earlier decisions and their original evidence context are preserved.
- An appeal cannot be closed without a completed independent review.
- Integrity rules are versioned so historical decisions remain explainable.

**Status:** Implemented baseline — these decisions inform the schema and workflow design. Corresponding automated tests cover defined scenarios; full lifecycle coverage and enforcement of every stated constraint are not claimed.

## 8. Case and Appeal Workflow Rules

### 8.1 Case Transitions

The intended case lifecycle includes these transitions:

- `open` → `assigned`
- `assigned` → `under_review`
- `under_review` → `decision_recorded`
- `decision_recorded` → `appealed`
- `decision_recorded` → `closed`
- `appealed` → `under_independent_review`
- `under_independent_review` → `closed`

The current implementation also uses "under_independent_review" as a case state. This overlap with the appeal lifecycle is a known design inconsistency.

A case may be reopened only through an explicit, audited action with a documented reason. Reopening must not erase prior decisions. Reopening behavior must be checked against the implementation and should not be assumed to be supported unless verified.

### 8.2 Decision Rules

- Similarity flags trigger review, not automatic guilt.
- A decision requires an eligible, non-conflicted reviewer.
- Every decision records its type, rationale, timestamp, and applicable rule version.
- A new decision must preserve earlier decisions.
- A case cannot close while a required review is incomplete.

### 8.3 Evidence Rules

- Every evidence item records its case, type, reference, and timestamp.
- Evidence additions after a decision require an audit event.
- Earlier decisions retain their original supporting context.
- Evidence must not be silently deleted or rewritten.

### 8.4 Appeal Rules

- An appeal must reference the case and challenged decision.
- Appeal review must be performed by an eligible independent reviewer.
- The appeal outcome and rationale must be recorded.
- An appeal cannot close without a completed independent review.
- An appeal outcome must not overwrite the original decision.

### 8.5 Reviewer Conflict Rules

- Conflicts must be recorded explicitly.
- A conflicted reviewer cannot make a decision on that case.
- Conflict checks must run when assigning a reviewer and recording a decision.
- Conflict resolution must be recorded before the reviewer becomes eligible.

### 8.6 Validation Expectations

The implementation and automated tests should validate the following behaviors:

- Reject invalid lifecycle transitions.
- Reject decisions made by conflicted reviewers.
- Reject appeal closure without independent review.
- Require audit history for post-decision evidence additions.
- Preserve previous decisions and significant state-change events.

**Verification status:** Partially verified. Defined automated tests cover selected workflow protections and positive and negative scenarios. They do not establish that every possible workflow path, database constraint, or business rule has been tested.
