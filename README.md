# Academic Integrity Case Management Dataset



A reproducible SQLite-backed synthetic dataset and workflow model for academic-integrity review.



The project models similarity reports, evidence, reviewer assignment, conflicts of interest, decisions, appeals, and audit history. A similarity score triggers review; it does not establish misconduct.



\## Features



\- Relational SQLite schema with primary keys, foreign keys, and constraints.

\- Reproducible synthetic data generation using a fixed seed.

\- Reviewer assignments and conflict-of-interest handling.

\- Evidence records, decision rationale, and independent appeal reviews.

\- Workflow protections implemented using SQLite triggers.

\- Audit history to preserve important case events.

\- CSV and JSON exports, validation summaries, and a data dictionary.

\- Automated data-integrity, workflow, and reproducibility tests.



\## Requirements



\- Python 3.10 or later recommended.

\- No third-party packages required by the generator or validation scripts.

\- SQLite support through Python's standard library.



\## Quick Start



Run from the repository root.



Generate the default dataset:



```powershell

python src/generate\_data.py

```



Default dataset:

\- 10,000 submissions

\- 1,000 flagged similarity reports

\- 300 cases

\- 60 appeals

\- Random seed: `20261022`



Generate a smaller dataset:



```powershell

python src/generate\_data.py --submissions 1000 --flags 100 --cases 30

```



Generated files are written to `outputs/`.



\## Validation



Generate the default dataset before running the checks.



```powershell

python tests/check\_schema.py

python tests/check\_data.py

python tests/check\_workflow.py

python tests/check\_positive\_workflows.py

python tests/check\_reproducibility.py

```



The reproducibility check regenerates the dataset and checks whether CSV and JSON exports remain byte-for-byte identical with the same seed.



\## Main Outputs



| File | Purpose |

|---|---|

| `outputs/integrity\_cases.db` | SQLite database |

| `outputs/submission.csv` | Operational submission records |

| `outputs/similarity\_report.csv` | Similarity scores and flag statuses |

| `outputs/case\_record.csv` | Case records and lifecycle statuses |

| `outputs/reviewer\_assignment.csv` | Reviewer assignments |

| `outputs/reviewer\_conflict.csv` | Conflict declarations and resolution |

| `outputs/evidence\_item.csv` | Evidence records |

| `outputs/decision.csv` | Decisions and rationale |

| `outputs/appeal.csv` | Appeal records and outcomes |

| `outputs/appeal\_review.csv` | Independent appeal reviews |

| `outputs/audit\_event.csv` | Case event history |

| `outputs/ground\_truth.csv` | Synthetic evaluation labels |

| `outputs/ground\_truth.json` | Synthetic evaluation labels in JSON |

| `outputs/validation\_summary.json` | Generation and validation summary |



Additional CSV files contain learner, assessment, integrity-rule, and reviewer records.



Ground-truth labels are evaluation artifacts. They must not be treated as operational input features when evaluating a detection or decision process.



\## Documentation



\- `docs/REQUIREMENTS.md` â€” requirements checklist.

\- `docs/DATA\_MODEL.md` â€” entities and relationships.

\- `docs/DATA\_DICTIONARY.md` â€” implemented columns, types, and constraints.

\- `docs/DECISIONS.md` â€” design decisions.

\- `docs/ACCEPTANCE\_CRITERIA.md` â€” acceptance checks.

\- `docs/PROJECT\_STATE.md` â€” implementation status.

\- `docs/TEST\_LOG.md` â€” test records.

\- `src/schema.sql` â€” database schema.

\- `src/workflow\_triggers.sql` â€” workflow protections.

\- `src/generate\_data.py` â€” data generator.



\## Design Principles



1\. Similarity flags initiate human review; they do not establish guilt.

2\. Decisions require a rationale.

3\. Conflicted reviewers must not perform prohibited review actions.

4\. Appeals require an independent reviewer who did not make the original decision.

5\. Evidence and audit history should preserve what happened and when.

6\. Synthetic anomalies are represented explicitly rather than by corrupting unrelated records.

7\. Identical configurations and seeds should produce reproducible outputs.



\## Limitations



This is a synthetic dataset and workflow prototype, not a production academic-integrity platform. Synthetic data does not establish real-world prevalence or model performance. Automated checks cover defined scenarios and do not prove that every possible workflow path is correct.



\## Responsible Use



Use synthetic records for development, testing, and evaluation. Real academic-integrity processes require appropriate human review, privacy safeguards, transparent evidence handling, and meaningful appeal procedures.




