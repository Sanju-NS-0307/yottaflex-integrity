# Source Manifest

## Project

YottaFlex Integrity - Academic Integrity Case Management and Synthetic Data Platform.

## Data Provenance

The dataset is generated locally by `src/generate_data.py` using Python's seeded random-number generator.

| Property | Value |
|---|---|
| Dataset type | Synthetic academic-integrity workflow data |
| Default seed | `20261022` |
| Default submissions | `10000` |
| Default flagged reports | `1000` |
| Default cases | `300` |
| Database engine | SQLite |
| Schema source | `src/schema.sql` |
| Workflow protections | `src/workflow_triggers.sql` |

The generator creates the records and exports operational data separately from ground-truth labels. The dataset should not be interpreted as real student records.

## Generated Artifacts

| Artifact | Purpose |
|---|---|
| `outputs/integrity_cases.db` | SQLite database |
| `outputs/integrity_cases_dump.sql` | SQL schema-and-data export |
| `outputs/validation_summary.json` | Validation counts and metrics |
| `outputs/ground_truth.csv` | Separate ground-truth labels |
| `outputs/ground_truth.json` | JSON version of the ground-truth labels |
| `outputs/ground_truth_anomalies.csv` | Labelled synthetic edge-case scenarios |
| `outputs/ground_truth_anomalies.json` | JSON version of the edge-case scenarios |
| `outputs/edge_case_results.csv` | Results of the edge-case validation checks |
| `outputs/edge_case_results.json` | JSON version of the edge-case validation results |
| `outputs/*.csv` | Table-level CSV exports |
| `docs/DATA_DICTIONARY.md` | Generated schema reference |

## Reproducibility

Run the default dataset generator from the repository root:

```powershell
python src/generate_data.py --seed 20261022
```

Optional parameters:

- `--submissions`: number of submissions; default `10000`
- `--flags`: number of flagged reports; default `1000`
- `--cases`: number of cases; default `300`

The generator requires `0 <= cases <= flags <= submissions`. Reproducibility checks compare generated CSV and JSON exports across repeated runs with the same seed and parameters.

## Validation Evidence

The following checks passed in the latest recorded run:

- Schema smoke test.
- Data-integrity checks.
- Negative workflow checks.
- Edge-case checks for flag-only records, reviewer conflicts, evidence audit history, and appeal-review independence.
- Positive workflow checks.
- CSV/JSON reproducibility checks.
- Data dictionary regression checks.
- SQL dump restoration, table-count comparison, foreign-key validation, and SQLite integrity check.

Rerun all checks before submission to verify the final repository state.

## Limitations

- Ground-truth labels are synthetic and should not be treated as real misconduct findings.
- Similarity flags are review signals, not automatic findings of misconduct.
- Reproducibility depends on the generator version, seed, parameters, and compatible runtime.
- This manifest documents the generated artifacts; it does not independently establish that every assessment requirement is satisfied.

