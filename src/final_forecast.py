from __future__ import annotations

import numpy as np
import pandas as pd

from src.history_features import add_historical_features


FINAL_MODEL_NAME = "Recent 365-day Store + weekday + Promo"
FINAL_BASELINE_COLUMN = "BaselineRecent365"


def generate_final_forecast(
    train_features: pd.DataFrame,
    test_features: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generate the final Rossmann test forecast.

    The selected Phase 5 model is a leakage-safe historical baseline based on
    the most recent 365 days, segmented by Store, DayOfWeek, and Promo.

    Closed stores receive a prediction of zero. Open stores receive the
    corresponding recent historical mean with the fallback hierarchy defined
    in src.history_features.
    """
    required_train_columns = {
        "Store",
        "Date",
        "OpenFilled",
        "Sales",
    }
    required_test_columns = {
        "Id",
        "Store",
        "Date",
        "OpenFilled",
    }

    missing_train = required_train_columns.difference(
        train_features.columns
    )
    missing_test = required_test_columns.difference(
        test_features.columns
    )

    if missing_train:
        raise ValueError(
            f"Missing train feature columns: {sorted(missing_train)}"
        )

    if missing_test:
        raise ValueError(
            f"Missing test feature columns: {sorted(missing_test)}"
        )

    train_data = train_features.copy()
    test_data = test_features.copy()

    train_data["Date"] = pd.to_datetime(
        train_data["Date"],
        errors="raise",
    )
    test_data["Date"] = pd.to_datetime(
        test_data["Date"],
        errors="raise",
    )

    forecast_start = test_data["Date"].min()

    reference_open = train_data.loc[
        (train_data["Date"] < forecast_start)
        & (train_data["OpenFilled"] == 1)
    ].copy()

    scored_test = add_historical_features(
        reference_open,
        test_data,
        cutoff_date=forecast_start,
    )

    prediction = np.where(
        scored_test["OpenFilled"].eq(1),
        scored_test[FINAL_BASELINE_COLUMN],
        0.0,
    )

    scored_test["PredictedSales"] = np.clip(
        prediction.astype(float),
        a_min=0,
        a_max=None,
    )

    return scored_test


def build_submission(
    scored_test: pd.DataFrame,
    sample_submission: pd.DataFrame,
) -> pd.DataFrame:
    """Build a Kaggle submission aligned to sample_submission Id order."""
    required_scored_columns = {"Id", "PredictedSales"}
    required_submission_columns = {"Id", "Sales"}

    missing_scored = required_scored_columns.difference(
        scored_test.columns
    )
    missing_submission = required_submission_columns.difference(
        sample_submission.columns
    )

    if missing_scored:
        raise ValueError(
            f"Missing scored-test columns: {sorted(missing_scored)}"
        )

    if missing_submission:
        raise ValueError(
            "sample_submission must contain Id and Sales."
        )

    prediction_lookup = scored_test[
        ["Id", "PredictedSales"]
    ].rename(
        columns={"PredictedSales": "Sales"}
    )

    submission = (
        sample_submission[["Id"]]
        .merge(
            prediction_lookup,
            on="Id",
            how="left",
            validate="one_to_one",
            sort=False,
        )
    )

    if submission["Sales"].isna().any():
        raise ValueError(
            "Submission contains missing predictions after Id alignment."
        )

    return submission
