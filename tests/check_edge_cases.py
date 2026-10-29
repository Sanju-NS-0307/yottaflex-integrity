import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(exist_ok=True)

SCENARIOS = [
    {
        "scenario_id": "EDGE-001",
        "issue_type": "flag_automatically_treated_as_guilt",
        "ground_truth_label": "flag_is_not_guilt",
        "expected_outcome": "A flag alone creates neither a case nor a decision.",
        "test_file": "check_no_automatic_guilt.py",
        "required_output": None,
    },
    {
        "scenario_id": "EDGE-002",
        "issue_type": "reviewer_conflict",
        "ground_truth_label": "conflicted_decision_rejected",
        "expected_outcome": "A conflicted reviewer cannot record a decision.",
        "test_file": "check_workflow.py",
        "required_output": "PASS: Conflicted reviewer cannot record a decision",
    },
    {
        "scenario_id": "EDGE-003",
        "issue_type": "post_decision_evidence_without_history",
        "ground_truth_label": "untracked_evidence_rejected",
        "expected_outcome": "Post-decision evidence without an audit event is rejected.",
        "test_file": "check_workflow.py",
        "required_output": "PASS: Post-decision evidence requires an audit event",
    },
    {
        "scenario_id": "EDGE-004",
        "issue_type": "appeal_closed_without_independent_review",
        "ground_truth_label": "independent_review_required",
        "expected_outcome": "An appeal cannot be closed without independent review.",
        "test_file": "check_workflow.py",
        "required_output": "PASS: Appeal cannot close before independent review",
    },
]


def main():
    results = []
    test_cache = {}

    for scenario in SCENARIOS:
        test_file = scenario["test_file"]

        if test_file not in test_cache:
            completed = subprocess.run(
                [sys.executable, str(ROOT / "tests" / test_file)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            test_cache[test_file] = completed

        completed = test_cache[test_file]
        output = completed.stdout + "\n" + completed.stderr

        if scenario["required_output"] is None:
            matched = completed.returncode == 0
        else:
            matched = scenario["required_output"] in output

        passed = completed.returncode == 0 and matched

        results.append({
            **scenario,
            "actual_result": "passed" if passed else "not_verified",
            "test_exit_code": completed.returncode,
            "verification_detail": (
                "Required test completed successfully."
                if passed
                else "Required result was not verified; inspect test output."
            ),
        })

    csv_path = OUTPUT / "edge_case_results.csv"
    json_path = OUTPUT / "edge_case_results.json"

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    for result in results:
        status = "PASS" if result["actual_result"] == "passed" else "FAIL"
        print(
            f'{status}: {result["scenario_id"]} '
            f'{result["issue_type"]} -> {result["actual_result"]}'
        )

    print(f"\nCSV: outputs/{csv_path.name}")
    print(f"JSON: outputs/{json_path.name}")

    if any(result["actual_result"] != "passed" for result in results):
        print("Some edge cases remain unverified.")
        return 1

    print("All four edge-case checks verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
