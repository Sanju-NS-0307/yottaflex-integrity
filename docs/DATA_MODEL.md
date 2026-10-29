# Data Model Specification



Status: Implemented baseline - verified against the current schema and workflow tests; full requirements audit remains in progress.



## 1\. Core Entities



### Learner

Purpose: Synthetic learner identity.

Primary key: learner\_id

Key fields: learner\_ref, cohort, created\_at, is\_active



### Assessment

Purpose: Assessment metadata and submission window.

Primary key: assessment\_id

Key fields: assessment\_ref, title, assessment\_type,

opens\_at, closes\_at, created\_at



### Submission

Purpose: A learner's submitted assessment work.

Primary key: submission\_id

Foreign keys: learner\_id, assessment\_id

Key fields: submission\_ref, submitted\_at, content\_hash,

submission\_status



### SimilarityReport

Purpose: Similarity measurements and review triggers.

Primary key: similarity\_report\_id

Foreign key: submission\_id

Key fields: report\_ref, similarity\_score, threshold\_applied,

generated\_at, flag\_status



### IntegrityRule

Purpose: Versioned review and decision rules.

Primary key: integrity\_rule\_id

Key fields: rule\_ref, rule\_version, threshold,

effective\_from, effective\_to, rule\_description



### Case

Purpose: Formal review of a flagged submission.

Primary key: case\_id

Foreign keys: submission\_id, similarity\_report\_id

Key fields: case\_ref, opened\_at, case\_status, priority



### EvidenceItem

Purpose: Evidence references associated with a case.

Primary key: evidence\_item\_id

Foreign key: case\_id

Key fields: evidence\_ref, evidence\_type, source\_reference,

added\_at, added\_by\_reviewer\_id, description



### Reviewer

Purpose: Synthetic reviewer identities and eligibility.

Primary key: reviewer\_id

Key fields: reviewer\_ref, role, is\_active, created\_at



### Decision

Purpose: A recorded review decision.

Primary key: decision\_id

Foreign keys: case\_id, reviewer\_id

Key fields: decision\_type, rationale, decided\_at,

rule\_version\_applied



### Appeal

Purpose: An appeal against a prior decision.

Primary key: appeal\_id

Foreign keys: case\_id, original\_decision\_id

Key fields: appeal\_ref, grounds, submitted\_at,

appeal\_status, outcome



## 2\. Required Supporting Structures



### ReviewerAssignment

Purpose: Many-to-many relationship between cases and reviewers.

Primary key: assignment\_id

Foreign keys: case\_id, reviewer\_id

Key fields: assigned\_at, unassigned\_at, assignment\_reason



### ReviewerConflict

Purpose: Records actual or declared conflicts of interest.

Primary key: conflict\_id

Foreign keys: reviewer\_id, case\_id

Key fields: conflict\_type, declared\_at, resolution\_status



### AuditEvent

Purpose: Append-only record of important case actions.

Primary key: event\_id

Foreign key: case\_id

Key fields: event\_type, actor\_type, actor\_id, occurred\_at,

previous\_state, new\_state, event\_details



### AppealReview

Purpose: Records independent appeal review.

Primary key: appeal\_review\_id

Foreign keys: appeal\_id, reviewer\_id

Key fields: review\_rationale, review\_outcome, reviewed\_at



## 3\. Relationship Cardinality



* Learner 1:N Submission
* Assessment 1:N Submission
* Submission 1:N SimilarityReport
* Submission 0:N Case, subject to documented case policy
* SimilarityReport 0:N Case, subject to documented case policy
* Case 1:N EvidenceItem
* Case N:M Reviewer through ReviewerAssignment
* Case 1:N Decision
* Case 0:N Appeal
* Appeal 1:N AppealReview
* Reviewer 1:N Decision
* Case 1:N AuditEvent



Optional relationships and any uniqueness constraints must be

documented explicitly before schema implementation.



## 4\. Lifecycle States



Submission:

draft, submitted, withdrawn



Similarity report:

generated, flagged, reviewed, superseded



Case:

open, assigned, under\_review, decision\_recorded,

appealed, closed



Decision:

pending, no\_breach, breach\_found, inconclusive, overturned



Appeal:

submitted, under\_independent\_review, upheld,

overturned, partially\_upheld, closed



These states are provisional and must be refined into valid

transitions before implementation.



## 5\. Integrity Principles



* Similarity scores trigger review; they do not establish guilt.
* Decisions require an eligible, non-conflicted reviewer.
* Evidence additions are timestamped and attributable.
* Historical decisions are preserved rather than overwritten.
* Appeals require independent review before closure.
* Ground-truth labels are stored outside operational inputs.
* Identifiers are immutable and consistent across exports.
* Rule versions are preserved for historical interpretation.



## 6\. Open Design Questions



* Should a submission permit multiple reports and multiple cases?
* How will multiple decisions and reviewer disagreements be represented?
* How will reviewer conflicts be detected and resolved?
* Which exact state transitions are permitted?
* Which timestamps are mandatory and which may be null?
* How will anomaly cases be labelled without corrupting valid records?





## 7. Resolved Design Decisions



- A submission may have multiple similarity reports.

- Reports retain their generation time and status.

- A submission may have historical cases, but duplicate active cases

  must be prevented by an explicit business rule.

- A case may have multiple decisions, each preserving its author,

  timestamp, rationale and applicable rule version.

- Reviewer assignments are many-to-many and time-aware.

- Reviewer conflicts are explicitly recorded and checked before

  assignment and decision recording.

- Evidence added after a decision must create an audit event.

- Earlier decisions and their original evidence context are preserved.

- An appeal cannot be closed without a completed independent review.

- Integrity rules are versioned so historical decisions remain explainable.



Status: Proposed - Validate these decisions against the workflow tests

before implementing the database schema.




## 8. Case Lifecycle Rules

### Valid Case Transitions

- open -> assigned
- assigned -> under_review
- under_review -> decision_recorded
- decision_recorded -> appealed
- decision_recorded -> closed
- appealed -> under_independent_review
- under_independent_review -> closed

A case may be reopened only through an explicit, audited action
with a documented reason. Reopening must not erase prior decisions.

### Decision Rules

- Similarity flags trigger review, not automatic guilt.
- A decision requires an eligible, non-conflicted reviewer.
- Every decision records its type, rationale, timestamp and rule version.
- A new decision must preserve earlier decisions.
- A case cannot close while a required review is incomplete.

### Evidence Rules

- Every evidence item records its case, type, reference and timestamp.
- Evidence additions after a decision require an audit event.
- Earlier decisions retain their original supporting context.
- Evidence must not be silently deleted or rewritten.

### Appeal Rules

- An appeal must reference the case and challenged decision.
- Appeal review must be performed by an eligible independent reviewer.
- The appeal outcome and rationale must be recorded.
- An appeal cannot close without a completed independent review.
- An appeal outcome must not overwrite the original decision.

### Reviewer Conflict Rules

- Conflicts must be recorded explicitly.
- A conflicted reviewer cannot make a decision on that case.
- Conflict checks must run when assigning a reviewer and recording a decision.
- Conflict resolution must be recorded before the reviewer becomes eligible.

### Validation Expectations

- Reject invalid lifecycle transitions.
- Reject decisions made by conflicted reviewers.
- Reject appeal closure without independent review.
- Require audit history for post-decision evidence additions.
- Preserve all previous decisions and significant state-change events.

Status: Partially verified - the documented workflow protections have corresponding automated checks. The checks cover defined scenarios and do not establish that every possible workflow path is correct.

