# Data Dictionary

Generated from `src/schema.sql`.

This document describes the implemented SQLite schema. Business meanings and lifecycle rules are documented separately in `DATA_MODEL.md` and `src/workflow_triggers.sql`.

## `appeal`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `appeal_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `appeal_ref` | `TEXT` | Yes | Unique (single-column) | `â€”` | â€” |
| `case_id` | `INTEGER` | Yes | â€” | `â€”` | case_record.case_id |
| `original_decision_id` | `INTEGER` | Yes | â€” | `â€”` | decision.decision_id |
| `grounds` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `submitted_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `appeal_status` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `outcome` | `TEXT` | No | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE appeal (
    appeal_id INTEGER PRIMARY KEY,
    appeal_ref TEXT NOT NULL UNIQUE,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    original_decision_id INTEGER NOT NULL REFERENCES decision(decision_id),
    grounds TEXT NOT NULL CHECK (length(trim(grounds)) > 0),
    submitted_at TEXT NOT NULL,
    appeal_status TEXT NOT NULL
        CHECK (appeal_status IN (
            'submitted', 'under_independent_review', 'upheld',
            'overturned', 'partially_upheld', 'closed'
        )),
    outcome TEXT
)
```

## `appeal_review`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `appeal_review_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `appeal_id` | `INTEGER` | Yes | â€” | `â€”` | appeal.appeal_id |
| `reviewer_id` | `INTEGER` | Yes | â€” | `â€”` | reviewer.reviewer_id |
| `review_rationale` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `review_outcome` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `reviewed_at` | `TEXT` | Yes | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE appeal_review (
    appeal_review_id INTEGER PRIMARY KEY,
    appeal_id INTEGER NOT NULL REFERENCES appeal(appeal_id),
    reviewer_id INTEGER NOT NULL REFERENCES reviewer(reviewer_id),
    review_rationale TEXT NOT NULL CHECK (length(trim(review_rationale)) > 0),
    review_outcome TEXT NOT NULL
        CHECK (review_outcome IN ('upheld', 'overturned', 'partially_upheld')),
    reviewed_at TEXT NOT NULL,
    UNIQUE (appeal_id, reviewer_id)
)
```

**Composite unique constraints**

- Together, `appeal_id`, `reviewer_id` must be unique.

## `assessment`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `assessment_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `assessment_ref` | `TEXT` | Yes | Unique (single-column) | `â€”` | â€” |
| `title` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `assessment_type` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `opens_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `closes_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `created_at` | `TEXT` | Yes | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE assessment (
    assessment_id INTEGER PRIMARY KEY,
    assessment_ref TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    opens_at TEXT NOT NULL,
    closes_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    CHECK (opens_at < closes_at)
)
```

## `audit_event`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `event_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `case_id` | `INTEGER` | Yes | â€” | `â€”` | case_record.case_id |
| `event_type` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `actor_type` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `actor_id` | `TEXT` | No | â€” | `â€”` | â€” |
| `occurred_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `previous_state` | `TEXT` | No | â€” | `â€”` | â€” |
| `new_state` | `TEXT` | No | â€” | `â€”` | â€” |
| `event_details` | `TEXT` | Yes | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE audit_event (
    event_id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    event_type TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    actor_id TEXT,
    occurred_at TEXT NOT NULL,
    previous_state TEXT,
    new_state TEXT,
    event_details TEXT NOT NULL
)
```

## `case_record`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `case_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `case_ref` | `TEXT` | Yes | Unique (single-column) | `â€”` | â€” |
| `submission_id` | `INTEGER` | Yes | â€” | `â€”` | submission.submission_id |
| `similarity_report_id` | `INTEGER` | Yes | â€” | `â€”` | similarity_report.similarity_report_id |
| `opened_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `case_status` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `priority` | `TEXT` | Yes | â€” | `'normal'` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE case_record (
    case_id INTEGER PRIMARY KEY,
    case_ref TEXT NOT NULL UNIQUE,
    submission_id INTEGER NOT NULL REFERENCES submission(submission_id),
    similarity_report_id INTEGER NOT NULL REFERENCES similarity_report(similarity_report_id),
    opened_at TEXT NOT NULL,
    case_status TEXT NOT NULL
        CHECK (case_status IN (
            'open', 'assigned', 'under_review', 'decision_recorded',
            'appealed', 'under_independent_review', 'closed'
        )),
    priority TEXT NOT NULL DEFAULT 'normal'
        CHECK (priority IN ('low', 'normal', 'high')),
    CHECK (case_id > 0)
)
```

