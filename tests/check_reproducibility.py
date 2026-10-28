import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
GENERATOR = ROOT / "src" / "generate_data.py"

def hashes():
    result = {}
    for path in sorted(OUTPUTS.glob("*")):
        if path.is_file() and path.suffix in {".csv", ".json"}:
            result[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result

before = hashes()
if not before:
    raise SystemExit("FAIL: No CSV/JSON outputs found before regeneration.")

print(f"Captured hashes for {len(before)} exported files.")

run = subprocess.run(
    [sys.executable, str(GENERATOR), "--seed", "20261022"],
    cwd=ROOT,
    capture_output=True,
    text=True,
)

if run.returncode != 0:
    print(run.stdout)
    print(run.stderr)
    raise SystemExit("FAIL: Generator failed during reproducibility test.")

print(run.stdout)
after = hashes()

if before.keys() != after.keys():
    print("Files before:", sorted(before))
    print("Files after:", sorted(after))
    raise SystemExit("FAIL: Exported file list changed.")

differences = [
    name for name in before
    if before[name] != after[name]
]

if differences:
    print("Files with different contents:")
    for name in differences:
        print(f" - {name}")
    raise SystemExit("FAIL: Outputs are not reproducible.")

print(f"PASS: All {len(after)} CSV/JSON exports are byte-for-byte identical.")
print("PASS: Seed 20261022 is reproducible across runs.")
