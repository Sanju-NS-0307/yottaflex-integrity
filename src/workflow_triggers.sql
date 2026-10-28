-- Case must reference a report for the same submission.
CREATE TRIGGER IF NOT EXISTS trg_case_report_match_insert
BEFORE INSERT ON case_record
WHEN NOT EXISTS (
    SELECT 1 FROM similarity_report r
    WHERE r.similarity_report_id = NEW.similarity_report_id
      AND r.submission_id = NEW.submission_id
)
BEGIN
    SELECT RAISE(ABORT, 'Case submission must match report submission');
END;

CREATE TRIGGER IF NOT EXISTS trg_case_report_match_update
BEFORE UPDATE OF submission_id, similarity_report_id ON case_record
WHEN NOT EXISTS (
    SELECT 1 FROM similarity_report r
    WHERE r.similarity_report_id = NEW.similarity_report_id
      AND r.submission_id = NEW.submission_id
)
BEGIN
    SELECT RAISE(ABORT, 'Case submission must match report submission');
END;

-- A conflicted reviewer cannot be assigned to, or decide, the same case.
CREATE TRIGGER IF NOT EXISTS trg_assignment_conflict_insert
BEFORE INSERT ON reviewer_assignment
WHEN EXISTS (
    SELECT 1 FROM reviewer_conflict c
    WHERE c.case_id = NEW.case_id
      AND c.reviewer_id = NEW.reviewer_id
      AND c.resolution_status IN ('unresolved', 'recused')
)
BEGIN
    SELECT RAISE(ABORT, 'Conflicted reviewer cannot be assigned');
END;

CREATE TRIGGER IF NOT EXISTS trg_decision_conflict_insert
BEFORE INSERT ON decision
WHEN EXISTS (
    SELECT 1 FROM reviewer_conflict c
    WHERE c.case_id = NEW.case_id
      AND c.reviewer_id = NEW.reviewer_id
      AND c.resolution_status IN ('unresolved', 'recused')
)
BEGIN
    SELECT RAISE(ABORT, 'Conflicted reviewer cannot record a decision');
END;

CREATE TRIGGER IF NOT EXISTS trg_decision_conflict_update
BEFORE UPDATE OF case_id, reviewer_id ON decision
WHEN EXISTS (
    SELECT 1 FROM reviewer_conflict c
    WHERE c.case_id = NEW.case_id
      AND c.reviewer_id = NEW.reviewer_id
      AND c.resolution_status IN ('unresolved', 'recused')
)
BEGIN
    SELECT RAISE(ABORT, 'Conflicted reviewer cannot record a decision');
END;

-- Completed appeals require a review by someone other than the original reviewer.
CREATE TRIGGER IF NOT EXISTS trg_appeal_terminal_insert
BEFORE INSERT ON appeal
WHEN NEW.appeal_status IN ('closed', 'upheld', 'overturned', 'partially_upheld')
BEGIN
    SELECT RAISE(ABORT, 'Create appeal first; review it before completion');
END;

CREATE TRIGGER IF NOT EXISTS trg_appeal_terminal_update
BEFORE UPDATE OF appeal_status ON appeal
WHEN NEW.appeal_status IN ('closed', 'upheld', 'overturned', 'partially_upheld')
 AND OLD.appeal_status <> NEW.appeal_status
 AND NOT EXISTS (
    SELECT 1
    FROM appeal_review ar
    JOIN decision d ON d.decision_id = (
        SELECT a.original_decision_id
        FROM appeal a
        WHERE a.appeal_id = NEW.appeal_id
    )
    WHERE ar.appeal_id = NEW.appeal_id
      AND ar.reviewer_id <> d.reviewer_id
)
BEGIN
    SELECT RAISE(ABORT, 'Appeal requires independent review before completion');
END;

CREATE TRIGGER IF NOT EXISTS trg_appeal_review_independent
BEFORE INSERT ON appeal_review
WHEN EXISTS (
    SELECT 1
    FROM appeal a
    JOIN decision d ON d.decision_id = a.original_decision_id
    WHERE a.appeal_id = NEW.appeal_id
      AND d.reviewer_id = NEW.reviewer_id
)
BEGIN
    SELECT RAISE(ABORT, 'Appeal reviewer must differ from original reviewer');
END;

-- Evidence added after a decision requires a matching audit event first.
CREATE TRIGGER IF NOT EXISTS trg_evidence_audit_required
BEFORE INSERT ON evidence_item
WHEN EXISTS (
    SELECT 1 FROM decision d WHERE d.case_id = NEW.case_id
)
AND NOT EXISTS (
    SELECT 1 FROM audit_event e
    WHERE e.case_id = NEW.case_id
      AND e.event_type = 'evidence_added'
      AND e.occurred_at = NEW.added_at
)
BEGIN
    SELECT RAISE(ABORT, 'Post-decision evidence requires a matching audit event');
END;

-- Audit history is append-only.
CREATE TRIGGER IF NOT EXISTS trg_audit_no_update
BEFORE UPDATE ON audit_event
BEGIN
    SELECT RAISE(ABORT, 'Audit events cannot be updated');
END;

CREATE TRIGGER IF NOT EXISTS trg_audit_no_delete
BEFORE DELETE ON audit_event
BEGIN
    SELECT RAISE(ABORT, 'Audit events cannot be deleted');
END;

-- Enforce allowed case lifecycle transitions.
CREATE TRIGGER IF NOT EXISTS trg_case_lifecycle
BEFORE UPDATE OF case_status ON case_record
WHEN NEW.case_status <> OLD.case_status
 AND NOT (
       (OLD.case_status = 'open' AND NEW.case_status = 'assigned')
    OR (OLD.case_status = 'assigned' AND NEW.case_status = 'under_review')
    OR (OLD.case_status = 'under_review' AND NEW.case_status = 'decision_recorded')
    OR (OLD.case_status = 'decision_recorded' AND NEW.case_status IN ('appealed', 'closed'))
    OR (OLD.case_status = 'appealed' AND NEW.case_status = 'under_independent_review')
    OR (OLD.case_status = 'under_independent_review' AND NEW.case_status = 'closed')
 )
BEGIN
    SELECT RAISE(ABORT, 'Invalid case lifecycle transition');
END;
