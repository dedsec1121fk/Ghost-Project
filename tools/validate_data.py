from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
errors = []

for p in sorted(DATA.glob("*.json")):
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"{p.name}: invalid JSON: {e}")
        continue
    if p.name != "sources.json" and not isinstance(data, list):
        errors.append(f"{p.name}: expected list")
    if p.name == "sources.json" and not isinstance(data, dict):
        errors.append(f"{p.name}: expected object")

if errors:
    print("Validation FAILED")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("Validation OK")
print("JSON files:", len(list(DATA.glob('*.json'))))
