from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


HISTORY_NUMERIC_FEATURES: list[str] = [
    "HistGlobalMean",
    "HistStoreMean",
    "HistStoreWeekdayMean",
    "HistStoreWeekdayPromoMean",
    "HistStoreWeekdayPromoCount",
    "Recent180StoreMean",
    "Recent180StoreWeekdayMean",
    "Recent180StoreWeekdayPromoMean",
    "Recent180StoreWeekdayPromoCount",
    "Recent365StoreMean",
    "Recent365StoreWeekdayMean",
    "Recent365StoreWeekdayPromoMean",
    "Recent365StoreWeekdayPromoCount",
    "Trend180VsLong",
    "Trend365VsLong",
    "BaselineLong",
    "BaselineRecent180",
    "BaselineRecent365",
    "BaselineBlend25Recent180",
    "BaselineBlend50Recent180",
    "BaselineBlend75Recent180",
]


BASELINE_CANDIDATE_COLUMNS: dict[str, str] = {
    "Long-term Store + weekday + Promo": "BaselineLong",
    "Recent 365-day Store + weekday + Promo": "BaselineRecent365",
    "Recent 180-day Store + weekday + Promo": "BaselineRecent180",
    "25% recent 180-day blend": "BaselineBlend25Recent180",
    "50% recent 180-day blend": "BaselineBlend50Recent180",
    "75% recent 180-day blend": "BaselineBlend75Recent180",
}


def _validate_reference_period(
    reference_open: pd.DataFrame,
    cutoff_date: pd.Timestamp,
) -> None:
    if reference_open.empty:
        raise ValueError("The historical reference dataset is empty.")

    if reference_open["Date"].max() >= cutoff_date:
        raise ValueError(
            "Historical reference data must end before the scoring cut-off."
        )

    if (reference_open["OpenFilled"] != 1).any():
        raise ValueError(
            "Historical reference data must contain only open-store rows."
        )


def _group_stat_map(
    reference: pd.DataFrame,
    keys: list[str],
    statistic: str,
) -> pd.Series:
    grouped = reference.groupby(keys, observed=True)["Sales"]

    if statistic == "mean":
        return grouped.mean()

    if statistic == "count":
        return grouped.size()

    raise ValueError(f"Unsupported statistic: {statistic}")


def _map_group_stat(
    scoring_data: pd.DataFrame,
    mapping: pd.Series,
    keys: list[str],
) -> pd.Series:
    if len(keys) == 1:
        values = scoring_data[keys[0]].map(mapping)
    else:
        index = pd.MultiIndex.from_frame(scoring_data[keys])
        values = pd.Series(
            index.map(mapping),
            index=scoring_data.index,
        )

    return pd.Series(
        values,
        index=scoring_data.index,
        dtype=float,
    )


def _hierarchical_mean(
    scoring_data: pd.DataFrame,
    *,
    detailed_map: pd.Series,
    detailed_keys: list[str],
    store_weekday_map: pd.Series,
    store_map: pd.Series,
    global_mean: float,
) -> pd.Series:
    prediction = _map_group_stat(
        scoring_data,
        detailed_map,
        detailed_keys,
    )

    prediction = prediction.fillna(
        _map_group_stat(
            scoring_data,
            store_weekday_map,
            ["Store", "DayOfWeek"],
        )
    )

    prediction = prediction.fillna(
        _map_group_stat(
            scoring_data,
            store_map,
            ["Store"],
        )
    )

    return prediction.fillna(global_mean)