## `decision`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `decision_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `case_id` | `INTEGER` | Yes | â€” | `â€”` | case_record.case_id |
| `reviewer_id` | `INTEGER` | Yes | â€” | `â€”` | reviewer.reviewer_id |
| `decision_type` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `rationale` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `decided_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `integrity_rule_id` | `INTEGER` | Yes | â€” | `â€”` | integrity_rule.integrity_rule_id |

**Declared SQL constraints**

```sql
CREATE TABLE decision (
    decision_id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    reviewer_id INTEGER NOT NULL REFERENCES reviewer(reviewer_id),
    decision_type TEXT NOT NULL
        CHECK (decision_type IN ('no_breach', 'breach_found', 'inconclusive', 'overturned')),
    rationale TEXT NOT NULL CHECK (length(trim(rationale)) > 0),
    decided_at TEXT NOT NULL,
    integrity_rule_id INTEGER NOT NULL REFERENCES integrity_rule(integrity_rule_id)
)
```

## `evidence_item`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `evidence_item_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `evidence_ref` | `TEXT` | Yes | Unique (single-column) | `â€”` | â€” |
| `case_id` | `INTEGER` | Yes | â€” | `â€”` | case_record.case_id |
| `evidence_type` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `source_reference` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `description` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `added_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `added_by_reviewer_id` | `INTEGER` | No | â€” | `â€”` | reviewer.reviewer_id |

**Declared SQL constraints**

```sql
CREATE TABLE evidence_item (
    evidence_item_id INTEGER PRIMARY KEY,
    evidence_ref TEXT NOT NULL UNIQUE,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    evidence_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    description TEXT NOT NULL,
    added_at TEXT NOT NULL,
    added_by_reviewer_id INTEGER REFERENCES reviewer(reviewer_id)
)
```

## `integrity_rule`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `integrity_rule_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `rule_ref` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `rule_version` | `INTEGER` | Yes | â€” | `â€”` | â€” |
| `threshold` | `REAL` | Yes | â€” | `â€”` | â€” |
| `effective_from` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `effective_to` | `TEXT` | No | â€” | `â€”` | â€” |
| `rule_description` | `TEXT` | Yes | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE integrity_rule (
    integrity_rule_id INTEGER PRIMARY KEY,
    rule_ref TEXT NOT NULL,
    rule_version INTEGER NOT NULL CHECK (rule_version > 0),
    threshold REAL NOT NULL CHECK (threshold >= 0 AND threshold <= 100),
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    rule_description TEXT NOT NULL,
    UNIQUE (rule_ref, rule_version),
    CHECK (effective_to IS NULL OR effective_from < effective_to)
)
```

**Composite unique constraints**

- Together, `rule_ref`, `rule_version` must be unique.

## `learner`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `learner_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `learner_ref` | `TEXT` | Yes | Unique (single-column) | `â€”` | â€” |
| `cohort` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `created_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `is_active` | `INTEGER` | Yes | â€” | `1` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE learner (
    learner_id INTEGER PRIMARY KEY,
    learner_ref TEXT NOT NULL UNIQUE,
    cohort TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
)
```

## `reviewer`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `reviewer_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `reviewer_ref` | `TEXT` | Yes | Unique (single-column) | `â€”` | â€” |
| `role` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `is_active` | `INTEGER` | Yes | â€” | `1` | â€” |
| `created_at` | `TEXT` | Yes | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE reviewer (
    reviewer_id INTEGER PRIMARY KEY,
    reviewer_ref TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL
        CHECK (role IN ('instructor', 'academic_administrator', 'support_staff', 'platform_administrator')),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL
)
```

## `reviewer_assignment`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `assignment_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `case_id` | `INTEGER` | Yes | â€” | `â€”` | case_record.case_id |
| `reviewer_id` | `INTEGER` | Yes | â€” | `â€”` | reviewer.reviewer_id |
| `assigned_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `unassigned_at` | `TEXT` | No | â€” | `â€”` | â€” |
| `assignment_reason` | `TEXT` | Yes | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE reviewer_assignment (
    assignment_id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    reviewer_id INTEGER NOT NULL REFERENCES reviewer(reviewer_id),
    assigned_at TEXT NOT NULL,
    unassigned_at TEXT,
    assignment_reason TEXT NOT NULL,
    CHECK (unassigned_at IS NULL OR assigned_at < unassigned_at)
)
```

