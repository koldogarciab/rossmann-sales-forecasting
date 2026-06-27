from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd


PROMO_INTERVAL_MONTHS: dict[str, set[int]] = {
    "Jan,Apr,Jul,Oct": {1, 4, 7, 10},
    "Feb,May,Aug,Nov": {2, 5, 8, 11},
    "Mar,Jun,Sept,Dec": {3, 6, 9, 12},
}


def find_project_root(start_path: Path) -> Path:
    """Return the nearest parent containing the expected project folders."""
    start_path = start_path.resolve()
    for candidate in [start_path, *start_path.parents]:
        if (candidate / "data").is_dir() and (candidate / "notebooks").is_dir():
            return candidate
    raise FileNotFoundError(
        "Project root not found. Confirm that data/ and notebooks/ exist."
    )


def _month_difference(later_date: pd.Series, earlier_date: pd.Series) -> pd.Series:
    """Calculate the whole calendar-month difference between two date series."""
    return (
        (later_date.dt.year - earlier_date.dt.year) * 12
        + (later_date.dt.month - earlier_date.dt.month)
    )


def _normalise_state_holiday(series: pd.Series) -> pd.Series:
    """Return StateHoliday as a clean categorical string."""
    return (
        series.fillna("0")
        .astype(str)
        .replace({"0.0": "0", "nan": "0", "None": "0"})
    )


def _build_competition_start_date(dataframe: pd.DataFrame) -> pd.Series:
    year_text = dataframe["CompetitionOpenSinceYear"].astype("Int64").astype("string")
    month_text = (
        dataframe["CompetitionOpenSinceMonth"]
        .astype("Int64")
        .astype("string")
        .str.zfill(2)
    )
    return pd.to_datetime(year_text + "-" + month_text + "-01", errors="coerce")


def _build_promo2_start_date(dataframe: pd.DataFrame) -> pd.Series:
    year_text = dataframe["Promo2SinceYear"].astype("Int64").astype("string")
    week_text = (
        dataframe["Promo2SinceWeek"]
        .astype("Int64")
        .astype("string")
        .str.zfill(2)
    )
    return pd.to_datetime(
        year_text + "-W" + week_text + "-1",
        format="%G-W%V-%u",
        errors="coerce",
    )


def _scheduled_promo2_month(
    month_values: Iterable[int],
    interval_values: Iterable[str],
) -> np.ndarray:
    return np.fromiter(
        (
            int(int(month) in PROMO_INTERVAL_MONTHS.get(str(interval), set()))
            for month, interval in zip(month_values, interval_values)
        ),
        dtype=np.int8,
    )