def _build_period_features(
    reference: pd.DataFrame,
    scoring_data: pd.DataFrame,
    *,
    prefix: str,
    global_fallback: float,
) -> pd.DataFrame:
    store_mean_map = _group_stat_map(reference, ["Store"], "mean")
    store_weekday_mean_map = _group_stat_map(
        reference,
        ["Store", "DayOfWeek"],
        "mean",
    )
    store_weekday_promo_mean_map = _group_stat_map(
        reference,
        ["Store", "DayOfWeek", "Promo"],
        "mean",
    )
    store_weekday_promo_count_map = _group_stat_map(
        reference,
        ["Store", "DayOfWeek", "Promo"],
        "count",
    )

    features = pd.DataFrame(index=scoring_data.index)

    features[f"{prefix}StoreMean"] = (
        _map_group_stat(scoring_data, store_mean_map, ["Store"])
        .fillna(global_fallback)
    )

    features[f"{prefix}StoreWeekdayMean"] = (
        _map_group_stat(
            scoring_data,
            store_weekday_mean_map,
            ["Store", "DayOfWeek"],
        )
        .fillna(features[f"{prefix}StoreMean"])
    )

    features[f"{prefix}StoreWeekdayPromoMean"] = _hierarchical_mean(
        scoring_data,
        detailed_map=store_weekday_promo_mean_map,
        detailed_keys=["Store", "DayOfWeek", "Promo"],
        store_weekday_map=store_weekday_mean_map,
        store_map=store_mean_map,
        global_mean=global_fallback,
    )

    features[f"{prefix}StoreWeekdayPromoCount"] = (
        _map_group_stat(
            scoring_data,
            store_weekday_promo_count_map,
            ["Store", "DayOfWeek", "Promo"],
        )
        .fillna(0)
    )

    return features


def add_historical_features(
    reference_open: pd.DataFrame,
    scoring_data: pd.DataFrame,
    *,
    cutoff_date: pd.Timestamp | str,
    recent_windows: Iterable[int] = (180, 365),
) -> pd.DataFrame:
    """
    Add frozen historical aggregates to a scoring dataset.

    Every statistic is calculated only from rows strictly before cutoff_date.
    This makes the resulting features safe for chronological validation and
    future prediction.
    """
    cutoff = pd.Timestamp(cutoff_date)
    reference = reference_open.copy()
    scoring = scoring_data.copy()

    reference["Date"] = pd.to_datetime(reference["Date"], errors="raise")
    scoring["Date"] = pd.to_datetime(scoring["Date"], errors="raise")

    _validate_reference_period(reference, cutoff)

    global_mean = float(reference["Sales"].mean())

    long_features = _build_period_features(
        reference,
        scoring,
        prefix="Hist",
        global_fallback=global_mean,
    )

    scoring = pd.concat([scoring, long_features], axis=1)
    scoring["HistGlobalMean"] = global_mean

    for window_days in recent_windows:
        period_start = cutoff - pd.Timedelta(days=int(window_days))
        recent_reference = reference.loc[
            reference["Date"] >= period_start
        ].copy()

        if recent_reference.empty:
            recent_reference = reference.copy()

        recent_features = _build_period_features(
            recent_reference,
            scoring,
            prefix=f"Recent{int(window_days)}",
            global_fallback=global_mean,
        )

        scoring = pd.concat([scoring, recent_features], axis=1)

    scoring["Trend180VsLong"] = (
        scoring["Recent180StoreWeekdayPromoMean"]
        / scoring["HistStoreWeekdayPromoMean"]
    ).replace([np.inf, -np.inf], np.nan).fillna(1.0).clip(0.50, 1.50)

    scoring["Trend365VsLong"] = (
        scoring["Recent365StoreWeekdayPromoMean"]
        / scoring["HistStoreWeekdayPromoMean"]
    ).replace([np.inf, -np.inf], np.nan).fillna(1.0).clip(0.50, 1.50)

    scoring["BaselineLong"] = scoring["HistStoreWeekdayPromoMean"]
    scoring["BaselineRecent180"] = scoring["Recent180StoreWeekdayPromoMean"]
    scoring["BaselineRecent365"] = scoring["Recent365StoreWeekdayPromoMean"]

    scoring["BaselineBlend25Recent180"] = (
        0.75 * scoring["BaselineLong"]
        + 0.25 * scoring["BaselineRecent180"]
    )
    scoring["BaselineBlend50Recent180"] = (
        0.50 * scoring["BaselineLong"]
        + 0.50 * scoring["BaselineRecent180"]
    )
    scoring["BaselineBlend75Recent180"] = (
        0.25 * scoring["BaselineLong"]
        + 0.75 * scoring["BaselineRecent180"]
    )

    missing_history_features = (
        scoring[HISTORY_NUMERIC_FEATURES]
        .isna()
        .sum()
        .sum()
    )

    if missing_history_features != 0:
        raise ValueError(
            "Historical feature engineering produced missing values."
        )

    return scoring
