"""Build the Phase 7 SQLite analytical model and Power BI source tables.

Run from the repository root:
    python -m src.build_sql_model

The module reads the Phase 6 source files, creates a star schema in SQLite,
performs reconciliation checks, and exports clean CSV tables for Power BI.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BuildPaths:
    repo_root: Path
    database: Path
    powerbi_data: Path
    sql_dir: Path


REQUIRED_FILES = (
    "data/raw/train.csv",
    "data/raw/test.csv",
    "data/raw/store.csv",
    "reports/tables/final_test_forecast.csv",
    "reports/tables/final_daily_forecast.csv",
    "reports/tables/final_store_forecast.csv",
    "reports/tables/final_weekday_forecast.csv",
    "reports/tables/final_promo_forecast.csv",
    "reports/tables/final_forecast_summary.csv",
    "reports/tables/final_forecast_controls.csv",
    "models/final_model_metadata.json",
    "sql/01_create_tables.sql",
    "sql/02_create_views.sql",
)

DAY_NAMES = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    """Resolve and validate the repository root."""
    if repo_root is not None:
        root = Path(repo_root).expanduser().resolve()
    else:
        current = Path.cwd().resolve()
        root = current.parent if current.name == "notebooks" else current

    missing = [relative for relative in REQUIRED_FILES if not (root / relative).exists()]
    if missing:
        formatted = "\n".join(f"  - {item}" for item in missing)
        raise FileNotFoundError(
            f"Repository root could not be validated: {root}\n"
            f"Missing required files:\n{formatted}"
        )
    return root


def build_paths(repo_root: Path, database_path: str | Path | None = None) -> BuildPaths:
    database = (
        Path(database_path).expanduser().resolve()
        if database_path is not None
        else repo_root / "data" / "processed" / "rossmann_analytics.db"
    )
    return BuildPaths(
        repo_root=repo_root,
        database=database,
        powerbi_data=repo_root / "powerbi" / "data",
        sql_dir=repo_root / "sql",
    )


def _read_csv(path: Path, **kwargs: Any) -> pd.DataFrame:
    try:
        return pd.read_csv(path, low_memory=False, **kwargs)
    except Exception as exc:  # pragma: no cover - defensive context
        raise RuntimeError(f"Could not read {path}: {exc}") from exc


def load_sources(repo_root: Path) -> dict[str, Any]:
    """Load raw, forecast, reconciliation, and metadata sources."""
    sources: dict[str, Any] = {
        "train": _read_csv(
            repo_root / "data/raw/train.csv",
            dtype={"StateHoliday": "string"},
        ),
        "test": _read_csv(
            repo_root / "data/raw/test.csv",
            dtype={"StateHoliday": "string"},
        ),
        "store": _read_csv(repo_root / "data/raw/store.csv"),
        "forecast": _read_csv(
            repo_root / "reports/tables/final_test_forecast.csv",
            dtype={"StateHoliday": "string"},
        ),
        "daily_expected": _read_csv(repo_root / "reports/tables/final_daily_forecast.csv"),
        "store_expected": _read_csv(repo_root / "reports/tables/final_store_forecast.csv"),
        "weekday_expected": _read_csv(repo_root / "reports/tables/final_weekday_forecast.csv"),
        "promo_expected": _read_csv(repo_root / "reports/tables/final_promo_forecast.csv"),
        "summary_expected": _read_csv(repo_root / "reports/tables/final_forecast_summary.csv"),
        "controls_expected": _read_csv(repo_root / "reports/tables/final_forecast_controls.csv"),
    }
    with (repo_root / "models/final_model_metadata.json").open(encoding="utf-8") as file:
        sources["metadata"] = json.load(file)
    return sources


def prepare_dim_date(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    start = pd.to_datetime(train["Date"]).min()
    end = pd.to_datetime(test["Date"]).max()
    dates = pd.DataFrame({"DateValue": pd.date_range(start, end, freq="D")})
    iso = dates["DateValue"].dt.isocalendar()
    dates["DateKey"] = dates["DateValue"].dt.strftime("%Y%m%d").astype(int)
    dates["Date"] = dates["DateValue"].dt.strftime("%Y-%m-%d")
    dates["Year"] = dates["DateValue"].dt.year.astype(int)
    dates["Quarter"] = dates["DateValue"].dt.quarter.astype(int)
    dates["QuarterLabel"] = "Q" + dates["Quarter"].astype(str)
    dates["Month"] = dates["DateValue"].dt.month.astype(int)
    dates["MonthName"] = dates["Month"].map(MONTH_NAMES)
    dates["YearMonth"] = dates["DateValue"].dt.strftime("%Y-%m")
    dates["ISOWeek"] = iso.week.astype(int)
    dates["DayOfMonth"] = dates["DateValue"].dt.day.astype(int)
    dates["DayOfWeek"] = (dates["DateValue"].dt.dayofweek + 1).astype(int)
    dates["DayName"] = dates["DayOfWeek"].map(DAY_NAMES)
    dates["IsWeekend"] = dates["DayOfWeek"].isin([6, 7]).astype(int)
    return dates[
        [
            "DateKey",
            "Date",
            "Year",
            "Quarter",
            "QuarterLabel",
            "Month",
            "MonthName",
            "YearMonth",
            "ISOWeek",
            "DayOfMonth",
            "DayOfWeek",
            "DayName",
            "IsWeekend",
        ]
    ]


def _competition_open_date(row: pd.Series) -> str | None:
    month = row.get("CompetitionOpenSinceMonth")
    year = row.get("CompetitionOpenSinceYear")
    if pd.isna(month) or pd.isna(year):
        return None
    try:
        return date(int(year), int(month), 1).isoformat()
    except ValueError:
        return None


def _promo2_start_date(row: pd.Series) -> str | None:
    week = row.get("Promo2SinceWeek")
    year = row.get("Promo2SinceYear")
    if pd.isna(week) or pd.isna(year):
        return None
    try:
        return date.fromisocalendar(int(year), int(week), 1).isoformat()
    except ValueError:
        return None


def prepare_dim_store(store: pd.DataFrame) -> pd.DataFrame:
    dim = store.copy()
    dim["CompetitionOpenDate"] = dim.apply(_competition_open_date, axis=1)
    dim["Promo2StartDate"] = dim.apply(_promo2_start_date, axis=1)
    integer_columns = [
        "CompetitionOpenSinceMonth",
        "CompetitionOpenSinceYear",
        "Promo2",
        "Promo2SinceWeek",
        "Promo2SinceYear",
    ]
    for column in integer_columns:
        dim[column] = pd.to_numeric(dim[column], errors="coerce")
    return dim[
        [
            "Store",
            "StoreType",
            "Assortment",
            "CompetitionDistance",
            "CompetitionOpenSinceMonth",
            "CompetitionOpenSinceYear",
            "CompetitionOpenDate",
            "Promo2",
            "Promo2SinceWeek",
            "Promo2SinceYear",
            "Promo2StartDate",
            "PromoInterval",
        ]
    ]


def prepare_fact_sales_history(train: pd.DataFrame) -> pd.DataFrame:
    fact = train.copy()
    fact["DateKey"] = pd.to_datetime(fact["Date"]).dt.strftime("%Y%m%d").astype(int)
    fact["StateHoliday"] = fact["StateHoliday"].fillna("0").astype(str)
    fact["OpenPromoFlag"] = ((fact["Open"] == 1) & (fact["Promo"] == 1)).astype(int)
    return fact[
        [
            "Store",
            "DateKey",
            "Sales",
            "Customers",
            "Open",
            "Promo",
            "OpenPromoFlag",
            "StateHoliday",
            "SchoolHoliday",
        ]
    ]


def prepare_fact_sales_forecast(
    forecast: pd.DataFrame,
    metadata: dict[str, Any],
) -> pd.DataFrame:
    fact = forecast.copy()
    fact["DateKey"] = pd.to_datetime(fact["Date"]).dt.strftime("%Y%m%d").astype(int)
    fact["StateHoliday"] = fact["StateHoliday"].fillna("0").astype(str)
    fact["OpenPromoFlag"] = (
        (fact["OpenFilled"] == 1) & (fact["Promo"] == 1)
    ).astype(int)
    fact["ModelName"] = metadata["model_name"]
    fact = fact.rename(
        columns={
            "Open": "OpenOriginal",
            "PredictedSales": "ForecastSales",
        }
    )
    return fact[
        [
            "Id",
            "Store",
            "DateKey",
            "OpenOriginal",
            "OpenFilled",
            "OpenMissingFlag",
            "Promo",
            "OpenPromoFlag",
            "StateHoliday",
            "SchoolHoliday",
            "Promo2Active",
            "BaselineRecent365",
            "ForecastSales",
            "ModelName",
        ]
    ]


def prepare_model_metrics(
    train: pd.DataFrame,
    fact_forecast: pd.DataFrame,
    metadata: dict[str, Any],
) -> pd.DataFrame:
    forecast_start = pd.Timestamp(metadata["forecast_start"])
    model_lookback_start = forecast_start - pd.Timedelta(days=int(metadata["history_window_days"]))
    open_store_days = int(fact_forecast["OpenFilled"].sum())
    return pd.DataFrame(
        [
            {
                "ModelKey": 1,
                "Project": metadata["project"],
                "ModelName": metadata["model_name"],
                "ModelType": metadata["model_type"],
                "PredictionColumn": metadata["prediction_column"],
                "HistoryWindowDays": int(metadata["history_window_days"]),
                "HistoricalDataStart": str(pd.to_datetime(train["Date"]).min().date()),
                "HistoricalDataEnd": metadata["historical_data_end"],
                "ModelLookbackStart": str(model_lookback_start.date()),
                "ForecastStart": metadata["forecast_start"],
                "ForecastEnd": metadata["forecast_end"],
                "ForecastRows": int(len(fact_forecast)),
                "ForecastStores": int(fact_forecast["Store"].nunique()),
                "ForecastDates": int(fact_forecast["DateKey"].nunique()),
                "OpenStoreDays": open_store_days,
                "ClosedStoreDays": int(len(fact_forecast) - open_store_days),
                "MissingOpenValues": int(fact_forecast["OpenMissingFlag"].sum()),
                "ForecastTotalSales": float(fact_forecast["ForecastSales"].sum()),
                "MeanRMSPE": float(metadata["phase5_mean_rmspe"]),
                "RMSPEStandardDeviation": float(metadata["phase5_rmspe_standard_deviation"]),
                "FinalFoldRMSPE": float(metadata["phase5_final_fold_rmspe"]),
                "KagglePublicRMSPE": float(metadata["kaggle_public_score"]),
                "KagglePrivateRMSPE": float(metadata["kaggle_private_score"]),
                "GeneratedAtUTC": metadata["generated_at_utc"],
                "KaggleEvaluatedAtUTC": metadata.get("kaggle_evaluated_at_utc"),
                "SelectionReason": metadata["selection_reason"],
                "ClosedStoreRule": metadata["closed_store_rule"],
                "MissingOpenRule": metadata["missing_open_rule"],
            }
        ]
    )


def _normalise_for_sql(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    return output.astype(object).where(pd.notna(output), None)


def _execute_sql_file(connection: sqlite3.Connection, path: Path) -> None:
    connection.executescript(path.read_text(encoding="utf-8"))


def _load_table(
    connection: sqlite3.Connection,
    table_name: str,
    frame: pd.DataFrame,
    chunksize: int = 50_000,
) -> None:
    _normalise_for_sql(frame).to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False,
        chunksize=chunksize,
        method=None,
    )


def create_database(
    paths: BuildPaths,
    tables: dict[str, pd.DataFrame],
) -> None:
    paths.database.parent.mkdir(parents=True, exist_ok=True)
    if paths.database.exists():
        paths.database.unlink()

    with sqlite3.connect(paths.database) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        _execute_sql_file(connection, paths.sql_dir / "01_create_tables.sql")

        _load_table(connection, "dim_date", tables["dim_date"])
        _load_table(connection, "dim_store", tables["dim_store"])
        _load_table(connection, "fact_sales_history", tables["fact_sales_history"])
        _load_table(connection, "fact_sales_forecast", tables["fact_sales_forecast"])
        _load_table(connection, "model_metrics", tables["model_metrics"])

        connection.executescript(
            """
            CREATE INDEX idx_history_date ON fact_sales_history(DateKey);
            CREATE INDEX idx_history_store ON fact_sales_history(Store);
            CREATE INDEX idx_history_promo ON fact_sales_history(Promo, OpenPromoFlag);
            CREATE INDEX idx_forecast_date ON fact_sales_forecast(DateKey);
            CREATE INDEX idx_forecast_store ON fact_sales_forecast(Store);
            CREATE INDEX idx_forecast_promo ON fact_sales_forecast(Promo, OpenPromoFlag);
            """
        )
        _execute_sql_file(connection, paths.sql_dir / "02_create_views.sql")
        connection.commit()


def _format_value(value: Any) -> str:
    if isinstance(value, (float, np.floating)):
        return f"{float(value):.10f}"
    return str(value)


def run_quality_checks(
    sources: dict[str, Any],
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    train = sources["train"]
    forecast_source = sources["forecast"]
    history = tables["fact_sales_history"]
    forecast = tables["fact_sales_forecast"]
    dim_store = tables["dim_store"]
    dim_date = tables["dim_date"]
    checked_at = datetime.now(timezone.utc).isoformat()
    checks: list[dict[str, Any]] = []

    def add(
        area: str,
        control: str,
        passed: bool,
        observed: Any,
        expected: Any,
        tolerance: str = "Exact",
    ) -> None:
        checks.append(
            {
                "Area": area,
                "ControlName": control,
                "Passed": int(bool(passed)),
                "ObservedValue": _format_value(observed),
                "ExpectedValue": _format_value(expected),
                "Tolerance": tolerance,
                "CheckedAtUTC": checked_at,
            }
        )

    add("Population", "Historical rows loaded", len(history) == len(train), len(history), len(train))
    add(
        "Population",
        "Forecast rows loaded",
        len(forecast) == len(forecast_source),
        len(forecast),
        len(forecast_source),
    )
    add("Dimensions", "Store dimension rows", len(dim_store) == sources["store"]["Store"].nunique(), len(dim_store), sources["store"]["Store"].nunique())
    expected_date_rows = (
        pd.to_datetime(sources["test"]["Date"]).max()
        - pd.to_datetime(train["Date"]).min()
    ).days + 1
    add("Dimensions", "Date dimension is continuous", len(dim_date) == expected_date_rows, len(dim_date), expected_date_rows)
    add("Keys", "Historical Store-Date duplicates", not history.duplicated(["Store", "DateKey"]).any(), int(history.duplicated(["Store", "DateKey"]).sum()), 0)
    add("Keys", "Forecast Store-Date duplicates", not forecast.duplicated(["Store", "DateKey"]).any(), int(forecast.duplicated(["Store", "DateKey"]).sum()), 0)
    add("Integrity", "Historical stores found in dimension", history["Store"].isin(dim_store["Store"]).all(), int((~history["Store"].isin(dim_store["Store"])).sum()), 0)
    add("Integrity", "Forecast stores found in dimension", forecast["Store"].isin(dim_store["Store"]).all(), int((~forecast["Store"].isin(dim_store["Store"])).sum()), 0)
    add("Integrity", "Historical dates found in dimension", history["DateKey"].isin(dim_date["DateKey"]).all(), int((~history["DateKey"].isin(dim_date["DateKey"])).sum()), 0)
    add("Integrity", "Forecast dates found in dimension", forecast["DateKey"].isin(dim_date["DateKey"]).all(), int((~forecast["DateKey"].isin(dim_date["DateKey"])).sum()), 0)
    add("Business rules", "Closed stores receive zero forecast", bool((forecast.loc[forecast["OpenFilled"] == 0, "ForecastSales"].abs() <= 1e-9).all()), int((forecast.loc[forecast["OpenFilled"] == 0, "ForecastSales"].abs() > 1e-9).sum()), 0, "Absolute tolerance 1e-9")
    history_promo_expected = ((history["Open"] == 1) & (history["Promo"] == 1)).astype(int)
    forecast_promo_expected = ((forecast["OpenFilled"] == 1) & (forecast["Promo"] == 1)).astype(int)
    promo_mismatches = int((history["OpenPromoFlag"] != history_promo_expected).sum() + (forecast["OpenPromoFlag"] != forecast_promo_expected).sum())
    add("Business rules", "OpenPromoFlag only counts open promoted stores", promo_mismatches == 0, promo_mismatches, 0)
    add("Measures", "No negative historical sales", bool((history["Sales"] >= 0).all()), int((history["Sales"] < 0).sum()), 0)
    add("Measures", "No negative forecasts", bool((forecast["ForecastSales"] >= 0).all()), int((forecast["ForecastSales"] < 0).sum()), 0)
    add("Measures", "No missing forecasts", not forecast["ForecastSales"].isna().any(), int(forecast["ForecastSales"].isna().sum()), 0)
    add("Forecast scope", "Forecast stores", forecast["Store"].nunique() == 856, forecast["Store"].nunique(), 856)
    add("Forecast scope", "Forecast dates", forecast["DateKey"].nunique() == 48, forecast["DateKey"].nunique(), 48)
    add("Forecast scope", "Missing Open values imputed", forecast["OpenMissingFlag"].sum() == 11, int(forecast["OpenMissingFlag"].sum()), 11)

    source_total = float(forecast_source["PredictedSales"].sum())
    fact_total = float(forecast["ForecastSales"].sum())
    add("Reconciliation", "Forecast total matches Phase 6 row-level output", np.isclose(fact_total, source_total, rtol=0, atol=1e-6), fact_total, source_total, "Absolute tolerance 1e-6")

    daily_actual = (
        forecast.assign(Date=pd.to_datetime(forecast_source["Date"]))
        .groupby("Date", as_index=False)
        .agg(
            forecast_sales=("ForecastSales", "sum"),
            reporting_stores=("Store", "size"),
            open_stores=("OpenFilled", "sum"),
            promo_store_days=("OpenPromoFlag", "sum"),
        )
    )
    daily_actual["mean_sales_per_open_store"] = daily_actual["forecast_sales"] / daily_actual["open_stores"]
    daily_expected = sources["daily_expected"].copy()
    daily_expected["Date"] = pd.to_datetime(daily_expected["Date"])
    daily_compare = daily_actual.merge(daily_expected, on="Date", suffixes=("_actual", "_expected"), validate="one_to_one")
    daily_numeric = ["forecast_sales", "reporting_stores", "open_stores", "promo_store_days", "mean_sales_per_open_store"]
    daily_max_diff = max(float((daily_compare[f"{col}_actual"] - daily_compare[f"{col}_expected"]).abs().max()) for col in daily_numeric)
    add("Reconciliation", "Daily forecast summary matches Phase 6", daily_max_diff <= 1e-6, daily_max_diff, 0, "Maximum absolute difference 1e-6")

    store_actual = (
        forecast.groupby("Store", as_index=False)
        .agg(
            forecast_sales=("ForecastSales", "sum"),
            open_days=("OpenFilled", "sum"),
            promo_days=("OpenPromoFlag", "sum"),
            mean_calendar_day_sales=("ForecastSales", "mean"),
            maximum_daily_sales=("ForecastSales", "max"),
        )
    )
    store_actual["closed_days"] = forecast.groupby("Store")["OpenFilled"].apply(lambda s: int((s == 0).sum())).values
    store_actual["mean_sales_per_open_day"] = store_actual["forecast_sales"] / store_actual["open_days"].replace(0, np.nan)
    store_compare = store_actual.merge(sources["store_expected"], on="Store", suffixes=("_actual", "_expected"), validate="one_to_one")
    store_numeric = ["forecast_sales", "open_days", "promo_days", "mean_calendar_day_sales", "maximum_daily_sales", "closed_days", "mean_sales_per_open_day"]
    store_max_diff = max(float((store_compare[f"{col}_actual"] - store_compare[f"{col}_expected"]).abs().max()) for col in store_numeric)
    add("Reconciliation", "Store forecast summary matches Phase 6", store_max_diff <= 1e-6, store_max_diff, 0, "Maximum absolute difference 1e-6")

    weekday_actual = (
        forecast.assign(DayOfWeek=forecast_source["DayOfWeek"].to_numpy())
        .groupby("DayOfWeek", as_index=False)
        .agg(
            rows=("Store", "size"),
            stores=("Store", "nunique"),
            forecast_sales=("ForecastSales", "sum"),
            open_store_days=("OpenFilled", "sum"),
            promo_store_days=("OpenPromoFlag", "sum"),
        )
    )
    weekday_actual["mean_sales_per_open_store"] = weekday_actual["forecast_sales"] / weekday_actual["open_store_days"]
    weekday_compare = weekday_actual.merge(sources["weekday_expected"], on="DayOfWeek", suffixes=("_actual", "_expected"), validate="one_to_one")
    weekday_numeric = ["rows", "stores", "forecast_sales", "open_store_days", "promo_store_days", "mean_sales_per_open_store"]
    weekday_max_diff = max(float((weekday_compare[f"{col}_actual"] - weekday_compare[f"{col}_expected"]).abs().max()) for col in weekday_numeric)
    add("Reconciliation", "Weekday forecast summary matches Phase 6", weekday_max_diff <= 1e-6, weekday_max_diff, 0, "Maximum absolute difference 1e-6")

    promo_actual = (
        forecast.loc[forecast["OpenFilled"] == 1]
        .groupby("Promo", as_index=False)
        .agg(
            open_store_days=("Store", "size"),
            forecast_sales=("ForecastSales", "sum"),
            mean_sales=("ForecastSales", "mean"),
            median_sales=("ForecastSales", "median"),
        )
    )
    promo_compare = promo_actual.merge(sources["promo_expected"], on="Promo", suffixes=("_actual", "_expected"), validate="one_to_one")
    promo_numeric = ["open_store_days", "forecast_sales", "mean_sales", "median_sales"]
    promo_max_diff = max(float((promo_compare[f"{col}_actual"] - promo_compare[f"{col}_expected"]).abs().max()) for col in promo_numeric)
    add("Reconciliation", "Promotion forecast summary matches Phase 6", promo_max_diff <= 1e-6, promo_max_diff, 0, "Maximum absolute difference 1e-6")

    phase6_controls_pass = bool(sources["controls_expected"]["passed"].astype(str).str.lower().eq("true").all())
    add("Inherited controls", "All Phase 6 forecast controls remain passed", phase6_controls_pass, int(sources["controls_expected"]["passed"].astype(str).str.lower().eq("true").sum()), len(sources["controls_expected"]))

    return pd.DataFrame(checks)


def load_quality_results(database: Path, results: pd.DataFrame) -> None:
    with sqlite3.connect(database) as connection:
        connection.execute("DELETE FROM data_quality_results")
        _load_table(connection, "data_quality_results", results, chunksize=1_000)
        connection.commit()


def export_powerbi_tables(
    output_dir: Path,
    tables: dict[str, pd.DataFrame],
    quality_results: pd.DataFrame,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    exports = {
        "dim_date": tables["dim_date"],
        "dim_store": tables["dim_store"],
        "fact_sales_history": tables["fact_sales_history"],
        "fact_sales_forecast": tables["fact_sales_forecast"],
        "model_metrics": tables["model_metrics"],
        "data_quality_results": quality_results,
    }
    paths: dict[str, Path] = {}
    for name, frame in exports.items():
        path = output_dir / f"{name}.csv"
        frame.to_csv(path, index=False)
        paths[name] = path
    return paths


def build_analytics_model(
    repo_root: str | Path | None = None,
    database_path: str | Path | None = None,
    export_powerbi: bool = True,
) -> dict[str, Any]:
    """Build the complete Phase 7 analytical layer."""
    root = resolve_repo_root(repo_root)
    paths = build_paths(root, database_path)
    sources = load_sources(root)

    tables = {
        "dim_date": prepare_dim_date(sources["train"], sources["test"]),
        "dim_store": prepare_dim_store(sources["store"]),
        "fact_sales_history": prepare_fact_sales_history(sources["train"]),
        "fact_sales_forecast": prepare_fact_sales_forecast(sources["forecast"], sources["metadata"]),
    }
    tables["model_metrics"] = prepare_model_metrics(
        sources["train"],
        tables["fact_sales_forecast"],
        sources["metadata"],
    )

    quality_results = run_quality_checks(sources, tables)
    failed = quality_results.loc[quality_results["Passed"] == 0]
    if not failed.empty:
        failed_controls = "\n".join(f"  - {row.Area}: {row.ControlName}" for row in failed.itertuples())
        raise ValueError(f"Phase 7 controls failed before database creation:\n{failed_controls}")

    create_database(paths, tables)
    load_quality_results(paths.database, quality_results)
    exports = export_powerbi_tables(paths.powerbi_data, tables, quality_results) if export_powerbi else {}

    return {
        "repo_root": root,
        "database_path": paths.database,
        "powerbi_exports": exports,
        "tables": tables,
        "quality_results": quality_results,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=None, help="Repository root. Defaults to the current directory.")
    parser.add_argument("--database-path", type=Path, default=None, help="Optional custom SQLite output path.")
    parser.add_argument("--no-powerbi-export", action="store_true", help="Build SQLite but do not export Power BI CSV files.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = build_analytics_model(
        repo_root=args.repo_root,
        database_path=args.database_path,
        export_powerbi=not args.no_powerbi_export,
    )
    quality = result["quality_results"]
    print("Phase 7 analytical model created successfully.")
    print(f"SQLite database: {result['database_path']}")
    if result["powerbi_exports"]:
        print(f"Power BI data folder: {next(iter(result['powerbi_exports'].values())).parent}")
    print(f"Controls passed: {int(quality['Passed'].sum())}/{len(quality)}")
    metrics = result["tables"]["model_metrics"].iloc[0]
    print(f"Forecast rows: {int(metrics['ForecastRows']):,}")
    print(f"Forecast stores: {int(metrics['ForecastStores']):,}")
    print(f"Forecast total sales: {float(metrics['ForecastTotalSales']):,.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
