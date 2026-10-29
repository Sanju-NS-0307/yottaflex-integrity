# AI Prompt History and Contribution Disclosure

## 1. Purpose

This document records how AI assistance was used while developing YottaFlex Integrity. It summarizes the main areas in which ChatGPT supported the work, including repository analysis, implementation planning, testing, debugging, and documentation.

## 2. AI Tool Used

- **Tool:** ChatGPT
- **Purpose:** Understanding project requirements, planning implementation steps, reviewing code and database logic, interpreting test results, troubleshooting issues, improving documentation, and assisting with Git commands.
- **Other AI tools:** No other AI tools have been reported by the project owner.

## 3. Prompt History and Record Limitations

This document is a reconstructed summary of the AI-assisted work based on the available conversation context. The prompt descriptions below represent the main requests made during development; they are not exact quotations or a complete verbatim export of every prompt submitted.

The original prompts have not all been independently recovered and verified. The summaries are included to provide a useful record without inventing historical wording or claiming that a complete transcript is available.

### 3.1 Understanding the Repository and Requirements

**Area of assistance:** Repository analysis and implementation planning.

**Representative prompt summary:** Asked ChatGPT to examine the existing project, explain its structure and purpose, identify the important components, and recommend a practical sequence of implementation and validation steps.

**How the assistance was used:** The guidance helped organize the work into manageable stages and identify the areas requiring implementation, testing, and documentation.

### 3.2 Synthetic Dataset and Database Design

**Area of assistance:** Dataset generation and database validation.

**Representative prompt summary:** Asked for help developing a reproducible synthetic academic-integrity dataset and checking the database schema, table relationships, record counts, and foreign-key integrity.

**How the assistance was used:** Guidance was used while working on the data-generation workflow and validation checks. The generated records are synthetic and should not be interpreted as real learner or institutional records.

### 3.3 Workflow Rules and Procedural Protections

**Area of assistance:** Case management, reviewer conflicts, appeals, and auditability.

**Representative prompt summary:** Asked ChatGPT to review the workflow logic for reviewer conflicts, independent appeal review, evidence added after a decision, audit-event requirements, and permitted case-state transitions.

**How the assistance was used:** The review helped identify important positive and negative scenarios for workflow testing and documentation. The implemented behavior was checked against the available schema, triggers, and automated tests.

### 3.4 Testing, Debugging, and Reproducibility

**Area of assistance:** Automated checks and validation.

**Representative prompt summary:** Asked for help interpreting test output, checking edge cases and positive workflows, validating data-dictionary consistency, verifying deterministic exports, and checking SQL dump integrity.

**How the assistance was used:** Test results were examined locally. The project includes checks for schema integrity, data quality, workflow behavior, reproducibility, data-dictionary consistency, and SQL dump restoration integrity. These checks provide evidence for the scenarios they cover; they do not prove that every possible defect or workflow path has been tested.

### 3.5 Documentation and Requirements Tracking

**Area of assistance:** Technical documentation and project status.

**Representative prompt summary:** Asked ChatGPT to review and improve the README, data model, data dictionary, source manifest, project-state notes, acceptance criteria, and requirements tracker so that the documentation better reflects the implementation and its verification status.

**How the assistance was used:** Documentation changes were reviewed against the available project files and implementation evidence. Known limitations and incomplete verification work are intended to remain explicitly documented rather than being presented as completed.

### 3.6 Final Review and Git Workflow

**Area of assistance:** Final checks, documentation corrections, and repository updates.

**Representative prompt summary:** Asked for help reviewing Git diffs, correcting inconsistencies between documentation and workflow implementation, interpreting command output, and proceeding with commits and pushes.

**How the assistance was used:** Commands were run in the local development environment, their output was reviewed, and Git operations were performed to update the public repository.

## 4. Contribution Disclosure

The project was developed through a combination of project-owner work and AI-assisted guidance.

The project owner ran commands locally, reviewed outputs, evaluated changes, and performed Git operations. ChatGPT provided explanations, implementation guidance, debugging assistance, testing suggestions, and proposed code or documentation changes.

This disclosure does not claim that every line was manually authored by the project owner, that every AI suggestion was adopted unchanged, or that every historical prompt has been recovered. The source code, tests, documentation, and available repository history should be considered when evaluating the actual implementation and contributions.

## 5. Limitations and Follow-up

- This record is a summary reconstructed from available conversation context, not a verbatim prompt transcript.
- Original prompts or conversation exports should be added if they can be recovered and verified.
- Missing prompt wording has not been invented or presented as an exact historical quotation.
- The list of AI tools reflects the information reported by the project owner and should be updated if additional tools were used.
- This document should be retained with the project documentation and updated if more complete records become available.
- No secrets, credentials, or unauthorized confidential material should be included in the prompt-history record.

## 6. Final Disclosure

ChatGPT was used as a development aid during the project. The record above describes the main areas of assistance and its limitations as accurately as the available information permits. It is intended to support transparency about AI use, not to substitute for review of the actual project artifacts or to claim a complete historical transcript.