## `reviewer_conflict`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `conflict_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `case_id` | `INTEGER` | Yes | â€” | `â€”` | case_record.case_id |
| `reviewer_id` | `INTEGER` | Yes | â€” | `â€”` | reviewer.reviewer_id |
| `conflict_type` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `declared_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `resolution_status` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `resolution_note` | `TEXT` | No | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE reviewer_conflict (
    conflict_id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    reviewer_id INTEGER NOT NULL REFERENCES reviewer(reviewer_id),
    conflict_type TEXT NOT NULL,
    declared_at TEXT NOT NULL,
    resolution_status TEXT NOT NULL
        CHECK (resolution_status IN ('unresolved', 'resolved', 'recused')),
    resolution_note TEXT
)
```

## `similarity_report`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `similarity_report_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `report_ref` | `TEXT` | Yes | Unique (single-column) | `â€”` | â€” |
| `submission_id` | `INTEGER` | Yes | â€” | `â€”` | submission.submission_id |
| `integrity_rule_id` | `INTEGER` | Yes | â€” | `â€”` | integrity_rule.integrity_rule_id |
| `similarity_score` | `REAL` | Yes | â€” | `â€”` | â€” |
| `generated_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `flag_status` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `evidence_reference` | `TEXT` | No | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE similarity_report (
    similarity_report_id INTEGER PRIMARY KEY,
    report_ref TEXT NOT NULL UNIQUE,
    submission_id INTEGER NOT NULL REFERENCES submission(submission_id),
    integrity_rule_id INTEGER NOT NULL REFERENCES integrity_rule(integrity_rule_id),
    similarity_score REAL NOT NULL
        CHECK (similarity_score >= 0 AND similarity_score <= 100),
    generated_at TEXT NOT NULL,
    flag_status TEXT NOT NULL
        CHECK (flag_status IN ('not_flagged', 'flagged', 'reviewed', 'superseded')),
    evidence_reference TEXT
)
```

## `submission`

| Column | SQLite type | Required? | Key / uniqueness | Default | References |
|---|---|---|---|---|---|
| `submission_id` | `INTEGER` | Yes | Primary key | `â€”` | â€” |
| `submission_ref` | `TEXT` | Yes | Unique (single-column) | `â€”` | â€” |
| `learner_id` | `INTEGER` | Yes | â€” | `â€”` | learner.learner_id |
| `assessment_id` | `INTEGER` | Yes | â€” | `â€”` | assessment.assessment_id |
| `submitted_at` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `content_hash` | `TEXT` | Yes | â€” | `â€”` | â€” |
| `submission_status` | `TEXT` | Yes | â€” | `â€”` | â€” |

**Declared SQL constraints**

```sql
CREATE TABLE submission (
    submission_id INTEGER PRIMARY KEY,
    submission_ref TEXT NOT NULL UNIQUE,
    learner_id INTEGER NOT NULL REFERENCES learner(learner_id),
    assessment_id INTEGER NOT NULL REFERENCES assessment(assessment_id),
    submitted_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    submission_status TEXT NOT NULL
        CHECK (submission_status IN ('submitted', 'withdrawn')),
    UNIQUE (learner_id, assessment_id, submitted_at)
)
```

**Composite unique constraints**

- Together, `learner_id`, `assessment_id`, `submitted_at` must be unique.

## Interpretation notes

- Similarity scores are percentages on a 0â€“100 scale.
- Boolean-like fields use SQLite integers constrained to 0 or 1.
- Timestamps are stored as ISO-formatted text; the schema does not enforce a timezone format.
- Enumerated values and range constraints are shown in each table's SQL definition above.
- Composite uniqueness and relationship rules should be reviewed in `DATA_MODEL.md` and `src/workflow_triggers.sql`.
- This generated reference documents the current implementation; it does not claim that every business rule is enforced by SQL.
