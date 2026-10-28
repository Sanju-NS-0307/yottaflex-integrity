
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS learner (
    learner_id INTEGER PRIMARY KEY,
    learner_ref TEXT NOT NULL UNIQUE,
    cohort TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE IF NOT EXISTS assessment (
    assessment_id INTEGER PRIMARY KEY,
    assessment_ref TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    opens_at TEXT NOT NULL,
    closes_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    CHECK (opens_at < closes_at)
);

CREATE TABLE IF NOT EXISTS integrity_rule (
    integrity_rule_id INTEGER PRIMARY KEY,
    rule_ref TEXT NOT NULL,
    rule_version INTEGER NOT NULL CHECK (rule_version > 0),
    threshold REAL NOT NULL CHECK (threshold >= 0 AND threshold <= 100),
    effective_from TEXT NOT NULL,
    effective_to TEXT,
    rule_description TEXT NOT NULL,
    UNIQUE (rule_ref, rule_version),
    CHECK (effective_to IS NULL OR effective_from < effective_to)
);

CREATE TABLE IF NOT EXISTS submission (
    submission_id INTEGER PRIMARY KEY,
    submission_ref TEXT NOT NULL UNIQUE,
    learner_id INTEGER NOT NULL REFERENCES learner(learner_id),
    assessment_id INTEGER NOT NULL REFERENCES assessment(assessment_id),
    submitted_at TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    submission_status TEXT NOT NULL
        CHECK (submission_status IN ('submitted', 'withdrawn')),
    UNIQUE (learner_id, assessment_id, submitted_at)
);

CREATE TABLE IF NOT EXISTS similarity_report (
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
);

CREATE TABLE IF NOT EXISTS reviewer (
    reviewer_id INTEGER PRIMARY KEY,
    reviewer_ref TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL
        CHECK (role IN ('instructor', 'academic_administrator', 'support_staff', 'platform_administrator')),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS case_record (
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
);

CREATE TABLE IF NOT EXISTS reviewer_assignment (
    assignment_id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    reviewer_id INTEGER NOT NULL REFERENCES reviewer(reviewer_id),
    assigned_at TEXT NOT NULL,
    unassigned_at TEXT,
    assignment_reason TEXT NOT NULL,
    CHECK (unassigned_at IS NULL OR assigned_at < unassigned_at)
);

CREATE TABLE IF NOT EXISTS reviewer_conflict (
    conflict_id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    reviewer_id INTEGER NOT NULL REFERENCES reviewer(reviewer_id),
    conflict_type TEXT NOT NULL,
    declared_at TEXT NOT NULL,
    resolution_status TEXT NOT NULL
        CHECK (resolution_status IN ('unresolved', 'resolved', 'recused')),
    resolution_note TEXT
);

CREATE TABLE IF NOT EXISTS evidence_item (
    evidence_item_id INTEGER PRIMARY KEY,
    evidence_ref TEXT NOT NULL UNIQUE,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    evidence_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    description TEXT NOT NULL,
    added_at TEXT NOT NULL,
    added_by_reviewer_id INTEGER REFERENCES reviewer(reviewer_id)
);

CREATE TABLE IF NOT EXISTS decision (
    decision_id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    reviewer_id INTEGER NOT NULL REFERENCES reviewer(reviewer_id),
    decision_type TEXT NOT NULL
        CHECK (decision_type IN ('no_breach', 'breach_found', 'inconclusive', 'overturned')),
    rationale TEXT NOT NULL CHECK (length(trim(rationale)) > 0),
    decided_at TEXT NOT NULL,
    integrity_rule_id INTEGER NOT NULL REFERENCES integrity_rule(integrity_rule_id)
);

CREATE TABLE IF NOT EXISTS appeal (
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
);

CREATE TABLE IF NOT EXISTS appeal_review (
    appeal_review_id INTEGER PRIMARY KEY,
    appeal_id INTEGER NOT NULL REFERENCES appeal(appeal_id),
    reviewer_id INTEGER NOT NULL REFERENCES reviewer(reviewer_id),
    review_rationale TEXT NOT NULL CHECK (length(trim(review_rationale)) > 0),
    review_outcome TEXT NOT NULL
        CHECK (review_outcome IN ('upheld', 'overturned', 'partially_upheld')),
    reviewed_at TEXT NOT NULL,
    UNIQUE (appeal_id, reviewer_id)
);

CREATE TABLE IF NOT EXISTS audit_event (
    event_id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES case_record(case_id),
    event_type TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    actor_id TEXT,
    occurred_at TEXT NOT NULL,
    previous_state TEXT,
    new_state TEXT,
    event_details TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_submission_learner
    ON submission(learner_id);

CREATE INDEX IF NOT EXISTS idx_submission_assessment
    ON submission(assessment_id);

CREATE INDEX IF NOT EXISTS idx_similarity_submission
    ON similarity_report(submission_id);

CREATE INDEX IF NOT EXISTS idx_case_status
    ON case_record(case_status);

CREATE INDEX IF NOT EXISTS idx_assignment_case
    ON reviewer_assignment(case_id, reviewer_id);

CREATE INDEX IF NOT EXISTS idx_decision_case
    ON decision(case_id, decided_at);

CREATE INDEX IF NOT EXISTS idx_audit_case_time
    ON audit_event(case_id, occurred_at);
