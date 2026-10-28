

# Architecture Decision Log



## ADR-001: Core Technology Stack



Status: Accepted



Decision:

Use Python for data generation, validation, business rules and exports.

Use SQLite for relational persistence and transactional operations.

Use CSV, JSON and SQL for portable data exports.



Reason:

The stack is free, locally runnable, suitable for relational data,

and practical to implement and verify within the challenge window.



Trade-offs:

SQLite is suitable for this assessment but is not intended to

demonstrate a large production multi-user deployment.



Verification:

Confirm the schema, generator and workflow run locally without

requiring a paid external service.



## ADR-002: Deterministic Synthetic Data



Status: Accepted



Decision:

Use a fixed seed of 20261022 and configurable dataset sizes.

Generate parent records before dependent records.

Use deterministic identifiers and derive dependent values from

documented rules.



Reason:

The same configuration must reproduce equivalent outputs.



Verification:

Run generation twice with the same configuration and compare

row counts and checksums.



## ADR-003: Academic Due Process



Status: Accepted



Decision:

A similarity flag initiates review and does not independently

establish misconduct.

Require documented decisions, reviewer eligibility, evidence

history and independent appeal review.



Reason:

The workflow must support fair review and transparent decisions.



Verification:

Test all required negative scenarios and valid lifecycle paths.



## ADR-004: Audit History



Status: Accepted



Decision:

Record important state changes and evidence actions as explicit

events. Preserve previous decisions and their supporting context.



Reason:

Reviewers must be able to reconstruct the case timeline.



Verification:

Confirm that later actions do not erase earlier events or decisions.



## ADR-005: Ground Truth Separation



Status: Accepted



Decision:

Store known synthetic anomalies and expected labels separately

from operational input data.



Reason:

Evaluation labels must not leak into operational decision inputs.



Verification:

Inspect exported files and confirm that the application does not

use ground-truth labels to make case decisions.



## ADR-006: Optional User Interface



Status: Deferred



Decision:

Do not build a dashboard until the mandatory data, workflow,

validation and export requirements have been implemented and tested.



Reason:

Core correctness and evidence of verification take priority over

optional visual features.




