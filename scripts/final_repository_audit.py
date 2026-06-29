from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pandas as pd


def find_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "models").exists() and (candidate / "reports").exists():
            return candidate
    raise SystemExit("FAIL - repository root not found")


ROOT = find_root()
failures: list[str] = []
passes: list[str] = []


def check(condition: bool, label: str) -> None:
    (passes if condition else failures).append(label)


required = [
    "README.md",
    "README_ES.md",
    "environment.yml",
    "requirements.txt",
    "models/final_model_metadata.json",
    "notebooks/01_data_audit.ipynb",
    "notebooks/02_eda.ipynb",
    "notebooks/03_feature_engineering.ipynb",
    "notebooks/04_baseline_models.ipynb",
    "notebooks/05_model_improvement.ipynb",
    "notebooks/06_final_forecast_submission.ipynb",
    "notebooks/07_sql_data_model.ipynb",
    "notebooks/09_explainability_business_impact.ipynb",
    "reports/submissions/rossmann_submission_recent365.csv",
    "reports/tables/final_test_forecast.csv",
    "powerbi/rossmann_sales_forecast_dashboard.pbix",
    "docs/phase_9_production_design_ES.md",
    "reports/figures/project_architecture.png",
]

for item in required:
    check((ROOT / item).exists(), f"required file: {item}")

for unwanted in [".ipynb_checkpoints", "__pycache__", ".virtual_documents", "anaconda_projects"]:
    found = [p for p in ROOT.rglob(unwanted) if ".git" not in p.parts]
    check(not found, f"no unwanted directory: {unwanted}")

pyc = [p for p in ROOT.rglob("*.pyc") if ".git" not in p.parts]
check(not pyc, "no .pyc files")

metadata_path = ROOT / "models/final_model_metadata.json"
if metadata_path.exists():
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    check(metadata.get("model_name") == "Recent 365-day Store + weekday + Promo", "final model name")
    check(metadata.get("forecast_rows") == 41088, "metadata forecast rows")
    check(metadata.get("forecast_stores") == 856, "metadata forecast stores")
    check(abs(float(metadata.get("phase5_mean_rmspe", -1)) - 0.1445) < 1e-9, "metadata mean RMSPE")
    check(abs(float(metadata.get("kaggle_private_score", -1)) - 0.14556) < 1e-9, "metadata Kaggle private score")

forecast_path = ROOT / "reports/tables/final_test_forecast.csv"
if forecast_path.exists():
    df = pd.read_csv(forecast_path, low_memory=False)
    check(len(df) == 41088, "forecast row count")
    check(df["Store"].nunique() == 856, "forecast store count")
    check(pd.to_datetime(df["Date"]).nunique() == 48, "forecast date count")
    check(df["PredictedSales"].notna().all(), "no missing predictions")
    check((df["PredictedSales"] >= 0).all(), "no negative predictions")
    check(abs(df["PredictedSales"].sum() - 247034117.4181572) < 1e-4, "forecast total reconciliation")

# Check tracked unwanted files when Git is available.
try:
    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files"], text=True, stderr=subprocess.DEVNULL
    ).splitlines()
    bad_tracked = [
        p for p in tracked
        if any(part in p for part in [".ipynb_checkpoints", "__pycache__", ".virtual_documents", "anaconda_projects"])
        or p.endswith(".pyc")
    ]
    check(not bad_tracked, "no unwanted tracked files")
    raw_tracked = {
        "data/raw/train.csv",
        "data/raw/store.csv",
        "data/raw/test.csv",
        "data/raw/sample_submission.csv",
    }.intersection(tracked)
    check(not raw_tracked, "raw competition CSV files are not tracked")
    powerbi_csv = [p for p in tracked if p.startswith("powerbi/data/") and p.endswith(".csv")]
    check(not powerbi_csv, "Power BI generated CSV files are not tracked")
except Exception:
    passes.append("Git tracked-file checks skipped")

# Check local image paths referenced in README files.
for readme_name in ["README.md", "README_ES.md"]:
    readme = ROOT / readme_name
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
        missing = [ref for ref in refs if not (ROOT / ref).exists()]
        check(not missing, f"{readme_name} image references")

print(f"Repository root: {ROOT}")
print(f"Checks passed: {len(passes)}")
for item in passes:
    print(f"PASS - {item}")

if failures:
    print(f"\nChecks failed: {len(failures)}")
    for item in failures:
        print(f"FAIL - {item}")
    raise SystemExit(1)

print("\nFINAL RESULT: ALL CHECKS PASSED")