def build_feature_table(
    daily_data: pd.DataFrame,
    store_data: pd.DataFrame,
    *,
    dataset_name: str,
) -> pd.DataFrame:
    """Create deterministic train/test features without Sales- or Customers-based leakage."""
    dataframe = daily_data.copy()
    store_master = store_data.copy()

    dataframe["Date"] = pd.to_datetime(dataframe["Date"], errors="raise")
    rows_before_merge = len(dataframe)

    dataframe = dataframe.merge(
        store_master,
        on="Store",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    unmatched_rows = int((dataframe["_merge"] != "both").sum())
    if len(dataframe) != rows_before_merge:
        raise ValueError(f"{dataset_name}: the store merge changed the row count.")
    if unmatched_rows != 0:
        raise ValueError(f"{dataset_name}: {unmatched_rows} rows have no matching store.")
    dataframe = dataframe.drop(columns="_merge")

    # Opening status
    dataframe["OpenMissingFlag"] = dataframe["Open"].isna().astype("int8")
    dataframe["OpenFilled"] = dataframe["Open"].fillna(1).astype("int8")

    # Clean categoricals
    dataframe["StateHoliday"] = _normalise_state_holiday(dataframe["StateHoliday"])
    dataframe["StoreType"] = dataframe["StoreType"].fillna("Unknown").astype(str)
    dataframe["Assortment"] = dataframe["Assortment"].fillna("Unknown").astype(str)
    dataframe["PromoInterval"] = dataframe["PromoInterval"].fillna("None").astype(str)

    # Calendar
    dataframe["Year"] = dataframe["Date"].dt.year.astype("int16")
    dataframe["Quarter"] = dataframe["Date"].dt.quarter.astype("int8")
    dataframe["Month"] = dataframe["Date"].dt.month.astype("int8")
    dataframe["Day"] = dataframe["Date"].dt.day.astype("int8")
    dataframe["ISOWeek"] = dataframe["Date"].dt.isocalendar().week.astype("int16")
    dataframe["IsWeekend"] = dataframe["DayOfWeek"].isin([6, 7]).astype("int8")
    dataframe["IsMonthStart"] = dataframe["Date"].dt.is_month_start.astype("int8")
    dataframe["IsMonthEnd"] = dataframe["Date"].dt.is_month_end.astype("int8")
    dataframe["DaysSince2013Start"] = (
        dataframe["Date"] - pd.Timestamp("2013-01-01")
    ).dt.days.astype("int16")

    dataframe["MonthSin"] = np.sin(2 * np.pi * dataframe["Month"] / 12)
    dataframe["MonthCos"] = np.cos(2 * np.pi * dataframe["Month"] / 12)
    dataframe["DayOfWeekSin"] = np.sin(2 * np.pi * dataframe["DayOfWeek"] / 7)
    dataframe["DayOfWeekCos"] = np.cos(2 * np.pi * dataframe["DayOfWeek"] / 7)
    dataframe["ISOWeekSin"] = np.sin(2 * np.pi * dataframe["ISOWeek"] / 52)
    dataframe["ISOWeekCos"] = np.cos(2 * np.pi * dataframe["ISOWeek"] / 52)

    # Competition
    dataframe["CompetitionDistanceMissing"] = (
        dataframe["CompetitionDistance"].isna().astype("int8")
    )
    competition_distance_median = store_master["CompetitionDistance"].median()
    dataframe["CompetitionDistanceImputed"] = (
        dataframe["CompetitionDistance"]
        .fillna(competition_distance_median)
        .astype(float)
    )
    dataframe["LogCompetitionDistance"] = np.log1p(
        dataframe["CompetitionDistanceImputed"]
    )
    dataframe["CompetitionStartDate"] = _build_competition_start_date(dataframe)
    dataframe["CompetitionStartMissing"] = (
        dataframe["CompetitionStartDate"].isna().astype("int8")
    )
    competition_active = (
        dataframe["CompetitionStartDate"].notna()
        & (dataframe["Date"] >= dataframe["CompetitionStartDate"])
    )
    dataframe["CompetitionActive"] = competition_active.astype("int8")
    competition_months = _month_difference(
        dataframe["Date"], dataframe["CompetitionStartDate"]
    )
    dataframe["CompetitionMonthsOpen"] = np.where(
        competition_active,
        competition_months.clip(lower=0),
        0,
    ).astype("int16")

    # Promo2
    dataframe["Promo2StartDate"] = _build_promo2_start_date(dataframe)
    dataframe["Promo2StartMissing"] = dataframe["Promo2StartDate"].isna().astype("int8")
    dataframe["Promo2ScheduledMonth"] = _scheduled_promo2_month(
        dataframe["Month"].to_numpy(),
        dataframe["PromoInterval"].to_numpy(),
    )
    promo2_started = (
        (dataframe["Promo2"] == 1)
        & dataframe["Promo2StartDate"].notna()
        & (dataframe["Date"] >= dataframe["Promo2StartDate"])
    )
    dataframe["Promo2Active"] = (
        promo2_started & (dataframe["Promo2ScheduledMonth"] == 1)
    ).astype("int8")
    promo2_months = _month_difference(dataframe["Date"], dataframe["Promo2StartDate"])
    dataframe["Promo2MonthsSinceStart"] = np.where(
        promo2_started,
        promo2_months.clip(lower=0),
        0,
    ).astype("int16")

    return dataframe


MODEL_NUMERIC_FEATURES: list[str] = [
    "DayOfWeek", "Promo", "SchoolHoliday", "Year", "Quarter",
    "Month", "Day", "ISOWeek", "IsWeekend", "IsMonthStart", "IsMonthEnd",
    "DaysSince2013Start", "MonthSin", "MonthCos", "DayOfWeekSin",
    "DayOfWeekCos", "ISOWeekSin", "ISOWeekCos",
    "CompetitionDistanceImputed", "LogCompetitionDistance",
    "CompetitionDistanceMissing", "CompetitionActive",
    "CompetitionStartMissing", "CompetitionMonthsOpen", "Promo2",
    "Promo2ScheduledMonth", "Promo2Active", "Promo2StartMissing",
    "Promo2MonthsSinceStart",
]

MODEL_CATEGORICAL_FEATURES: list[str] = [
    "Store", "StateHoliday", "StoreType", "Assortment", "PromoInterval",
]

MODEL_FEATURES: list[str] = MODEL_NUMERIC_FEATURES + MODEL_CATEGORICAL_FEATURES
